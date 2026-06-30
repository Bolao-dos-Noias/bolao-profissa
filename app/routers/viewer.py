from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
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


def _render_palpite(
    request: Request,
    target: User,
    mode: str,
    session: Session,
):
    ctx = build_bet_context(session, target)
    ctx["target"] = target
    ctx["mode"] = mode
    return templates.TemplateResponse(request, "viewer/palpite.html", ctx)


@router.get("/minha-aposta/resumo")
def minha_aposta_resumo(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return _render_palpite(request, user, "resumo", session)


@router.get("/minha-aposta/completa")
def minha_aposta_completa(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return _render_palpite(request, user, "completa", session)


@router.get("/palpites/{user_id:int}")
def palpite_publico(
    user_id: int,
    request: Request,
    current: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    target = session.get(User, user_id)
    if not target:
        return templates.TemplateResponse(request, "404.html", {}, status_code=404)
    if not _can_view(current, target):
        return templates.TemplateResponse(request, "viewer/locked.html", {"user": current, "target": target}, status_code=403)
    return _render_palpite(request, target, "completa", session)

