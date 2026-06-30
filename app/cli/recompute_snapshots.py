import argparse

from sqlmodel import Session

from app.db import engine
from app.domain.pontuacao import serialize_snapshot_ordering
from app.models import LeaderboardSnapshot, Match
from app.services.ranking import compute_scores, compute_snapshot_ordering, ordered_leaderboard_snapshots


def _sql_escape(value: str) -> str:
    return value.replace("'", "''")


def _snapshot_label(session: Session, snapshot: LeaderboardSnapshot) -> str:
    if not snapshot.match_id:
        return f"-- snapshot id={snapshot.id} match_id=NULL"
    match = session.get(Match, snapshot.match_id)
    if not match:
        return f"-- snapshot id={snapshot.id} match_id={snapshot.match_id}"
    number = f"#{match.match_no}" if match.match_no is not None else "#?"
    group = f" group={match.group_letter}" if match.group_letter else ""
    return f"-- snapshot id={snapshot.id} match_id={snapshot.match_id} {match.stage} {number}{group}"


def recompute(apply: bool = False, only_changed: bool = False) -> int:
    processed = 0
    changed = 0
    with Session(engine) as session:
        snapshots = ordered_leaderboard_snapshots(session)
        snapshot_match_ids: set[int] = set()
        for snapshot in snapshots:
            if snapshot.match_id:
                snapshot_match_ids.add(int(snapshot.match_id))
                csv = compute_snapshot_ordering(session, snapshot_match_ids)
            else:
                rows = compute_scores(session, cutoff_utc=snapshot.captured_at)
                csv = serialize_snapshot_ordering(rows)

            differs = csv != (snapshot.ordering or "")
            if differs:
                changed += 1
            if differs or not only_changed:
                print(_snapshot_label(session, snapshot))
                print(
                    "UPDATE leaderboard_snapshots "
                    f"SET ordering='{_sql_escape(csv)}' WHERE id={snapshot.id};"
                )
            if apply:
                snapshot.ordering = csv
                session.add(snapshot)
            processed += 1
        if apply:
            session.commit()
            print(f"-- {processed} snapshots processados; {changed} alterados")
        else:
            print(f"-- DRY-RUN: {processed} snapshots processados; {changed} alterariam")
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Recalcula historico do leaderboard.")
    parser.add_argument("--apply", action="store_true", help="Persiste as alteracoes.")
    parser.add_argument("--only-changed", action="store_true", help="Mostra apenas linhas que mudariam.")
    args = parser.parse_args()
    recompute(apply=args.apply, only_changed=args.only_changed)


if __name__ == "__main__":
    main()

