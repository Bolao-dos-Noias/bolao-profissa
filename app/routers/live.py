from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from app.db import get_session
from app.deps import current_user, deadline_passed
from app.models import BetGroup, Match, Team, User
from app.services.ranking import stage_qualifiers
from app.templates_env import templates

router = APIRouter()


def _teams(session: Session) -> dict[int, Team]:
    return {team.id: team for team in session.exec(select(Team)).all() if team.id is not None}


def _official_group_summary(session: Session, teams: dict[int, Team]) -> list[dict]:
    stats = {
        team.id: {"played": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0, "gd": 0, "points": 0}
        for team in teams.values()
    }
    matches = session.exec(select(Match).where(Match.stage == "GROUP")).all()
    for match in matches:
        if (
            match.status != "FINISHED"
            or match.home_team_id is None
            or match.away_team_id is None
            or match.home_score is None
            or match.away_score is None
        ):
            continue
        home = stats[match.home_team_id]
        away = stats[match.away_team_id]
        home["played"] += 1
        away["played"] += 1
        home["gf"] += match.home_score
        home["ga"] += match.away_score
        away["gf"] += match.away_score
        away["ga"] += match.home_score
        if match.home_score > match.away_score:
            home["wins"] += 1
            home["points"] += 3
            away["losses"] += 1
        elif match.home_score < match.away_score:
            away["wins"] += 1
            away["points"] += 3
            home["losses"] += 1
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1
        home["gd"] = home["gf"] - home["ga"]
        away["gd"] = away["gf"] - away["ga"]

    groups = sorted({team.group_letter for team in teams.values()})
    summary = []
    for group in groups:
        group_teams = [team for team in teams.values() if team.group_letter == group]
        ranked = sorted(
            group_teams,
            key=lambda team: (
                -stats[team.id]["points"],
                -stats[team.id]["gd"],
                -stats[team.id]["gf"],
                team.name_pt,
            ),
        )
        summary.append(
            {
                "letter": group,
                "rows": [
                    {"rank": index, "team": team, "stats": stats[team.id]}
                    for index, team in enumerate(ranked, 1)
                ],
            }
        )
    return summary


@router.get("/ao-vivo")
async def ao_vivo(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    teams = _teams(session)
    matches = session.exec(
        select(Match).where(Match.stage != "THIRD").order_by(Match.kickoff_utc, Match.id)
    ).all()
    grouped: dict[str, list[Match]] = defaultdict(list)
    for match in matches:
        grouped[match.status].append(match)
    return templates.TemplateResponse(
        request,
        "live/live.html",
        {"user": user, "teams": teams, "grouped": grouped, "title": "Ao vivo"},
    )


@router.get("/ao-vivo/consolidado")
async def consolidado(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    teams = _teams(session)
    qualifiers = stage_qualifiers(session)
    ko_matches = session.exec(
        select(Match).where(Match.stage != "GROUP", Match.stage != "THIRD").order_by(Match.match_no, Match.id)
    ).all()
    return templates.TemplateResponse(
        request,
        "live/consolidado.html",
        {
            "user": user,
            "teams": teams,
            "groups": _official_group_summary(session, teams),
            "qualifiers": qualifiers,
            "ko_matches": ko_matches,
        },
    )


@router.get("/ao-vivo/consolidado/completo")
async def consolidado_completo(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    teams = _teams(session)
    matches = session.exec(
        select(Match).where(Match.stage != "THIRD").order_by(Match.kickoff_utc, Match.id)
    ).all()
    return templates.TemplateResponse(
        request,
        "live/resultados.html",
        {"user": user, "teams": teams, "matches": matches},
    )


@router.get("/ao-vivo/jogo/{match_id:int}/palpites")
async def palpites_do_jogo(
    match_id: int,
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    match = session.get(Match, match_id)
    if not match:
        return templates.TemplateResponse(request, "404.html", {"user": user}, status_code=404)

    teams = _teams(session)
    bets = session.exec(select(BetGroup).where(BetGroup.match_id == match_id)).all()
    picks = {bet.user_id: bet.pick for bet in bets}
    if deadline_passed():
        players = session.exec(
            select(User)
            .where(User.is_admin == False, User.password_hash != None)  # noqa: E711,E712
            .order_by(User.nickname)
        ).all()
    else:
        players = [user] if user else []
    rows = [{"player": player, "pick": picks.get(player.id)} for player in players]
    return templates.TemplateResponse(
        request,
        "live/palpites_jogo.html",
        {"user": user, "match": match, "teams": teams, "rows": rows},
    )
