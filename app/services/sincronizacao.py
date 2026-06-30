from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Protocol

import httpx
import structlog
from sqlalchemy import text
from sqlmodel import Session, select

from app.db import engine
from app.models import LeaderboardSnapshot, Match, Team
from app.services.ranking import compute_snapshot_ordering
from app.services.seed import TEAM_META

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world"
log = structlog.get_logger()


@dataclass
class MatchUpdate:
    external_id: str
    kickoff_utc: datetime
    venue: Optional[str]
    status: str
    home_score: Optional[int]
    away_score: Optional[int]
    home_team_name: str
    away_team_name: str
    home_team_code: Optional[str] = None
    away_team_code: Optional[str] = None
    live_clock: Optional[str] = None
    live_period: Optional[int] = None
    winner_side: Optional[str] = None


class FixtureSource(Protocol):
    async def fetch_updates(self) -> list[MatchUpdate]: ...


def _status_from_espn(state: str) -> str:
    return {"pre": "SCHEDULED", "in": "LIVE", "post": "FINISHED"}.get(state, "SCHEDULED")


def _live_clock_from_espn(status: dict) -> tuple[Optional[str], Optional[int]]:
    status_type = status.get("type") or {}
    if status_type.get("state") != "in":
        return None, None
    period = status.get("period")
    detail = (status_type.get("shortDetail") or status_type.get("detail") or "").strip()
    description = (status_type.get("description") or "").strip().lower()
    if "halftime" in description or detail.upper() in {"HT", "HALF TIME"}:
        return "INTERVALO", period
    if period == 5 or "penalt" in description:
        return "PENALTIS", period
    if period in (3, 4):
        return detail or "PRORROGACAO", period
    if "'" in detail:
        return detail, period
    clock = status.get("displayClock")
    if clock and ":" in clock:
        return f"{clock.split(':')[0]}'", period
    return detail or None, period


class ESPNSource:
    async def fetch_updates(self, start: str = "20260611", end: str = "20260720") -> list[MatchUpdate]:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(f"{ESPN_BASE}/scoreboard", params={"dates": f"{start}-{end}"})
            response.raise_for_status()
            payload = response.json()

        updates: list[MatchUpdate] = []
        for event in payload.get("events", []):
            try:
                competition = event["competitions"][0]
                competitors = competition["competitors"]
                home = next(item for item in competitors if item.get("homeAway") == "home")
                away = next(item for item in competitors if item.get("homeAway") == "away")
                status_block = event.get("status") or {}
                live_clock, live_period = _live_clock_from_espn(status_block)
                winner_side = None
                if home.get("winner") is True:
                    winner_side = "HOME"
                elif away.get("winner") is True:
                    winner_side = "AWAY"
                updates.append(
                    MatchUpdate(
                        external_id=str(event["id"]),
                        kickoff_utc=datetime.fromisoformat(event["date"].replace("Z", "+00:00")),
                        venue=(competition.get("venue") or {}).get("fullName"),
                        status=_status_from_espn(event["status"]["type"]["state"]),
                        home_score=int(home["score"]) if home.get("score") else None,
                        away_score=int(away["score"]) if away.get("score") else None,
                        home_team_name=home["team"]["displayName"],
                        away_team_name=away["team"]["displayName"],
                        home_team_code=(home.get("team") or {}).get("abbreviation"),
                        away_team_code=(away.get("team") or {}).get("abbreviation"),
                        live_clock=live_clock,
                        live_period=live_period,
                        winner_side=winner_side,
                    )
                )
            except (KeyError, StopIteration, ValueError) as exc:
                log.warning("evento ESPN invalido", error=str(exc), event_id=event.get("id"))
        return updates


ESPN_NAME_OVERRIDES = {
    "USA": "USA",
    "Czechia": "Czech Republic",
    "Türkiye": "Turkey",
    "Korea Republic": "South Korea",
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Cabo Verde": "Cape Verde",
    "Curacao": "Curacao",
    "Congo DR": "DR Congo",
    "DR Congo": "DR Congo",
    "IR Iran": "Iran",
}


def _team_id_by_code(session: Session, code: Optional[str]) -> Optional[int]:
    if not code:
        return None
    team = session.exec(select(Team).where(Team.fifa_code == code.upper())).first()
    return team.id if team else None


def _team_id_by_name(session: Session, espn_name: str) -> Optional[int]:
    canonical = ESPN_NAME_OVERRIDES.get(espn_name, espn_name)
    meta = TEAM_META.get(canonical)
    if not meta:
        log.warning("nome ESPN sem mapeamento", espn_name=espn_name)
        return None
    team = session.exec(select(Team).where(Team.fifa_code == meta[0])).first()
    return team.id if team else None


def _resolve_team_ids(session: Session, update: MatchUpdate) -> tuple[Optional[int], Optional[int]]:
    home_id = _team_id_by_code(session, update.home_team_code) or _team_id_by_name(session, update.home_team_name)
    away_id = _team_id_by_code(session, update.away_team_code) or _team_id_by_name(session, update.away_team_name)
    return home_id, away_id


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _find_match_by_pair_and_kickoff(
    session: Session,
    home_id: int,
    away_id: int,
    kickoff_utc: datetime,
) -> Optional[Match]:
    target = _as_utc(kickoff_utc)
    threshold = timedelta(hours=36)
    candidates = session.exec(
        select(Match).where(
            Match.external_id == None,  # noqa: E711
            Match.home_team_id != None,  # noqa: E711
            Match.away_team_id != None,  # noqa: E711
        )
    ).all()
    scored: list[tuple[timedelta, int, Match]] = []
    for match in candidates:
        same_order = match.home_team_id == home_id and match.away_team_id == away_id
        swapped = match.home_team_id == away_id and match.away_team_id == home_id
        if not (same_order or swapped):
            continue
        delta = abs(_as_utc(match.kickoff_utc) - target)
        if delta <= threshold:
            scored.append((delta, match.match_no or 999, match))
    scored.sort(key=lambda item: (item[0], item[1]))
    return scored[0][2] if scored else None


def _find_ko_match_by_kickoff(session: Session, kickoff_utc: datetime) -> Optional[Match]:
    target = _as_utc(kickoff_utc)
    threshold = timedelta(hours=8)
    candidates = session.exec(
        select(Match).where(Match.stage != "GROUP", Match.external_id == None)  # noqa: E711
    ).all()
    scored = [
        (abs(_as_utc(match.kickoff_utc) - target), match.match_no or 999, match)
        for match in candidates
        if abs(_as_utc(match.kickoff_utc) - target) <= threshold
    ]
    scored.sort(key=lambda item: (item[0], item[1]))
    return scored[0][2] if scored else None


def _match_for_update(session: Session, update: MatchUpdate) -> Optional[Match]:
    match = session.exec(select(Match).where(Match.external_id == update.external_id)).first()
    if match:
        return match
    home_id, away_id = _resolve_team_ids(session, update)
    if home_id and away_id:
        return _find_match_by_pair_and_kickoff(session, home_id, away_id, update.kickoff_utc) or _find_ko_match_by_kickoff(
            session, update.kickoff_utc
        )
    return None


def _result_for(update: MatchUpdate) -> Optional[str]:
    if update.status != "FINISHED" or update.home_score is None or update.away_score is None:
        return None
    if update.winner_side in {"HOME", "AWAY"}:
        return update.winner_side
    if update.home_score > update.away_score:
        return "HOME"
    if update.home_score < update.away_score:
        return "AWAY"
    return "DRAW"


def _ensure_snapshots(session: Session) -> None:
    rows = session.execute(
        text(
            "SELECT m.id, EXISTS ("
            "SELECT 1 FROM leaderboard_snapshots ls WHERE ls.match_id = m.id"
            ") AS has_snapshot "
            "FROM matches m WHERE m.status='FINISHED' "
            "ORDER BY m.kickoff_utc, m.id"
        )
    ).all()
    snapshot_match_ids: set[int] = set()
    for match_id, has_snapshot in rows:
        match_id = int(match_id)
        snapshot_match_ids.add(match_id)
        if has_snapshot:
            continue
        session.add(
            LeaderboardSnapshot(
                match_id=match_id,
                ordering=compute_snapshot_ordering(session, snapshot_match_ids),
            )
        )
    session.commit()


def apply_updates(session: Session, updates: list[MatchUpdate]) -> int:
    updated = 0
    for item in updates:
        match = _match_for_update(session, item)
        if not match:
            log.warning("partida nao vinculavel", external_id=item.external_id)
            continue
        home_id, away_id = _resolve_team_ids(session, item)
        match.external_id = item.external_id
        match.kickoff_utc = item.kickoff_utc
        match.venue = item.venue or match.venue
        if match.stage != "GROUP":
            match.home_team_id = home_id or match.home_team_id
            match.away_team_id = away_id or match.away_team_id
        match.status = item.status
        match.home_score = item.home_score
        match.away_score = item.away_score
        match.live_clock = item.live_clock if item.status == "LIVE" else None
        match.live_period = item.live_period if item.status == "LIVE" else None
        match.result = _result_for(item)
        match.last_synced_at = datetime.now(timezone.utc)
        session.add(match)
        updated += 1
    session.commit()
    _ensure_snapshots(session)
    return updated


async def sync_once() -> int:
    try:
        updates = await ESPNSource().fetch_updates()
    except Exception as exc:
        log.warning("sync ESPN falhou", error=str(exc))
        return 0
    with Session(engine) as session:
        return apply_updates(session, updates)

