from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.auth import hash_password, validate_password, verify_password
from app.db import get_session
from app.deps import current_user
from app.models import User
from app.security import verify_csrf
from app.templates_env import templates

router = APIRouter(prefix="/perfil")


def _require_user(user: Optional[User]) -> User:
    if not user:
        raise HTTPException(401, "login necessario")
    return user


def _check_password(user: User, password: str) -> bool:
    return bool(user.password_hash and verify_password(password, user.password_hash))


@router.get("")
async def perfil_home():
    return RedirectResponse("/perfil/nome", status_code=303)


@router.get("/nome")
async def nome_form(request: Request, user: Optional[User] = Depends(current_user)):
    return templates.TemplateResponse(
        request,
        "perfil/nome.html",
        {"user": _require_user(user), "errors": []},
    )


@router.post("/nome")
async def nome_save(
    request: Request,
    nome_completo: str = Form(...),
    senha_atual: str = Form(...),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    current = _require_user(user)
    name = nome_completo.strip()
    errors: list[str] = []
    if len(name) < 2:
        errors.append("Nome muito curto.")
    if len(name) > 80:
        errors.append("Nome muito longo.")
    if not errors and not _check_password(current, senha_atual):
        errors.append("Senha atual incorreta.")
    if errors:
        return templates.TemplateResponse(
            request,
            "perfil/nome.html",
            {"user": current, "errors": errors, "nome_completo": name},
            status_code=400,
        )

    db_user = session.get(User, current.id)
    db_user.nome_completo = name
    session.add(db_user)
    session.commit()
    return RedirectResponse("/", status_code=303)


@router.get("/nickname")
async def nickname_form(request: Request, user: Optional[User] = Depends(current_user)):
    return templates.TemplateResponse(
        request,
        "perfil/nickname.html",
        {"user": _require_user(user), "errors": []},
    )


@router.post("/nickname")
async def nickname_save(
    request: Request,
    nickname: str = Form(...),
    senha_atual: str = Form(...),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    current = _require_user(user)
    nick = nickname.strip()
    errors: list[str] = []
    if len(nick) < 2:
        errors.append("Nickname muito curto.")
    if len(nick) > 30:
        errors.append("Nickname muito longo.")
    if not errors:
        clash = session.exec(select(User).where(User.nickname == nick, User.id != current.id)).first()
        if clash:
            errors.append("Nickname ja esta em uso.")
    if not errors and not _check_password(current, senha_atual):
        errors.append("Senha atual incorreta.")
    if errors:
        return templates.TemplateResponse(
            request,
            "perfil/nickname.html",
            {"user": current, "errors": errors, "nickname": nick},
            status_code=400,
        )

    db_user = session.get(User, current.id)
    db_user.nickname = nick
    session.add(db_user)
    session.commit()
    return RedirectResponse("/", status_code=303)


@router.get("/senha")
async def senha_form(request: Request, user: Optional[User] = Depends(current_user)):
    return templates.TemplateResponse(
        request,
        "perfil/senha.html",
        {"user": _require_user(user), "errors": []},
    )


@router.post("/senha")
async def senha_save(
    request: Request,
    senha_atual: str = Form(...),
    senha_nova: str = Form(...),
    senha_nova_confirma: str = Form(...),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    current = _require_user(user)
    errors: list[str] = []
    if not _check_password(current, senha_atual):
        errors.append("Senha atual incorreta.")
    if not validate_password(senha_nova):
        errors.append("Senha nova invalida.")
    if senha_nova != senha_nova_confirma:
        errors.append("Confirmacao da senha nao confere.")
    if errors:
        return templates.TemplateResponse(
            request,
            "perfil/senha.html",
            {"user": current, "errors": errors},
            status_code=400,
        )

    db_user = session.get(User, current.id)
    db_user.password_hash = hash_password(senha_nova)
    session.add(db_user)
    session.commit()
    return RedirectResponse("/", status_code=303)
