from collections import defaultdict

from sqlmodel import Session, select

from app.domain.classificacao import compute_standings, derive_r32_candidates
from app.models import BetGroup, BetKnockout, Match, Team, User

KO_STAGE_LABELS = {
    "R32": "16-avos",
    "R16": "Oitavas",
    "QF": "Quartas",
    "SF": "Semifinais",
    "F": "Final",
    "CHAMPION": "Campeao",
}
KO_STAGE_SIZES = {"R32": 32, "R16": 16, "QF": 8, "SF": 4, "F": 2, "CHAMPION": 1}
KO_STAGE_ORDER = ["R32", "R16", "QF", "SF", "F", "CHAMPION"]


def all_teams(session: Session) -> list[Team]:
    return session.exec(select(Team).order_by(Team.group_letter, Team.name_pt)).all()


def teams_by_id(session: Session) -> dict[int, Team]:
    return {team.id: team for team in all_teams(session) if team.id is not None}


def group_matches(session: Session) -> list[Match]:
    return session.exec(
        select(Match).where(Match.stage == "GROUP").order_by(Match.group_letter, Match.match_no, Match.id)
    ).all()


def matches_by_group(session: Session) -> dict[str, list[Match]]:
    grouped: dict[str, list[Match]] = defaultdict(list)
    for match in group_matches(session):
        grouped[match.group_letter or "?"].append(match)
    return dict(sorted(grouped.items()))


def user_group_picks(session: Session, user_id: int) -> dict[int, str]:
    rows = session.exec(select(BetGroup).where(BetGroup.user_id == user_id)).all()
    return {row.match_id: row.pick for row in rows}


def user_ko_picks(session: Session, user_id: int) -> dict[str, set[int]]:
    rows = session.exec(select(BetKnockout).where(BetKnockout.user_id == user_id)).all()
    out: dict[str, set[int]] = defaultdict(set)
    for row in rows:
        out[row.stage].add(row.team_id)
    return dict(out)


def build_bet_context(session: Session, user: User) -> dict:
    grouped = matches_by_group(session)
    teams = teams_by_id(session)
    group_picks = user_group_picks(session, user.id)
    standings = compute_standings(grouped, group_picks, teams)
    _top2, thirds = derive_r32_candidates(standings)
    return {
        "user": user,
        "teams": teams,
        "teams_list": list(teams.values()),
        "matches_by_group": grouped,
        "group_picks": group_picks,
        "standings": standings,
        "thirds_candidates": thirds,
        "ko_picks": user_ko_picks(session, user.id),
        "ko_stage_labels": KO_STAGE_LABELS,
        "ko_stage_sizes": KO_STAGE_SIZES,
        "ko_stage_order": KO_STAGE_ORDER,
    }


def save_group_pick(session: Session, user_id: int, match_id: int, pick: str) -> None:
    existing = session.exec(
        select(BetGroup).where(BetGroup.user_id == user_id, BetGroup.match_id == match_id)
    ).first()
    if existing:
        existing.pick = pick
        session.add(existing)
    else:
        session.add(BetGroup(user_id=user_id, match_id=match_id, pick=pick))
    session.commit()


def save_ko_stage(session: Session, user_id: int, stage: str, team_ids: list[int]) -> None:
    existing = session.exec(
        select(BetKnockout).where(BetKnockout.user_id == user_id, BetKnockout.stage == stage)
    ).all()
    for row in existing:
        session.delete(row)
    for team_id in dict.fromkeys(team_ids):
        session.add(BetKnockout(user_id=user_id, stage=stage, team_id=team_id))
    session.commit()


def player_list(session: Session) -> list[User]:
    return session.exec(
        select(User)
        .where(User.is_admin == False)  # noqa: E712
        .order_by(User.nickname)
    ).all()

