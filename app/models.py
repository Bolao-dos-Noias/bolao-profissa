from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: Optional[str] = Field(default=None, unique=True, index=True)
    username: Optional[str] = Field(default=None, unique=True, index=True)
    nickname: str = Field(index=True, unique=True)
    nome_completo: Optional[str] = None
    roster_slug: Optional[str] = Field(default=None, unique=True, index=True)
    invite_code: Optional[str] = Field(default=None, unique=True, index=True)
    password_hash: Optional[str] = None
    is_admin: bool = False
    edit_unlock_until: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utcnow)


class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    name_pt: str
    fifa_code: str = Field(unique=True)
    iso2: str
    group_letter: str = Field(index=True)


class Match(SQLModel, table=True):
    __tablename__ = "matches"

    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: Optional[str] = Field(default=None, unique=True, index=True)
    stage: str = Field(index=True)
    group_letter: Optional[str] = Field(default=None, index=True)
    match_no: Optional[int] = Field(default=None, index=True)
    home_team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    away_team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    slot_home: Optional[str] = None
    slot_away: Optional[str] = None
    kickoff_utc: datetime = Field(index=True)
    venue: Optional[str] = None
    status: str = Field(default="SCHEDULED", index=True)
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    result: Optional[str] = None
    last_synced_at: Optional[datetime] = None
    live_clock: Optional[str] = None
    live_period: Optional[int] = None


class BetGroup(SQLModel, table=True):
    __tablename__ = "bets_group"
    __table_args__ = (UniqueConstraint("user_id", "match_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    match_id: int = Field(foreign_key="matches.id", index=True)
    pick: str
    updated_at: datetime = Field(default_factory=utcnow)


class BetKnockout(SQLModel, table=True):
    __tablename__ = "bets_knockout"
    __table_args__ = (UniqueConstraint("user_id", "stage", "team_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    stage: str = Field(index=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    updated_at: datetime = Field(default_factory=utcnow)


class BetMatch(SQLModel, table=True):
    __tablename__ = "bets_match"
    __table_args__ = (UniqueConstraint("user_id", "match_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    match_id: int = Field(foreign_key="matches.id", index=True)
    winner_team_id: int = Field(foreign_key="teams.id")
    updated_at: datetime = Field(default_factory=utcnow)


class BetTieBreak(SQLModel, table=True):
    __tablename__ = "bets_tie_break"
    __table_args__ = (UniqueConstraint("user_id", "group_letter"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    group_letter: str
    ordered_team_ids: str
    updated_at: datetime = Field(default_factory=utcnow)


class BetThirdsOrder(SQLModel, table=True):
    __tablename__ = "bets_thirds_order"

    user_id: int = Field(primary_key=True, foreign_key="users.id")
    ordered_team_ids: str
    updated_at: datetime = Field(default_factory=utcnow)


class Setting(SQLModel, table=True):
    __tablename__ = "settings"

    key: str = Field(primary_key=True)
    value: str


class LeaderboardSnapshot(SQLModel, table=True):
    __tablename__ = "leaderboard_snapshots"

    id: Optional[int] = Field(default=None, primary_key=True)
    captured_at: datetime = Field(default_factory=utcnow, index=True)
    match_id: Optional[int] = Field(default=None, index=True)
    ordering: str

