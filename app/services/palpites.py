from collections import defaultdict

from sqlmodel import Session, select

from app.domain.classificacao import compute_standings, derive_r32_candidates
from app.models import BetGroup, BetKnockout, BetThirdsOrder, BetTieBreak, Match, Team, User

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


def user_tiebreaks(session: Session, user_id: int) -> dict[str, list[int]]:
    rows = session.exec(select(BetTieBreak).where(BetTieBreak.user_id == user_id)).all()
    out: dict[str, list[int]] = {}
    for row in rows:
        try:
            out[row.group_letter] = [int(item) for item in row.ordered_team_ids.split(",") if item]
        except ValueError:
            continue
    return out


def user_thirds_order(session: Session, user_id: int, candidates: list[dict]) -> list[int]:
    candidate_ids = [item["team_id"] for item in candidates]
    candidate_set = set(candidate_ids)
    saved = session.get(BetThirdsOrder, user_id)
    if saved and saved.ordered_team_ids:
        try:
            selected = [
                int(item)
                for item in saved.ordered_team_ids.split(",")
                if item and int(item) in candidate_set
            ]
            return selected[:8]
        except ValueError:
            pass
    return candidate_ids[:8]


def build_bet_context(session: Session, user: User) -> dict:
    grouped = matches_by_group(session)
    teams = teams_by_id(session)
    group_picks = user_group_picks(session, user.id)
    tiebreaks = user_tiebreaks(session, user.id)
    standings = compute_standings(grouped, group_picks, teams, tiebreaks=tiebreaks)
    _top2, thirds = derive_r32_candidates(standings)
    return {
        "user": user,
        "teams": teams,
        "teams_list": list(teams.values()),
        "matches_by_group": grouped,
        "group_picks": group_picks,
        "standings": standings,
        "tiebreaks": tiebreaks,
        "thirds_candidates": thirds,
        "thirds_order": user_thirds_order(session, user.id, thirds),
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


def save_group_tiebreak(session: Session, user_id: int, group: str, team_ids: list[int]) -> None:
    existing = session.exec(
        select(BetTieBreak).where(BetTieBreak.user_id == user_id, BetTieBreak.group_letter == group)
    ).first()
    ordered = ",".join(str(team_id) for team_id in team_ids)
    if existing:
        existing.ordered_team_ids = ordered
        session.add(existing)
    else:
        session.add(BetTieBreak(user_id=user_id, group_letter=group, ordered_team_ids=ordered))
    session.commit()


def save_thirds_order(session: Session, user_id: int, team_ids: list[int]) -> None:
    ordered = ",".join(str(team_id) for team_id in dict.fromkeys(team_ids))
    existing = session.get(BetThirdsOrder, user_id)
    if existing:
        existing.ordered_team_ids = ordered
        session.add(existing)
    else:
        session.add(BetThirdsOrder(user_id=user_id, ordered_team_ids=ordered))
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
