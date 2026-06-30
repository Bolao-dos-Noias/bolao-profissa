import argparse

from app.services.seed import seed


def main() -> None:
    parser = argparse.ArgumentParser(description="Popula times e jogos da Copa 2026.")
    parser.add_argument("--force", action="store_true", help="Apaga tabelas e recria o seed.")
    args = parser.parse_args()
    result = seed(force=args.force)
    print(result)


if __name__ == "__main__":
    main()

