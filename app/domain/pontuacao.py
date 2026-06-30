from dataclasses import dataclass, field
from typing import Optional

PESOS_MATA_MATA = {"R32": 3, "R16": 5, "QF": 7, "SF": 10, "F": 14, "CHAMPION": 20}
ORDEM_MATA_MATA = ["R32", "R16", "QF", "SF", "F", "CHAMPION"]


@dataclass
class ScoreRow:
    user_id: int
    nickname: str
    nome_completo: str = ""
    group_pts: int = 0
    zebra_pts: int = 0
    zebra_max: int = 0
    ko_pts: int = 0
    total: int = 0
    hit_champion: bool = False
    hit_f: int = 0
    hit_sf: int = 0
    hit_qf: int = 0
    hit_r16: int = 0
    hit_r32: int = 0
    by_stage: dict[str, int] = field(default_factory=dict)
    rank: int = 0
    prev_rank: Optional[int] = None
    delta_rank: Optional[int] = None


def ordenar_ranking(rows: list[ScoreRow]) -> list[ScoreRow]:
    for row in rows:
        row.total = row.group_pts + row.zebra_pts + row.ko_pts

    ordered = sorted(
        rows,
        key=lambda row: (
            -row.total,
            -int(row.hit_champion),
            -row.hit_f,
            -row.hit_sf,
            -row.hit_qf,
            -row.hit_r16,
            -row.hit_r32,
            -row.group_pts,
            (row.nickname or "").lower(),
        ),
    )

    previous_tier: tuple | None = None
    previous_rank = 0
    for index, row in enumerate(ordered, 1):
        tier = (
            row.total,
            int(row.hit_champion),
            row.hit_f,
            row.hit_sf,
            row.hit_qf,
            row.hit_r16,
            row.hit_r32,
            row.group_pts,
        )
        if tier == previous_tier:
            row.rank = previous_rank
        else:
            row.rank = index
            previous_tier = tier
            previous_rank = index
    return ordered


def serialize_snapshot_ordering(rows: list[ScoreRow]) -> str:
    return ",".join(f"{row.user_id}:{row.rank}:{row.total}" for row in rows)


def parse_snapshot(ordering: str) -> tuple[dict[int, int], dict[int, int]]:
    items = [item.strip() for item in (ordering or "").split(",") if item.strip()]
    ranks: dict[int, int] = {}
    totals: dict[int, int] = {}
    if not items:
        return ranks, totals
    if ":" in items[0]:
        for item in items:
            parts = item.split(":")
            user_id = int(parts[0])
            ranks[user_id] = int(parts[1]) if len(parts) > 1 else 0
            if len(parts) > 2:
                try:
                    totals[user_id] = int(parts[2])
                except ValueError:
                    pass
    else:
        for index, item in enumerate(items, 1):
            ranks[int(item)] = index
    return ranks, totals

