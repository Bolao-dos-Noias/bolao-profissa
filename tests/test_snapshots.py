from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select

from app import db as app_db
from app.cli.recompute_snapshots import recompute
from app.domain.pontuacao import parse_snapshot
from app.models import BetGroup, BetKnockout, LeaderboardSnapshot, Match, Team, User
from app.services.sincronizacao import MatchUpdate, apply_updates


def _user(session: Session, nickname: str) -> User:
    user = User(nickname=nickname)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _team(session: Session, name: str, code: str, group: str = "A") -> Team:
    team = Team(name_pt=name, fifa_code=code, iso2=code.lower(), group_letter=group)
    session.add(team)
    session.commit()
    session.refresh(team)
    return team


def _group_match(
    session: Session,
    *,
    external_id: str,
    match_no: int,
    home: Team,
    away: Team,
    kickoff: datetime,
    status: str = "SCHEDULED",
    home_score: int | None = None,
    away_score: int | None = None,
    result: str | None = None,
    group: str = "A",
) -> Match:
    match = Match(
        external_id=external_id,
        stage="GROUP",
        group_letter=group,
        match_no=match_no,
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_utc=kickoff,
        status=status,
        home_score=home_score,
        away_score=away_score,
        result=result,
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def _r32_match(
    session: Session,
    *,
    external_id: str,
    match_no: int,
    home: Team,
    away: Team,
    kickoff: datetime,
    slot_home: str,
    slot_away: str,
) -> Match:
    match = Match(
        external_id=external_id,
        stage="R32",
        match_no=match_no,
        home_team_id=home.id,
        away_team_id=away.id,
        slot_home=slot_home,
        slot_away=slot_away,
        kickoff_utc=kickoff,
        status="SCHEDULED",
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    return match


def _bet(session: Session, user: User, match: Match, pick: str) -> None:
    session.add(BetGroup(user_id=user.id, match_id=match.id, pick=pick))
    session.commit()


def _totals(ordering: str) -> dict[int, int]:
    _ranks, totals = parse_snapshot(ordering)
    return totals


def test_sync_snapshots_are_incremental_and_ignore_live_matches():
    kickoff = datetime(2026, 6, 24, 19, tzinfo=timezone.utc)
    with Session(app_db.engine) as session:
        alice = _user(session, "alice")
        bob = _user(session, "bob")
        teams = [_team(session, f"Team {index}", f"T{index:02}") for index in range(6)]
        match_1 = _group_match(session, external_id="m1", match_no=1, home=teams[0], away=teams[1], kickoff=kickoff)
        match_2 = _group_match(session, external_id="m2", match_no=2, home=teams[2], away=teams[3], kickoff=kickoff)
        live = _group_match(
            session,
            external_id="live",
            match_no=3,
            home=teams[4],
            away=teams[5],
            kickoff=kickoff,
            status="LIVE",
            home_score=1,
            away_score=0,
        )

        _bet(session, alice, match_1, "HOME")
        _bet(session, bob, match_1, "AWAY")
        _bet(session, alice, match_2, "AWAY")
        _bet(session, bob, match_2, "HOME")
        _bet(session, bob, live, "HOME")

        updated = apply_updates(
            session,
            [
                MatchUpdate("m1", kickoff, None, "FINISHED", 1, 0, "Team 0", "Team 1"),
                MatchUpdate("m2", kickoff, None, "FINISHED", 2, 0, "Team 2", "Team 3"),
            ],
        )

        assert updated == 2
        snapshots = session.exec(select(LeaderboardSnapshot).order_by(LeaderboardSnapshot.id)).all()
        assert [snapshot.match_id for snapshot in snapshots] == [match_1.id, match_2.id]
        assert _totals(snapshots[0].ordering) == {alice.id: 6, bob.id: 0}
        assert _totals(snapshots[1].ordering) == {alice.id: 6, bob.id: 6}


def test_recompute_snapshots_repairs_existing_history_incrementally():
    kickoff = datetime(2026, 6, 24, 19, tzinfo=timezone.utc)
    with Session(app_db.engine) as session:
        alice = _user(session, "alice")
        bob = _user(session, "bob")
        teams = [_team(session, f"Team {index}", f"R{index:02}") for index in range(4)]
        match_1 = _group_match(
            session,
            external_id="r1",
            match_no=1,
            home=teams[0],
            away=teams[1],
            kickoff=kickoff,
            status="FINISHED",
            home_score=1,
            away_score=0,
            result="HOME",
        )
        match_2 = _group_match(
            session,
            external_id="r2",
            match_no=2,
            home=teams[2],
            away=teams[3],
            kickoff=kickoff,
            status="FINISHED",
            home_score=2,
            away_score=0,
            result="HOME",
        )
        _bet(session, alice, match_1, "HOME")
        _bet(session, bob, match_1, "AWAY")
        _bet(session, alice, match_2, "AWAY")
        _bet(session, bob, match_2, "HOME")
        wrong = f"{alice.id}:1:6,{bob.id}:2:12"
        session.add(LeaderboardSnapshot(match_id=match_1.id, captured_at=kickoff + timedelta(minutes=1), ordering=wrong))
        session.add(LeaderboardSnapshot(match_id=match_2.id, captured_at=kickoff + timedelta(minutes=2), ordering=wrong))
        session.commit()
        alice_id = alice.id
        bob_id = bob.id

    assert recompute(apply=True) == 2

    with Session(app_db.engine) as session:
        snapshots = session.exec(select(LeaderboardSnapshot).order_by(LeaderboardSnapshot.id)).all()
        assert _totals(snapshots[0].ordering) == {alice_id: 6, bob_id: 0}
        assert _totals(snapshots[1].ordering) == {alice_id: 6, bob_id: 6}


def test_recompute_awards_r32_top2_on_group_close_and_thirds_after_all_groups():
    kickoff = datetime(2026, 6, 24, 19, tzinfo=timezone.utc)
    with Session(app_db.engine) as session:
        alice = _user(session, "alice")
        bob = _user(session, "bob")
        a1 = _team(session, "A Winner", "A01", "A")
        a2 = _team(session, "A Runner Up", "A02", "A")
        a3 = _team(session, "A Third", "A03", "A")
        b1 = _team(session, "B Winner", "B01", "B")
        b2 = _team(session, "B Runner Up", "B02", "B")
        group_a_final = _group_match(
            session,
            external_id="group-a-final",
            match_no=1,
            home=a1,
            away=a2,
            kickoff=kickoff,
            status="FINISHED",
            home_score=1,
            away_score=0,
            result="HOME",
            group="A",
        )
        group_b_final = _group_match(
            session,
            external_id="group-b-final",
            match_no=2,
            home=b1,
            away=b2,
            kickoff=kickoff + timedelta(hours=2),
            status="FINISHED",
            home_score=1,
            away_score=0,
            result="HOME",
            group="B",
        )
        _r32_match(session, external_id="r32-a", match_no=33, home=a1, away=a2, kickoff=kickoff, slot_home="1A", slot_away="2A")
        _r32_match(session, external_id="r32-b", match_no=34, home=b1, away=a3, kickoff=kickoff, slot_home="1B", slot_away="3A/B")
        session.add(BetKnockout(user_id=alice.id, stage="R32", team_id=a1.id))
        session.add(BetKnockout(user_id=alice.id, stage="R32", team_id=a2.id))
        session.add(BetKnockout(user_id=bob.id, stage="R32", team_id=a3.id))
        wrong = f"{alice.id}:1:0,{bob.id}:2:0"
        session.add(LeaderboardSnapshot(match_id=group_a_final.id, captured_at=kickoff + timedelta(minutes=1), ordering=wrong))
        session.add(LeaderboardSnapshot(match_id=group_b_final.id, captured_at=kickoff + timedelta(hours=2, minutes=1), ordering=wrong))
        session.commit()
        alice_id = alice.id
        bob_id = bob.id

    assert recompute(apply=True) == 2

    with Session(app_db.engine) as session:
        snapshots = session.exec(select(LeaderboardSnapshot).order_by(LeaderboardSnapshot.id)).all()
        assert _totals(snapshots[0].ordering) == {alice_id: 6, bob_id: 0}
        assert _totals(snapshots[1].ordering) == {alice_id: 6, bob_id: 3}

