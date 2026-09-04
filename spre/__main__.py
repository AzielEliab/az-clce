"""Allow ``python -m spre`` to invoke the SPRE CLI."""

from spre.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
