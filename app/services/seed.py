import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlmodel import Session, SQLModel, select

from app.config import settings
from app.db import engine, init_db
from app.models import Match, Setting, Team

SEED_PATH = Path(__file__).resolve().parents[2] / "data" / "seed" / "worldcup-2026.json"

STAGE_MAP = {
    "Round of 32": "R32",
    "Round of 16": "R16",
    "Quarter-final": "QF",
    "Semi-final": "SF",
    "Match for third place": "THIRD",
    "Final": "F",
}

TEAM_META: dict[str, tuple[str, str, str]] = {
    "Mexico": ("MEX", "mx", "Mexico"),
    "South Africa": ("RSA", "za", "Africa do Sul"),
    "South Korea": ("KOR", "kr", "Coreia do Sul"),
    "Czech Republic": ("CZE", "cz", "Tchequia"),
    "Canada": ("CAN", "ca", "Canada"),
    "Switzerland": ("SUI", "ch", "Suica"),
    "Bosnia & Herzegovina": ("BIH", "ba", "Bosnia e Herzegovina"),
    "Qatar": ("QAT", "qa", "Catar"),
    "Brazil": ("BRA", "br", "Brasil"),
    "Morocco": ("MAR", "ma", "Marrocos"),
    "Scotland": ("SCO", "gb-sct", "Escocia"),
    "Haiti": ("HAI", "ht", "Haiti"),
    "USA": ("USA", "us", "Estados Unidos"),
    "Turkey": ("TUR", "tr", "Turquia"),
    "Paraguay": ("PAR", "py", "Paraguai"),
    "Australia": ("AUS", "au", "Australia"),
    "Germany": ("GER", "de", "Alemanha"),
    "Ecuador": ("ECU", "ec", "Equador"),
    "Ivory Coast": ("CIV", "ci", "Costa do Marfim"),
    "Curacao": ("CUW", "cw", "Curacao"),
    "Curaçao": ("CUW", "cw", "Curacao"),
    "Netherlands": ("NED", "nl", "Holanda"),
    "Japan": ("JPN", "jp", "Japao"),
    "Sweden": ("SWE", "se", "Suecia"),
    "Tunisia": ("TUN", "tn", "Tunisia"),
    "Belgium": ("BEL", "be", "Belgica"),
    "Iran": ("IRN", "ir", "Ira"),
    "Egypt": ("EGY", "eg", "Egito"),
    "New Zealand": ("NZL", "nz", "Nova Zelandia"),
    "Spain": ("ESP", "es", "Espanha"),
    "Uruguay": ("URU", "uy", "Uruguai"),
    "Saudi Arabia": ("KSA", "sa", "Arabia Saudita"),
    "Cape Verde": ("CPV", "cv", "Cabo Verde"),
    "France": ("FRA", "fr", "Franca"),
    "Senegal": ("SEN", "sn", "Senegal"),
    "Norway": ("NOR", "no", "Noruega"),
    "Iraq": ("IRQ", "iq", "Iraque"),
    "Argentina": ("ARG", "ar", "Argentina"),
    "Austria": ("AUT", "at", "Austria"),
    "Algeria": ("ALG", "dz", "Argelia"),
    "Jordan": ("JOR", "jo", "Jordania"),
    "Portugal": ("POR", "pt", "Portugal"),
    "Colombia": ("COL", "co", "Colombia"),
    "Uzbekistan": ("UZB", "uz", "Uzbequistao"),
    "DR Congo": ("COD", "cd", "R.D. Congo"),
    "England": ("ENG", "gb-eng", "Inglaterra"),
    "Croatia": ("CRO", "hr", "Croacia"),
    "Ghana": ("GHA", "gh", "Gana"),
    "Panama": ("PAN", "pa", "Panama"),
}

TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s+UTC([+-]?\d+)$")


def parse_kickoff(date_str: str, time_str: str) -> datetime:
    match = TIME_RE.match(time_str.strip())
    if not match:
        raise ValueError(f"time invalido: {time_str!r}")
    hour, minute, offset = int(match.group(1)), int(match.group(2)), int(match.group(3))
    local = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=hour, minute=minute)
    return (local - timedelta(hours=offset)).replace(tzinfo=timezone.utc)


def load_payload() -> dict:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def seed(force: bool = False) -> dict:
    if force:
        SQLModel.metadata.drop_all(engine)
    init_db()
    payload = load_payload()

    with Session(engine) as session:
        if session.exec(select(Team)).first() and not force:
            return {"created": False, "reason": "dados ja existem"}

        team_by_name: dict[str, Team] = {}
        teams_seen: set[str] = set()
        for item in payload["matches"]:
            if not item.get("group"):
                continue
            group = item["group"].replace("Group ", "")
            for key in ("team1", "team2"):
                name = item[key]
                if name in teams_seen:
                    continue
                teams_seen.add(name)
                meta = TEAM_META.get(name)
                if not meta:
                    continue
                session.add(Team(name_pt=meta[2], fifa_code=meta[0], iso2=meta[1], group_letter=group))
        session.commit()

        for team in session.exec(select(Team)).all():
            original = next((name for name, meta in TEAM_META.items() if meta[0] == team.fifa_code), None)
            if original:
                team_by_name[original] = team

        group_counter: dict[str, int] = {}
        ko_count = 0
        group_count = 0
        for item in payload["matches"]:
            kickoff = parse_kickoff(item["date"], item["time"])
            venue = item.get("ground")
            if item.get("group"):
                group = item["group"].replace("Group ", "")
                home = team_by_name.get(item["team1"])
                away = team_by_name.get(item["team2"])
                if not home or not away:
                    continue
                group_counter[group] = group_counter.get(group, 0) + 1
                session.add(
                    Match(
                        stage="GROUP",
                        group_letter=group,
                        match_no=group_counter[group],
                        home_team_id=home.id,
                        away_team_id=away.id,
                        kickoff_utc=kickoff,
                        venue=venue,
                    )
                )
                group_count += 1
            else:
                stage = STAGE_MAP.get(item["round"])
                if not stage:
                    continue
                number = item.get("num")
                if number is None:
                    number = 104 if stage == "F" else 103
                session.add(
                    Match(
                        stage=stage,
                        match_no=number,
                        slot_home=item.get("team1"),
                        slot_away=item.get("team2"),
                        kickoff_utc=kickoff,
                        venue=venue,
                    )
                )
                ko_count += 1

        session.merge(Setting(key="deadline", value=settings.bolao_deadline_utc.isoformat()))
        session.merge(Setting(key="current_season", value="2026"))
        session.commit()
    return {"created": True, "teams": len(team_by_name), "group_matches": group_count, "ko_matches": ko_count}

