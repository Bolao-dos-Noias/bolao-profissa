from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlmodel import Session, select
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .db import engine, get_session, init_db
from .deps import can_edit_picks, missing_picks_summary, user_state
from .models import Match, User
from .routers import admin, auth, bets, compare, leaderboard, live, pages, perfil, viewer
from .security import limiter
from .templates_env import templates


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Bolao Profissa", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

ALLOW_UNAUTH = {"/", "/login", "/login/codigo", "/logout", "/healthz", "/favicon.ico"}
ALLOW_NO_PROFILE = {"/complete-profile", "/logout", "/healthz"}
ALLOW_NO_BET = {"/aposta", "/logout", "/healthz"}
ALLOW_NO_BET_PREFIX = ("/perfil",)
ALLOW_PREFIX_ALL = ("/static/", "/api/")
ADMIN_TOKEN_PATHS = {"/admin/seed", "/admin/sync"}
ADMIN_SESSION_PREFIX = "/admin/users"


class WorkflowGateMiddleware:
    def __init__(self, inner_app):
        self.inner_app = inner_app

    @staticmethod
    def _is_public_path(path: str) -> bool:
        return (
            path in {"/healthz", "/favicon.ico"}
            or path in ADMIN_TOKEN_PATHS
            or any(path.startswith(prefix) for prefix in ALLOW_PREFIX_ALL)
        )

    @staticmethod
    def _can_skip_bet_gate(path: str) -> bool:
        return (
            path in ALLOW_NO_BET
            or path in ALLOW_UNAUTH
            or any(path.startswith(prefix) for prefix in ALLOW_NO_BET_PREFIX)
        )

    async def _redirect(self, scope, receive, send, location: str) -> None:
        await RedirectResponse(location, status_code=303)(scope, receive, send)

    @staticmethod
    def _workflow_state(user_id: int):
        with Session(engine) as session:
            user = session.get(User, user_id)
            state = user_state(session, user)
            edit_open = can_edit_picks(user)
            preview, total = missing_picks_summary(session, user) if edit_open else ([], 0)
        return user, state, edit_open, preview, total

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.inner_app(scope, receive, send)
            return

        request = Request(scope, receive)
        path = scope.get("path", "")
        if self._is_public_path(path):
            await self.inner_app(scope, receive, send)
            return

        user_id = request.session.get("uid") if "session" in request.scope else None
        if not user_id:
            request.state.user_state = "unauth"
            if path in ALLOW_UNAUTH:
                await self.inner_app(scope, receive, send)
                return
            await self._redirect(scope, receive, send, "/login")
            return

        user, state, edit_open, preview, total = self._workflow_state(user_id)
        request.state.user_state = state
        request.state.can_edit = edit_open
        request.state.missing_preview = preview
        request.state.missing_count = total

        if user and user.is_admin:
            if path.startswith(ADMIN_SESSION_PREFIX) or path == "/logout":
                await self.inner_app(scope, receive, send)
                return
            await self._redirect(scope, receive, send, "/admin/users")
            return

        if path.startswith("/admin/"):
            await self._redirect(scope, receive, send, "/login")
            return
        if state == "no_profile" and path not in ALLOW_NO_PROFILE:
            await self._redirect(scope, receive, send, "/complete-profile")
            return
        if state == "no_bet" and not self._can_skip_bet_gate(path):
            await self._redirect(scope, receive, send, "/aposta")
            return
        await self.inner_app(scope, receive, send)


app.add_middleware(WorkflowGateMiddleware)


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="bolao_sess",
    max_age=60 * 60 * 24 * 30,
    same_site="lax",
    https_only=settings.app_env == "prod",
)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(bets.router)
app.include_router(compare.router)
app.include_router(leaderboard.router)
app.include_router(live.router)
app.include_router(admin.router)
app.include_router(perfil.router)
app.include_router(viewer.router)


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/api/next-match")
async def api_next_match(session: Session = Depends(get_session)):
    now = datetime.now(timezone.utc)
    match = session.exec(
        select(Match)
        .where(Match.kickoff_utc >= now, Match.status != "FINISHED")
        .order_by(Match.kickoff_utc)
    ).first()
    if not match:
        return {"next_kickoff_iso": None}
    kickoff = match.kickoff_utc
    if kickoff.tzinfo is None:
        kickoff = kickoff.replace(tzinfo=timezone.utc)
    return {"next_kickoff_iso": kickoff.isoformat().replace("+00:00", "Z")}


@app.get("/favicon.ico")
async def favicon():
    return RedirectResponse("/static/assets/favicon.svg")


@app.exception_handler(404)
async def not_found(request: Request, exc):  # noqa: ARG001
    return templates.TemplateResponse(request, "404.html", {}, status_code=404)
