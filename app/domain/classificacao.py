from dataclasses import dataclass


@dataclass
class StandingRow:
    team_id: int
    team_name: str
    iso2: str
    fifa_code: str
    points: int
    rank: int
    tied: bool


def apply_tiebreak(rows: list[StandingRow], ordered_ids: list[int]) -> list[StandingRow]:
    if not ordered_ids:
        return rows
    positions = {team_id: index for index, team_id in enumerate(ordered_ids)}
    reordered = sorted(rows, key=lambda row: (-row.points, positions.get(row.team_id, 999), row.team_name))
    for index, row in enumerate(reordered, 1):
        row.rank = index
    return reordered


def compute_standings(
    group_matches: dict[str, list],
    picks: dict[int, str],
    teams_by_id: dict[int, object],
    tiebreaks: dict[str, list[int]] | None = None,
) -> dict[str, list[StandingRow]]:
    standings: dict[str, list[StandingRow]] = {}
    for group, matches in group_matches.items():
        team_ids: set[int] = set()
        for match in matches:
            if match.home_team_id:
                team_ids.add(match.home_team_id)
            if match.away_team_id:
                team_ids.add(match.away_team_id)

        points = {team_id: 0 for team_id in team_ids}
        for match in matches:
            pick = picks.get(match.id)
            if not pick:
                continue
            if pick == "HOME" and match.home_team_id:
                points[match.home_team_id] += 3
            elif pick == "AWAY" and match.away_team_id:
                points[match.away_team_id] += 3
            elif pick == "DRAW":
                if match.home_team_id:
                    points[match.home_team_id] += 1
                if match.away_team_id:
                    points[match.away_team_id] += 1

        ordered = sorted(team_ids, key=lambda team_id: (-points[team_id], teams_by_id[team_id].name_pt))
        rows = [
            StandingRow(
                team_id=team_id,
                team_name=teams_by_id[team_id].name_pt,
                iso2=teams_by_id[team_id].iso2,
                fifa_code=teams_by_id[team_id].fifa_code,
                points=points[team_id],
                rank=index,
                tied=False,
            )
            for index, team_id in enumerate(ordered, 1)
        ]
        for index, row in enumerate(rows):
            if index > 0 and row.points == rows[index - 1].points:
                row.tied = True
                rows[index - 1].tied = True
        if tiebreaks and group in tiebreaks:
            rows = apply_tiebreak(rows, tiebreaks[group])
        standings[group] = rows
    return dict(sorted(standings.items()))


def derive_r32_candidates(standings: dict[str, list[StandingRow]]) -> tuple[dict[str, list[int]], list[dict]]:
    top2: dict[str, list[int]] = {}
    thirds: list[dict] = []
    for group, rows in standings.items():
        top2[group] = [row.team_id for row in rows[:2]]
        if len(rows) >= 3:
            row = rows[2]
            thirds.append(
                {
                    "group": group,
                    "team_id": row.team_id,
                    "team_name": row.team_name,
                    "iso2": row.iso2,
                    "points": row.points,
                    "tied_with_4th": row.tied and len(rows) >= 4 and rows[3].points == row.points,
                }
            )
    thirds.sort(key=lambda item: (-item["points"], item["group"]))
    return top2, thirds

