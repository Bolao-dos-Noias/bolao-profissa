from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy import event, text
from sqlalchemy.pool import NullPool
from sqlmodel import Session, SQLModel, create_engine

from .auth import hash_password
from .config import settings

RAW_DATABASE_URL = settings.database_url
IS_LOCAL_SQLITE = RAW_DATABASE_URL.startswith("sqlite:///")
IS_LIBSQL = RAW_DATABASE_URL.startswith(("sqlite+libsql://", "libsql://"))


def _normalize_libsql(url: str) -> tuple[str, dict]:
    if url.startswith("libsql://"):
        url = f"sqlite+{url}"
    parsed = urlparse(url)
    qs = dict(parse_qsl(parsed.query))
    connect_args: dict[str, str] = {}
    token = qs.pop("authToken", None) or qs.pop("auth_token", None)
    if token:
        connect_args["auth_token"] = token
    qs.setdefault("secure", "true")
    cleaned = urlunparse(parsed._replace(query=urlencode(qs)))
    return cleaned, connect_args


if IS_LOCAL_SQLITE and "./" in RAW_DATABASE_URL:
    Path(RAW_DATABASE_URL.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

if IS_LIBSQL:
    DATABASE_URL, CONNECT_ARGS = _normalize_libsql(RAW_DATABASE_URL)

    from sqlalchemy.dialects.sqlite.base import SQLiteDialect

    def _libsql_get_isolation_level(self, dbapi_conn):  # noqa: ARG001
        return "SERIALIZABLE"

    SQLiteDialect.get_isolation_level = _libsql_get_isolation_level  # type: ignore[assignment]
else:
    DATABASE_URL = RAW_DATABASE_URL
    CONNECT_ARGS = {"check_same_thread": False} if IS_LOCAL_SQLITE else {}

ENGINE_KWARGS: dict = {"connect_args": CONNECT_ARGS, "echo": False}
if IS_LIBSQL:
    ENGINE_KWARGS["poolclass"] = NullPool
elif not IS_LOCAL_SQLITE:
    ENGINE_KWARGS["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **ENGINE_KWARGS)


if IS_LOCAL_SQLITE:

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def _add_column_if_missing(table: str, column: str, kind: str) -> None:
    try:
        with engine.connect() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {kind}"))
            conn.commit()
    except Exception:
        pass


def _run_compat_migrations() -> None:
    for table, column, kind in [
        ("users", "nome_completo", "TEXT"),
        ("users", "roster_slug", "TEXT"),
        ("users", "invite_code", "TEXT"),
        ("users", "edit_unlock_until", "TEXT"),
        ("matches", "slot_home", "TEXT"),
        ("matches", "slot_away", "TEXT"),
        ("matches", "live_clock", "TEXT"),
        ("matches", "live_period", "INTEGER"),
    ]:
        _add_column_if_missing(table, column, kind)


def _ensure_admin() -> None:
    from .models import User

    with Session(engine) as session:
        admin = session.exec(text("SELECT id FROM users WHERE nickname='admin'")).first()
        password_hash = hash_password(settings.admin_password)
        if admin:
            session.execute(
                text("UPDATE users SET password_hash=:hash, is_admin=1 WHERE nickname='admin'"),
                {"hash": password_hash},
            )
        else:
            session.add(
                User(
                    nickname="admin",
                    username="admin",
                    email="admin@bolao.local",
                    nome_completo="Admin",
                    password_hash=password_hash,
                    is_admin=True,
                )
            )
        session.commit()


def init_db() -> None:
    from . import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    _run_compat_migrations()
    _ensure_admin()


def get_session():
    with Session(engine) as session:
        yield session

