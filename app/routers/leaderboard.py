from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session, select

from app.db import get_session
from app.deps import current_user, deadline_passed
from app.domain.pontuacao import parse_snapshot
from app.models import Match, Team, User
from app.services.ranking import compute_scores, current_maxima, ordered_leaderboard_snapshots
from app.templates_env import templates

router = APIRouter()


def _chart_payload(session: Session) -> dict:
    snapshots = ordered_leaderboard_snapshots(session)
    users = {
        user.id: user.nickname
        for user in session.exec(select(User).where(User.is_admin == False)).all()  # noqa: E712
        if user.id is not None
    }
    match_ids = [snapshot.match_id for snapshot in snapshots if snapshot.match_id]
    matches = {}
    if match_ids:
        matches = {match.id: match for match in session.exec(select(Match).where(Match.id.in_(match_ids))).all()}
    teams = {team.id: team for team in session.exec(select(Team)).all()}

    series: dict[int, list[dict]] = {user_id: [] for user_id in users}
    points_seen: list[int] = []
    labels: list[str] = []
    for index, snapshot in enumerate(snapshots, 1):
        _ranks, totals = parse_snapshot(snapshot.ordering)
        match = matches.get(snapshot.match_id)
        if match:
            home = teams.get(match.home_team_id)
            away = teams.get(match.away_team_id)
            if home and away:
                label = f"{home.name_pt} x {away.name_pt}"
            else:
                label = f"Jogo {match.match_no or index}"
        else:
            label = f"Snapshot {index}"
        labels.append(label)
        for user_id in users:
            total = totals.get(user_id, 0)
            points_seen.append(total)
            series[user_id].append({"x": index, "total": total})
    return {
        "has_data": bool(snapshots),
        "labels": labels,
        "series": [
            {"user_id": user_id, "nickname": users[user_id], "points": points}
            for user_id, points in series.items()
        ],
        "max_total": max(points_seen) if points_seen else 0,
    }


@router.get("/leaderboard")
async def leaderboard(
    request: Request,
    user: Optional[User] = Depends(current_user),
    session: Session = Depends(get_session),
):
    rows = compute_scores(session)
    if not deadline_passed():
        rows = sorted(rows, key=lambda row: row.nickname.lower())
    live_matches_count = len(session.exec(select(Match).where(Match.status == "LIVE")).all())
    return templates.TemplateResponse(
        request,
        "leaderboard/leaderboard.html",
        {
            "user": user,
            "rows": rows,
            "pre_cup": not deadline_passed(),
            "chart": _chart_payload(session),
            "live_matches_count": live_matches_count,
            "maxima": current_maxima(session),
        },
    )
