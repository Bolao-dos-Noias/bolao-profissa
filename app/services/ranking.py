from collections import Counter, defaultdict
from datetime import datetime, timezone
import re
from typing import Optional

from sqlmodel import Session, select

from app.domain.pontuacao import (
    ORDEM_MATA_MATA,
    PESOS_MATA_MATA,
    ScoreRow,
    ordenar_ranking,
    parse_snapshot,
    serialize_snapshot_ordering,
)
from app.models import BetGroup, BetKnockout, LeaderboardSnapshot, Match, User

TOP2_SLOT_RE = re.compile(r"^[12]([A-Z])$")
THIRD_SLOT_RE = re.compile(r"^3[A-Z/]+$")


def _as_utc_naive(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)


def stage_qualifiers(
    session: Session,
    cutoff_utc: Optional[datetime] = None,
    match_ids: Optional[set[int]] = None,
) -> dict[str, set[int]]:
    qualifiers: dict[str, set[int]] = {stage: set() for stage in ORDEM_MATA_MATA}

    def match_in_scope(match: Match) -> bool:
        if match.status != "FINISHED":
            return False
        if match_ids is not None and (match.id is None or match.id not in match_ids):
            return False
        if cutoff_utc is not None and _as_utc_naive(match.kickoff_utc) > _as_utc_naive(cutoff_utc):
            return False
        return True

    def completed_groups() -> set[str]:
        grouped: dict[str, list[Match]] = defaultdict(list)
        group_matches = session.exec(select(Match).where(Match.stage == "GROUP")).all()
        for match in group_matches:
            if match.group_letter:
                grouped[match.group_letter].append(match)
        return {
            group
            for group, matches in grouped.items()
            if matches and all(match_in_scope(match) for match in matches)
        }

    def group_phase_resolved() -> bool:
        group_matches = session.exec(select(Match).where(Match.stage == "GROUP")).all()
        return bool(group_matches) and all(match_in_scope(match) for match in group_matches)

    def r32_matches_with_teams() -> list[Match]:
        return session.exec(
            select(Match).where(
                Match.stage == "R32",
                Match.home_team_id != None,  # noqa: E711
                Match.away_team_id != None,  # noqa: E711
            )
        ).all()

    def add_current_r32() -> None:
        for match in r32_matches_with_teams():
            if match.home_team_id:
                qualifiers["R32"].add(match.home_team_id)
            if match.away_team_id:
                qualifiers["R32"].add(match.away_team_id)

    def add_historical_r32() -> None:
        completed = completed_groups()
        all_groups_resolved = group_phase_resolved()
        any_slot = False

        for match in r32_matches_with_teams():
            for slot, team_id in ((match.slot_home, match.home_team_id), (match.slot_away, match.away_team_id)):
                if not team_id:
                    continue
                if not slot:
                    if all_groups_resolved:
                        qualifiers["R32"].add(team_id)
                    continue
                normalized = slot.strip().upper()
                any_slot = True
                top2 = TOP2_SLOT_RE.match(normalized)
                if top2:
                    if top2.group(1) in completed:
                        qualifiers["R32"].add(team_id)
                    continue
                if THIRD_SLOT_RE.match(normalized) and all_groups_resolved:
                    qualifiers["R32"].add(team_id)
                    continue
                if all_groups_resolved:
                    qualifiers["R32"].add(team_id)

        if all_groups_resolved and not any_slot:
            add_current_r32()

    def finished_matches(stage: str) -> list[Match]:
        statement = select(Match).where(Match.stage == stage, Match.status == "FINISHED")
        if match_ids is not None:
            statement = statement.where(Match.id.in_(match_ids))
        if cutoff_utc is not None:
            statement = statement.where(Match.kickoff_utc <= cutoff_utc)
        return session.exec(statement).all()

    if cutoff_utc is not None or match_ids is not None:
        add_historical_r32()
    else:
        add_current_r32()

    for next_stage, played_stage in [("R16", "R32"), ("QF", "R16"), ("SF", "QF"), ("F", "SF")]:
        for match in finished_matches(played_stage):
            if match.result == "HOME" and match.home_team_id:
                qualifiers[next_stage].add(match.home_team_id)
            elif match.result == "AWAY" and match.away_team_id:
                qualifiers[next_stage].add(match.away_team_id)

    final = next(iter(finished_matches("F")), None)
    if final and final.result:
        winner_id = final.home_team_id if final.result == "HOME" else final.away_team_id
        if winner_id:
            qualifiers["CHAMPION"].add(winner_id)

    return qualifiers


def _base_rows(session: Session) -> tuple[dict[int, ScoreRow], Optional[int]]:
    users = session.exec(select(User).where(User.is_admin == False)).all()  # noqa: E712
    rows = {
        user.id: ScoreRow(
            user_id=user.id,
            nickname=user.nickname,
            nome_completo=user.nome_completo or "",
        )
        for user in users
        if user.id is not None
    }
    claude_id = next(
        (user_id for user_id, row in rows.items() if row.nickname.lower() == "claude"),
        None,
    )
    return rows, claude_id


def _scored_group_matches(
    session: Session,
    cutoff_utc: Optional[datetime],
    snapshot_match_ids: Optional[set[int]],
) -> list[Match]:
    if snapshot_match_ids is not None:
        return session.exec(
            select(Match).where(
                Match.stage == "GROUP",
                Match.status == "FINISHED",
                Match.id.in_(snapshot_match_ids),
            )
        ).all()
    if cutoff_utc is not None:
        return session.exec(
            select(Match).where(
                Match.stage == "GROUP",
                Match.status == "FINISHED",
                Match.kickoff_utc <= cutoff_utc,
            )
        ).all()
    return session.exec(
        select(Match).where(
            Match.stage == "GROUP",
            Match.status.in_(["FINISHED", "LIVE"]),
        )
    ).all()


def _effective_result(match: Match) -> Optional[str]:
    if match.status == "FINISHED":
        return match.result
    if match.home_score is None or match.away_score is None:
        return None
    if match.home_score > match.away_score:
        return "HOME"
    if match.home_score < match.away_score:
        return "AWAY"
    return "DRAW"


def _apply_group_points(
    session: Session,
    rows: dict[int, ScoreRow],
    claude_id: Optional[int],
    group_matches: list[Match],
) -> None:
    hit_users_per_match: dict[int, list[int]] = defaultdict(list)
    for match in group_matches:
        if match.id is None:
            continue
        result = _effective_result(match)
        if not result:
            continue
        bets = session.exec(select(BetGroup).where(BetGroup.match_id == match.id)).all()
        for bet in bets:
            if bet.user_id not in rows:
                continue
            if bet.pick == result:
                rows[bet.user_id].group_pts += 3
                hit_users_per_match[match.id].append(bet.user_id)

    for hitters in hit_users_per_match.values():
        real_hitters = [user_id for user_id in hitters if user_id != claude_id]
        if len(real_hitters) == 1:
            rows[real_hitters[0]].zebra_pts += 3
        if claude_id is not None and claude_id in hitters and len(real_hitters) <= 1:
            rows[claude_id].zebra_pts += 3


def _apply_zebra_cap(session: Session, rows: dict[int, ScoreRow], claude_id: Optional[int]) -> None:
    pickers_by_pair: dict[tuple[int, str], list[int]] = defaultdict(list)
    all_group_bets = session.exec(select(BetGroup)).all()
    for bet in all_group_bets:
        pickers_by_pair[(bet.match_id, bet.pick)].append(bet.user_id)

    for bet in all_group_bets:
        if bet.user_id not in rows:
            continue
        same_pick = pickers_by_pair[(bet.match_id, bet.pick)]
        real = [user_id for user_id in same_pick if user_id != claude_id]
        if bet.user_id != claude_id:
            if real == [bet.user_id]:
                rows[bet.user_id].zebra_max += 3
        elif len(real) <= 1:
            rows[bet.user_id].zebra_max += 3


def _apply_knockout_points(
    session: Session,
    rows: dict[int, ScoreRow],
    qualifiers: dict[str, set[int]],
) -> None:
    for stage, weight in PESOS_MATA_MATA.items():
        bets = session.exec(select(BetKnockout).where(BetKnockout.stage == stage)).all()
        per_user: dict[int, int] = Counter()
        for bet in bets:
            if bet.user_id in rows and bet.team_id in qualifiers[stage]:
                per_user[bet.user_id] += 1
        for user_id, hits in per_user.items():
            row = rows[user_id]
            row.ko_pts += hits * weight
            row.by_stage[stage] = hits
            if stage == "CHAMPION":
                row.hit_champion = hits > 0
            elif stage == "F":
                row.hit_f = hits
            elif stage == "SF":
                row.hit_sf = hits
            elif stage == "QF":
                row.hit_qf = hits
            elif stage == "R16":
                row.hit_r16 = hits
            elif stage == "R32":
                row.hit_r32 = hits


def compute_scores(
    session: Session,
    cutoff_utc: Optional[datetime] = None,
    snapshot_match_ids: Optional[set[int]] = None,
) -> list[ScoreRow]:
    rows, claude_id = _base_rows(session)
    group_matches = _scored_group_matches(session, cutoff_utc, snapshot_match_ids)
    _apply_group_points(session, rows, claude_id, group_matches)
    _apply_zebra_cap(session, rows, claude_id)
    qualifiers = stage_qualifiers(session, cutoff_utc=cutoff_utc, match_ids=snapshot_match_ids)
    _apply_knockout_points(session, rows, qualifiers)
    ordered = ordenar_ranking(list(rows.values()))

    if cutoff_utc is None and snapshot_match_ids is None:
        any_live = session.exec(select(Match).where(Match.status == "LIVE")).first() is not None
        snapshots = ordered_leaderboard_snapshots(session, descending=True, limit=2)
        snapshot = snapshots[0] if any_live and snapshots else None
        if not any_live and len(snapshots) >= 2:
            snapshot = snapshots[1]
        if snapshot and snapshot.ordering:
            previous_ranks, _previous_totals = parse_snapshot(snapshot.ordering)
            for row in ordered:
                previous_rank = previous_ranks.get(row.user_id)
                if previous_rank is not None:
                    row.prev_rank = previous_rank
                    row.delta_rank = previous_rank - row.rank

    return ordered


def ordered_leaderboard_snapshots(
    session: Session,
    *,
    descending: bool = False,
    limit: Optional[int] = None,
) -> list[LeaderboardSnapshot]:
    snapshots = session.exec(select(LeaderboardSnapshot)).all()
    match_ids = [snapshot.match_id for snapshot in snapshots if snapshot.match_id]
    matches: dict[int, Match] = {}
    if match_ids:
        rows = session.exec(select(Match).where(Match.id.in_(match_ids))).all()
        matches = {match.id: match for match in rows if match.id is not None}

    def sort_key(snapshot: LeaderboardSnapshot) -> tuple:
        match = matches.get(snapshot.match_id) if snapshot.match_id else None
        if match:
            return (match.kickoff_utc, match.id or 0, snapshot.id or 0)
        return (snapshot.captured_at, 0, snapshot.id or 0)

    ordered = sorted(snapshots, key=sort_key, reverse=descending)
    return ordered[:limit] if limit is not None else ordered


def compute_snapshot_ordering(session: Session, match_ids: set[int]) -> str:
    rows = compute_scores(session, snapshot_match_ids=set(match_ids))
    return serialize_snapshot_ordering(rows)


def current_maxima(session: Session) -> dict[str, int]:
    group_open = len(
        session.exec(
            select(Match).where(Match.stage == "GROUP", Match.status.in_(["FINISHED", "LIVE"]))
        ).all()
    )
    qualifiers = stage_qualifiers(session)
    values = {
        "p": group_open * 3,
        "r32": len(qualifiers["R32"]) * 3,
        "r16": len(qualifiers["R16"]) * 5,
        "qf": len(qualifiers["QF"]) * 7,
        "sf": len(qualifiers["SF"]) * 10,
        "f": len(qualifiers["F"]) * 14,
        "champ": len(qualifiers["CHAMPION"]) * 20,
    }
    values["total"] = sum(values.values())
    return values

