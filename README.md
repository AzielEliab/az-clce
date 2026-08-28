# AZ-CLCE

**Cross-Layer Consistency Engine.** Detects inconsistency across
representation (R), description (D), and reality (P). Optional negative
space N. Jaccard triple, pairwise average (paper §5), and CLCE+.

**Author:** Aziel Eliab
**Date:** 2026
**License:** [Apache-2.0](LICENSE)

> CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice.

See the spec: [docs/whitepaper.md](docs/whitepaper.md). Source papers:
[docs/source/AZ-CLCE-v2.0.pdf](docs/source/AZ-CLCE-v2.0.pdf),
[docs/source/AZ-CLCE-v1.0.txt](docs/source/AZ-CLCE-v1.0.txt).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
clce ui
```

Open http://127.0.0.1:8845 (loopback only). No CDN, no telemetry.

Counted download: [https://azclce-download-tracker.vibelock.workers.dev/](https://azclce-download-tracker.vibelock.workers.dev/)

Direct tarball (also counted): [az-clce-0.1.0.tar.gz](https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.1.0.tar.gz)

GitHub: [https://github.com/AzielEliab/az-clce](https://github.com/AzielEliab/az-clce)

---

## Honest scope

- CLCE detects **inconsistency, not intent**. Type D is a label, not a finding of malice.
- Human validation required.
- Not a cybersecurity exploit, not a scanner of other people's systems, not a lie detector.
- Advisory scores only. Threshold 0.7 is the paper's "acceptable" line, not a pass/fail of truth.
- Loopback UI, no CDN, no telemetry.
- Standalone from ForgeReceipts, ZionPattern, DecisionGATE, AZ-OS, Glossa Filter.

## What it computes

Layers are normalized token sets (lowercase, split on non-alnum).

| Quantity | Formula |
|----------|---------|
| Triple | `\|R ∩ D ∩ P\| / \|R ∪ D ∪ P\|` (empty-all → 1.0) |
| Pairwise | R↔D, D↔P, R↔P as Jaccard; §5 `final = average of three` |
| CLCE+ | `\|R ∩ D ∩ P\| / (\|R ∪ D ∪ P\| + \|N\|)` |

Band: 1.0 perfect; ≥0.7 acceptable; <0.7 structural inconsistency.

### Mismatch types (deterministic)

| Type | When | Meaning |
|------|------|---------|
| A Surface Error | R↔D low (<0.7) while D↔P and R↔P are higher | Docs/UI disagree; function closer to one layer |
| B Functional Error | R↔D high (≥0.7) while D↔P or R↔P is low | Pretty alignment, function diverges |
| C Structural Gap | High \|N\| relative to union, or all pairwise mediocre and triple <0.7 | Hidden or missing structure |
| D Intentional Obfuscation | **LABEL ONLY.** High N AND D↔P very low AND R↔D high | Representation matches description while reality and missing-elements diverge. Never a finding of malice. |

The report lists every matching type and prefers the most severe (D > C > B > A) as `primary`.

## Install

Python 3.10+. Stdlib only at runtime.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## CLI

```bash
clce version
clce ui                                          # 127.0.0.1:8845 loopback only
clce score --r "..." --d "..." --p "..." [--n "..."]
clce classify --r ... --d ... --p ... [--n ...]
clce gate --min 0.7 --r ... --d ... --p ...      # exit 0 if triple ≥ min else 1
```

`--json` prints the full report. `--help` lists `ui` and `version`.

## Library

```python
from clce import score, classify, gate

report = score(
    r="login button blue",
    d="login form submits",
    p="login button submits",
)
print(report.triple, report.pairwise_avg, report.plus, report.band)
print(classify(r="...", d="...", p="...", n="csrf session").types)
ok, report = gate(r="a", d="a", p="a", min_score=0.7)
```

## UI

`clce ui` binds **127.0.0.1:8845** only. Three textareas R/D/P, optional N,
Score / Classify / Gate. Shows triple + pairwise + CLCE+ + types + the
limitation banner. Self-contained CSS, no CDN, no telemetry. Dark matte / gold.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.azclce`.
Offline. No analytics. Dark matte / gold.

Three fields (R, D, P), optional N, score, mismatch types, limitation banner.

```bash
cd mobile
flutter create --org com.azieeliab --project-name azclce .
flutter pub get
flutter run
```

The `android/` and `ios/` folders in this tree are skeleton READMEs until you
run `flutter create .` (this machine has no Flutter SDK on PATH). Then open
`android/` in Android Studio or `ios/Runner.xcworkspace` in Xcode. Not a
store listing.

Counted desktop download: [https://azclce-download-tracker.vibelock.workers.dev/](https://azclce-download-tracker.vibelock.workers.dev/)

**Forks are welcome and always allowed.**

## Tests

```bash
pip install -e ".[dev]"
python -m pytest -q
```

Offline. No network. Stdlib runtime. pytest is the dev extra.

## Worker

Isolated download counter for this project only. Worker
`azclce-download-tracker`, project `azclce`, KV `AZCLCE_DOWNLOADS` bound as
`DOWNLOADS`. GET `/download` **serves** `az-clce-0.1.0.tar.gz` (does not 302
to GitHub). See [workers/download-tracker/README.md](workers/download-tracker/README.md).

Counted downloads (number on the button, no user reporting):
[https://azclce-download-tracker.vibelock.workers.dev/](https://azclce-download-tracker.vibelock.workers.dev/)

## Layout

```
clce/                 library (engine, cli, ui)
clce/web/             loopback UI
tests/                pytest
docs/whitepaper.md    spec
docs/source/          v1.0 TXT and v2.0 PDF
mobile/               Flutter iPhone + Android (`flutter create .`)
workers/download-tracker/   Cloudflare Worker
```

## AI runtime

CLCE detects **inconsistency, not intent**. Type D is a label, not a
finding of malice. Threshold 0.7 is advisory.

- `POST https://azclce-download-tracker.vibelock.workers.dev/v1/score` `{r,d,p,n}`
- `POST https://azclce-download-tracker.vibelock.workers.dev/v1/classify` `{r,d,p,n}`
- `POST https://azclce-download-tracker.vibelock.workers.dev/v1/gate` `{r,d,p,n,min}`
- OpenAPI 3.1: https://azclce-download-tracker.vibelock.workers.dev/openapi.json
- Help: https://azclce-download-tracker.vibelock.workers.dev/ai

`/v1` does not increment the download counter.

One-URL catalog: https://aziel-runtime.vibelock.workers.dev/openapi.json


## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
