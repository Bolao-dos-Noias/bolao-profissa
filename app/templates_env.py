from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.templating import Jinja2Templates

from .security import csrf_token

BRT = timezone(timedelta(hours=-3))


templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def brt(value: datetime | None, fmt: str = "%d/%m/%Y %H:%M") -> str:
    if value is None:
        return "-"
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(BRT).strftime(fmt)


def outcome_label(value: str | None) -> str:
    return {"HOME": "Mandante", "DRAW": "Empate", "AWAY": "Visitante"}.get(value or "", "-")


templates.env.globals["csrf_token"] = csrf_token
templates.env.filters["brt"] = brt
templates.env.filters["outcome"] = outcome_label

