import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlmodel import Session

from app.db import get_session
from app.deps import current_user, deadline_passed
from app.models import User
from app.services.palpites import build_bet_context
from app.templates_env import templates

router = APIRouter()


def _can_view(current: Optional[User], target: User) -> bool:
    if not current:
        return False
    if current.is_admin or current.id == target.id:
        return True
    return deadline_passed()


def _load_target(session: Session, user_id: int) -> Optional[User]:
    target = session.get(User, user_id)
    if not target or target.is_admin or target.password_hash is None:
        return None
    return target


def _csv_response(session: Session, target: User) -> Response:
    context = build_bet_context(session, target)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["tipo", "fase", "grupo", "jogo", "mandante", "visitante", "palpite"])

    for group, matches in context["matches_by_group"].items():
        for match in matches:
            home = context["teams"].get(match.home_team_id)
            away = context["teams"].get(match.away_team_id)
            writer.writerow(
                [
                    "grupo",
                    "GROUP",
                    group,
                    match.match_no or "",
                    home.name_pt if home else "",
                    away.name_pt if away else "",
                    context["group_picks"].get(match.id, ""),
                ]
            )

    for stage in context["ko_stage_order"]:
        picked_names = [
            context["teams"][team_id].name_pt
            for team_id in sorted(context["ko_picks"].get(stage, []))
            if team_id in context["teams"]
        ]
        writer.writerow(["mata-mata", stage, "", "", "", "", "; ".join(picked_names)])

    filename = f"palpite-{target.nickname}.csv".replace("/", "-")
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(buffer.getvalue(), media_type="text/csv; charset=utf-8", headers=headers)


def _render_palpite(
    request: Request,
    current: Optional[User],
    target: User,
    mode: str,
    session: Session,
):
    ctx = build_bet_context(session, target)
    ctx["user"] = current
    ctx["target"] = target
    ctx["mode"] = mode
    return templates.TemplateResponse(request, "viewer/palpite.html", ctx)


@router.get("/minha-aposta/resumo")
async def minha_aposta_resumo(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return _render_palpite(request, user, user, "resumo", session)


@router.get("/minha-aposta/completa")
async def minha_aposta_completa(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return _render_palpite(request, user, user, "completa", session)


@router.get("/minha-aposta/completa.csv")
async def minha_aposta_csv(
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return _csv_response(session, user)


@router.get("/palpites/{user_id:int}")
async def palpite_publico(
    user_id: int,
    request: Request,
    current: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    target = _load_target(session, user_id)
    if not target:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    if not _can_view(current, target):
        return templates.TemplateResponse(request, "viewer/locked.html", {"user": current, "target": target}, status_code=403)
    return _render_palpite(request, current, target, "completa", session)


@router.get("/palpite/{user_id:int}/resumo")
async def palpite_resumo_compat(
    user_id: int,
    request: Request,
    current: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    target = _load_target(session, user_id)
    if not target:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    if not _can_view(current, target):
        return templates.TemplateResponse(request, "viewer/locked.html", {"user": current, "target": target}, status_code=403)
    return _render_palpite(request, current, target, "resumo", session)


@router.get("/palpite/{user_id:int}/completa")
async def palpite_completa_compat(
    user_id: int,
    request: Request,
    current: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    target = _load_target(session, user_id)
    if not target:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    if not _can_view(current, target):
        return templates.TemplateResponse(request, "viewer/locked.html", {"user": current, "target": target}, status_code=403)
    return _render_palpite(request, current, target, "completa", session)


@router.get("/palpite/{user_id:int}/completa.csv")
async def palpite_csv_compat(
    user_id: int,
    current: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    target = _load_target(session, user_id)
    if not target:
        return RedirectResponse("/leaderboard", status_code=303)
    if not _can_view(current, target):
        return RedirectResponse(f"/palpite/{user_id}/completa", status_code=303)
    return _csv_response(session, target)
