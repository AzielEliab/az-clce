"""Allow ``python -m clce`` to invoke the CLI."""

from clce.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
