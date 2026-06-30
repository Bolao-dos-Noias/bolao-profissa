from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.db import get_session
from app.deps import can_edit_picks, current_user
from app.models import User
from app.security import verify_csrf
from app.services.palpites import (
    KO_STAGE_ORDER,
    KO_STAGE_SIZES,
    build_bet_context,
    save_group_pick,
    save_group_tiebreak,
    save_ko_stage,
    save_thirds_order,
)
from app.templates_env import templates

router = APIRouter()

VALID_GROUP_PICKS = {"HOME", "DRAW", "AWAY"}


@router.get("/aposta")
async def aposta(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not can_edit_picks(user):
        return RedirectResponse("/minha-aposta/resumo", status_code=303)
    return templates.TemplateResponse(request, "bets/aposta.html", build_bet_context(session, user))


@router.post("/aposta/grupo/{match_id:int}")
async def post_group_pick(
    match_id: int,
    pick: str = Form(...),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not can_edit_picks(user):
        raise HTTPException(403, "Prazo encerrado")
    if pick not in VALID_GROUP_PICKS:
        raise HTTPException(400, "Palpite invalido")
    save_group_pick(session, user.id, match_id, pick)
    return RedirectResponse("/aposta", status_code=303)


@router.post("/aposta/grupo/{group}/tiebreak")
async def post_group_tiebreak(
    group: str,
    team_id: int = Form(...),
    direction: str = Form(...),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    if not user:
        raise HTTPException(401, "login necessario")
    if not can_edit_picks(user):
        raise HTTPException(403, "Prazo encerrado")
    if direction not in {"up", "down"}:
        raise HTTPException(400, "direcao invalida")

    context = build_bet_context(session, user)
    rows = list(context["standings"].get(group.upper(), []))
    index = next((position for position, row in enumerate(rows) if row.team_id == team_id), -1)
    if index < 0:
        raise HTTPException(404, "selecao fora do grupo")
    swap_index = index - 1 if direction == "up" else index + 1
    if swap_index < 0 or swap_index >= len(rows):
        raise HTTPException(400, "movimento fora da classificacao")
    if rows[index].points != rows[swap_index].points:
        raise HTTPException(400, "desempate permitido apenas entre selecoes empatadas")

    ordered_ids = [row.team_id for row in rows]
    ordered_ids[index], ordered_ids[swap_index] = ordered_ids[swap_index], ordered_ids[index]
    save_group_tiebreak(session, user.id, group.upper(), ordered_ids)
    return RedirectResponse("/aposta", status_code=303)


@router.post("/aposta/terceiros")
async def post_thirds_order(
    team_ids: list[int] = Form(default=[]),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    if not user:
        raise HTTPException(401, "login necessario")
    if not can_edit_picks(user):
        raise HTTPException(403, "Prazo encerrado")

    context = build_bet_context(session, user)
    candidate_ids = {item["team_id"] for item in context["thirds_candidates"]}
    unique_ids = list(dict.fromkeys(team_ids))
    if len(unique_ids) > 8:
        raise HTTPException(400, "selecione no maximo 8 terceiros")
    if any(team_id not in candidate_ids for team_id in unique_ids):
        raise HTTPException(400, "terceiro fora dos candidatos calculados")
    save_thirds_order(session, user.id, unique_ids)
    return RedirectResponse("/aposta", status_code=303)


@router.post("/aposta/ko/{stage}")
async def post_ko_stage(
    stage: str,
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    if not can_edit_picks(user):
        raise HTTPException(403, "Prazo encerrado")
    form = await request.form()
    if form.get("csrf") != request.session.get("csrf"):
        raise HTTPException(400, "CSRF invalido")
    stage = stage.upper()
    if stage not in KO_STAGE_ORDER:
        raise HTTPException(404, "Fase invalida")
    raw_ids = form.getlist("team_ids")
    try:
        team_ids = [int(raw_id) for raw_id in raw_ids]
    except ValueError as exc:
        raise HTTPException(400, "Time invalido") from exc
    max_size = KO_STAGE_SIZES[stage]
    if len(set(team_ids)) > max_size:
        raise HTTPException(400, f"{stage} permite no maximo {max_size} selecoes")
    save_ko_stage(session, user.id, stage, team_ids)
    return RedirectResponse("/aposta", status_code=303)
