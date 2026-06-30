import asyncio

from app.services.sincronizacao import sync_once


def main() -> None:
    updated = asyncio.run(sync_once())
    print({"matches_updated": updated})


if __name__ == "__main__":
    main()

