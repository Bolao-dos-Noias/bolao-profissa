from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.db import get_session
from app.deps import current_user
from app.models import User
from app.services.palpites import (
    KO_STAGE_LABELS,
    KO_STAGE_ORDER,
    group_matches,
    player_list,
    teams_by_id,
    user_group_picks,
    user_ko_picks,
)
from app.templates_env import templates

router = APIRouter(prefix="/comparativo")


def _players(session: Session, current: Optional[User]) -> list[User]:
    players = player_list(session)
    if current and current.id not in {player.id for player in players} and not current.is_admin:
        players.append(current)
    return players


@router.get("/geral")
def comparativo_geral(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    players = _players(session, user)
    picks = {player.id: user_group_picks(session, player.id) for player in players}
    return templates.TemplateResponse(
        request,
        "compare/geral.html",
        {
            "user": user,
            "players": players,
            "matches": group_matches(session),
            "teams": teams_by_id(session),
            "picks": picks,
        },
    )


@router.get("/1x1")
def comparativo_1x1(
    request: Request,
    a: Optional[int] = None,
    b: Optional[int] = None,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    players = _players(session, user)
    if not players:
        return templates.TemplateResponse(request, "compare/um_vs_um.html", {"user": user, "players": []})
    first = session.get(User, a) if a else (user if user and not user.is_admin else players[0])
    second = session.get(User, b) if b else next((player for player in players if player.id != first.id), first)
    return templates.TemplateResponse(
        request,
        "compare/um_vs_um.html",
        {
            "user": user,
            "players": players,
            "first": first,
            "second": second,
            "matches": group_matches(session),
            "teams": teams_by_id(session),
            "picks": {
                first.id: user_group_picks(session, first.id),
                second.id: user_group_picks(session, second.id),
            },
        },
    )


@router.get("/mata-mata")
def comparativo_mata_mata(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    players = _players(session, user)
    teams = teams_by_id(session)
    picks = {player.id: user_ko_picks(session, player.id) for player in players}
    return templates.TemplateResponse(
        request,
        "compare/mata_mata.html",
        {
            "user": user,
            "players": players,
            "teams": teams,
            "picks": picks,
            "stages": KO_STAGE_ORDER,
            "stage_labels": KO_STAGE_LABELS,
        },
    )

