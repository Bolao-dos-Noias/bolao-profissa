from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import Depends, Request
from sqlmodel import Session, select

from .config import settings
from .db import get_session
from .models import BetGroup, BetKnockout, User


def current_user(request: Request, session: Session = Depends(get_session)) -> Optional[User]:
    user_id = request.session.get("uid")
    if not user_id:
        return None
    return session.get(User, user_id)


def deadline_passed() -> bool:
    deadline = settings.bolao_deadline_utc
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) >= deadline


def can_edit_picks(user: Optional[User]) -> bool:
    if not user or user.is_admin:
        return False
    if not deadline_passed():
        return True
    unlock = user.edit_unlock_until
    if unlock is None:
        return False
    if unlock.tzinfo is None:
        unlock = unlock.replace(tzinfo=timezone.utc)
    return unlock > datetime.now(timezone.utc)


def is_admin(user: Optional[User]) -> bool:
    return bool(user and user.is_admin)


def has_started_bet(session: Session, user: User) -> bool:
    if user.id is None:
        return False
    if session.exec(select(BetGroup).where(BetGroup.user_id == user.id)).first():
        return True
    if session.exec(select(BetKnockout).where(BetKnockout.user_id == user.id)).first():
        return True
    return False


UserState = Literal["unauth", "no_profile", "no_bet", "active"]


def user_state(session: Session, user: Optional[User]) -> UserState:
    if not user:
        return "unauth"
    if not user.nome_completo or not user.password_hash:
        return "no_profile"
    if user.is_admin:
        return "active"
    if not has_started_bet(session, user):
        return "no_bet"
    return "active"


def missing_picks_summary(session: Session, user: Optional[User], limit: int = 5) -> tuple[list[str], int]:
    from .models import Match

    if not user or user.is_admin or user.id is None:
        return [], 0

    group_matches = session.exec(
        select(Match).where(Match.stage == "GROUP").order_by(Match.match_no, Match.id)
    ).all()
    user_bets = session.exec(select(BetGroup).where(BetGroup.user_id == user.id)).all()
    bet_match_ids = {bet.match_id for bet in user_bets}
    items: list[str] = []
    for match in group_matches:
        if match.id in bet_match_ids:
            continue
        label = f"Jogo #{match.match_no or match.id}"
        if match.group_letter:
            label += f" - Grupo {match.group_letter}"
        items.append(label)

    champion = session.exec(
        select(BetKnockout).where(BetKnockout.user_id == user.id, BetKnockout.stage == "CHAMPION")
    ).first()
    if not champion:
        items.append("Palpite de campeão")

    return items[:limit], len(items)

