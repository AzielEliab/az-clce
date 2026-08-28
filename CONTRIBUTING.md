# Contributing to AZ-CLCE

**Forks are first-class.** This project is Apache-2.0; you do not need
permission to fork, patch, or redistribute.

**Forks are welcome and always allowed.**

## How to run tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
```

Python 3.10+. Core is stdlib only (`dataclasses`, `json`, `http.server`,
`argparse`, `re`). pytest is the dev extra. No network. No ML.

## Ground rules

1. **Inconsistency, not intent.** Type D is a label, not a finding of
   malice. Do not add "lie detector", exploit, or remote-scan features.
2. **Human validation required.** Scores are advisory. Threshold 0.7 is
   the paper's acceptable line, not a pass/fail of truth.
3. **Keep the dependency list tiny.** Stdlib only in the core.
4. **UI binds loopback only** (`127.0.0.1:8845`). Do not listen on `0.0.0.0`.
5. **Do not merge this product into ForgeReceipts, ZionPattern Solver,
   DecisionGATE, AZ-OS, Glossa Filter, or any *Lock tree.** AZ-CLCE is
   standalone.
6. **Do not mix the download tracker** with any other product's Worker or KV.
7. New behavior needs a test that fails without the change.
8. Tokenization stays lowercase + split on non-alnum. Jaccard empty-all
   is 1.0.

## Where to change things

- Token sets / Jaccard / CLCE+ / types: `clce/engine.py`
- CLI: `clce/cli.py`
- Local UI: `clce/ui.py`, `clce/web/`
- Spec: `docs/whitepaper.md`
- Source papers: `docs/source/`
- Flutter: `mobile/`
- Isolated counter: `workers/download-tracker/`

## License of contributions

By submitting a change you agree it is licensed under Apache-2.0, the
same license as the rest of the tree. Keep the copyright lines honest.
Ship as Aziel Eliab.
