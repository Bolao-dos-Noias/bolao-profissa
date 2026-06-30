import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.config import settings
from app.db import get_session
from app.deps import current_user
from app.models import User
from app.security import verify_csrf
from app.services.seed import seed
from app.services.sincronizacao import sync_once
from app.templates_env import templates

router = APIRouter(prefix="/admin")


def _check_token(token: str | None, bearer: str | None = None) -> None:
    allowed = {settings.admin_token} - {""}
    if bearer and bearer.startswith("Bearer "):
        token = bearer[7:]
    if not allowed or token not in allowed:
        raise HTTPException(status_code=401, detail="admin token invalido")


async def require_admin(user: User | None = Depends(current_user)) -> User:
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="admin necessario")
    return user


@router.api_route("/seed", methods=["GET", "POST"])
async def admin_seed(x_admin_token: str | None = Header(default=None)):
    _check_token(x_admin_token)
    return {"ok": True, "action": "seed", **seed(force=False)}


@router.api_route("/sync", methods=["GET", "POST"])
async def admin_sync(
    x_admin_token: str | None = Header(default=None),
    authorization: str | None = Header(default=None),
):
    _check_token(x_admin_token, authorization)
    updated = await sync_once()
    return {"ok": True, "action": "sync", "matches_updated": updated}


@router.get("/users")
async def users_page(
    request: Request,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    users = session.exec(select(User).order_by(User.nickname)).all()
    return templates.TemplateResponse(
        request,
        "admin/users.html",
        {"user": admin, "users": users, "errors": [], "flash": request.query_params.get("flash")},
    )


@router.post("/users/new")
async def users_create(
    request: Request,
    nickname: str = Form(...),
    nome_completo: str = Form(""),
    admin: User = Depends(require_admin),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    nick = nickname.strip()
    errors: list[str] = []
    if len(nick) < 2 or len(nick) > 30:
        errors.append("Nickname precisa ter de 2 a 30 caracteres.")
    if session.exec(select(User).where(User.nickname == nick)).first():
        errors.append("Nickname ja existe.")
    if errors:
        users = session.exec(select(User).order_by(User.nickname)).all()
        return templates.TemplateResponse(
            request,
            "admin/users.html",
            {"user": admin, "users": users, "errors": errors, "flash": None},
            status_code=400,
        )
    code = secrets.token_urlsafe(8)
    session.add(
        User(
            nickname=nick,
            username=nick,
            email=f"{nick}@bolao.local",
            nome_completo=nome_completo.strip() or None,
            invite_code=code,
            password_hash="",
        )
    )
    session.commit()
    return RedirectResponse("/admin/users?flash=usuario-criado", status_code=303)


@router.post("/users/{user_id:int}/unlock")
async def users_unlock(
    user_id: int,
    minutes: int = Form(30),
    admin: User = Depends(require_admin),  # noqa: ARG001
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    user = session.get(User, user_id)
    if not user or user.is_admin:
        raise HTTPException(404, "usuario nao encontrado")
    user.edit_unlock_until = datetime.now(timezone.utc) + timedelta(minutes=max(1, minutes))
    session.add(user)
    session.commit()
    return RedirectResponse("/admin/users?flash=edicao-liberada", status_code=303)
