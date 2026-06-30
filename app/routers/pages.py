from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, func, select

from app.config import settings
from app.db import get_session
from app.deps import current_user, deadline_passed
from app.models import Match, Team, User
from app.templates_env import templates

router = APIRouter()


def _copa_stats(session: Session) -> dict:
    matches = session.exec(select(Match).where(Match.stage != "THIRD")).all()
    finished = [match for match in matches if match.status == "FINISHED"]
    live = [match for match in matches if match.status == "LIVE"]
    goals = sum(
        (match.home_score or 0) + (match.away_score or 0)
        for match in finished
        if match.home_score is not None and match.away_score is not None
    )
    next_matches = sorted(
        [match for match in matches if match.status != "FINISHED"],
        key=lambda match: match.kickoff_utc,
    )
    return {
        "total": len(matches),
        "finished": len(finished),
        "live": len(live),
        "scheduled": len(matches) - len(finished) - len(live),
        "goals": goals,
        "next_match": next_matches[0] if next_matches else None,
    }


@router.get("/")
def home(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    participantes = session.exec(
        select(func.count(User.id)).where(User.is_admin == False, User.password_hash != None)  # noqa: E711, E712
    ).one()
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "user": user,
            "deadline": settings.bolao_deadline_utc,
            "deadline_passed": deadline_passed(),
            "participantes": participantes,
            "stats": _copa_stats(session),
        },
    )


@router.get("/copa")
def copa(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    return templates.TemplateResponse(request, "copa.html", {"user": user, "stats": _copa_stats(session)})


@router.get("/palpites")
def palpites(request: Request, user: Optional[User] = Depends(current_user)):
    return templates.TemplateResponse(request, "palpites.html", {"user": user})


@router.get("/copa/consulta")
def copa_consulta(
    request: Request,
    team: str = "",
    stage: str = "",
    status: str = "",
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    teams = {team_row.id: team_row for team_row in session.exec(select(Team)).all()}
    matches = session.exec(
        select(Match).where(Match.stage != "THIRD").order_by(Match.kickoff_utc, Match.id)
    ).all()
    team_query = team.strip().lower()
    stage_query = stage.strip().upper()
    status_query = status.strip().upper()
    rows = []
    for match in matches:
        home = teams.get(match.home_team_id)
        away = teams.get(match.away_team_id)
        if stage_query and match.stage != stage_query:
            continue
        if status_query and match.status != status_query:
            continue
        if team_query:
            haystack = " ".join(
                [
                    home.name_pt if home else "",
                    away.name_pt if away else "",
                    home.fifa_code if home else "",
                    away.fifa_code if away else "",
                ]
            ).lower()
            if team_query not in haystack:
                continue
        rows.append({"match": match, "home": home, "away": away})
    return templates.TemplateResponse(
        request,
        "copa_consulta.html",
        {
            "user": user,
            "rows": rows,
            "team_query": team,
            "stage_query": stage_query,
            "status_query": status_query,
            "stages": ["GROUP", "R32", "R16", "QF", "SF", "F"],
            "statuses": ["SCHEDULED", "LIVE", "FINISHED"],
        },
    )


@router.get("/regulamento")
def regulamento(request: Request, user: Optional[User] = Depends(current_user)):
    return templates.TemplateResponse(request, "regulamento.html", {"user": user})

