from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.auth import hash_password, validate_password, verify_password
from app.db import get_session
from app.deps import current_user
from app.models import User
from app.security import limiter, verify_csrf
from app.templates_env import templates

router = APIRouter()


@router.get("/login")
async def login_form(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {"registered": request.query_params.get("registered") == "1"},
    )


@router.post("/login")
@limiter.limit("100/15minute")
async def login(
    request: Request,
    nickname: str = Form(...),
    senha: str = Form(...),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.nickname == nickname.strip())).first()
    if not user or not verify_password(senha, user.password_hash):
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {"error": "Nickname ou senha incorretos.", "nickname_value": nickname.strip()},
            status_code=401,
        )
    request.session["uid"] = user.id
    return RedirectResponse("/", status_code=303)


@router.get("/login/codigo")
async def login_codigo_form(request: Request):
    return templates.TemplateResponse(request, "auth/login_codigo.html", {})


@router.post("/login/codigo")
@limiter.limit("100/15minute")
async def login_codigo(
    request: Request,
    code: str = Form(...),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.invite_code == code.strip())).first()
    if not user:
        return templates.TemplateResponse(
            request,
            "auth/login_codigo.html",
            {"error": "Codigo invalido."},
            status_code=401,
        )
    if user.password_hash:
        return templates.TemplateResponse(
            request,
            "auth/login_codigo.html",
            {"error": "Codigo ja usado. Entre com nickname e senha."},
            status_code=401,
        )
    request.session["uid"] = user.id
    return RedirectResponse("/complete-profile", status_code=303)


@router.get("/complete-profile")
async def complete_profile_form(request: Request, user: Optional[User] = Depends(current_user)):
    if not user:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(request, "auth/complete_profile.html", {"user": user, "errors": []})


@router.post("/complete-profile")
async def complete_profile_save(
    request: Request,
    nome_completo: str = Form(""),
    nickname: str = Form(""),
    senha: str = Form(...),
    user: Optional[User] = Depends(current_user),
    _: None = Depends(verify_csrf),
    session: Session = Depends(get_session),
):
    if not user:
        return RedirectResponse("/login", status_code=303)

    errors: list[str] = []
    new_nickname = (nickname or user.nickname).strip()
    if len(new_nickname) < 2:
        errors.append("Nickname precisa ter pelo menos 2 caracteres.")
    if not validate_password(senha):
        errors.append("Senha invalida.")
    if new_nickname != user.nickname:
        clash = session.exec(select(User).where(User.nickname == new_nickname)).first()
        if clash:
            errors.append("Nickname ja esta em uso.")
    if errors:
        return templates.TemplateResponse(
            request,
            "auth/complete_profile.html",
            {"user": user, "errors": errors},
            status_code=400,
        )

    db_user = session.get(User, user.id)
    db_user.nickname = new_nickname
    db_user.nome_completo = nome_completo.strip() or db_user.nome_completo or new_nickname
    db_user.password_hash = hash_password(senha)
    db_user.invite_code = None
    session.add(db_user)
    session.commit()
    request.session.clear()
    return RedirectResponse("/login?registered=1", status_code=303)


@router.api_route("/logout", methods=["GET", "POST"])
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)
