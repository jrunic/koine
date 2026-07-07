import sys


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        print("uso: koine <cliente|subcomando> ...", file=sys.stderr)
        return 2
    return 0
