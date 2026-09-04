# AZ-CLCE

**Cross-Layer Consistency Engine.** Detects inconsistency across
representation (R), description (D), and reality (P). Optional negative
space N. Jaccard triple, pairwise average (paper §5), and CLCE+.

**Author:** Aziel Eliab
**Date:** 2026
**License:** [Apache-2.0](LICENSE)
**Version:** 0.3.0

> CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice.
> SPRE scores structural similarity only. Official narrative is not evidence. Never guilt.

See the spec: [docs/whitepaper.md](docs/whitepaper.md). Source papers:
[docs/source/AZ-CLCE-v2.0.pdf](docs/source/AZ-CLCE-v2.0.pdf),
[docs/source/AZ-CLCE-v1.0.txt](docs/source/AZ-CLCE-v1.0.txt).
How to contribute: [CONTRIBUTING.md](CONTRIBUTING.md).

**Forks are welcome and always allowed.**


## One-click install

```bash
curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash
```

The script curls the **counted** tarball from this project's Worker
(`/download`, User-Agent `Mozilla/5.0`), extracts, makes a venv, and
`pip install -e .`. Then run `clce ui`.

Or tap **Download** / **One-click install** on the Worker homepage
(a 6th-grader can tap it):
https://azclce-download-tracker.vibelock.workers.dev/

## Counted download (Cloudflare Worker)

**This is the counted download.** GitHub releases exist as a mirror.
The Worker serves the gzip itself (HTTP 200, no 302 to GitHub).

# → [https://azclce-download-tracker.vibelock.workers.dev/](https://azclce-download-tracker.vibelock.workers.dev/) ←

Direct tarball (also counted):
[az-clce-0.3.0.tar.gz](https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.3.0.tar.gz)

- Live count JSON: [https://azclce-download-tracker.vibelock.workers.dev/stats](https://azclce-download-tracker.vibelock.workers.dev/stats)
- OpenAPI: [https://azclce-download-tracker.vibelock.workers.dev/openapi.json](https://azclce-download-tracker.vibelock.workers.dev/openapi.json)
- Skill: [https://azclce-download-tracker.vibelock.workers.dev/v1/skill](https://azclce-download-tracker.vibelock.workers.dev/v1/skill)
- One-click install: [https://azclce-download-tracker.vibelock.workers.dev/install.sh](https://azclce-download-tracker.vibelock.workers.dev/install.sh)
- GitHub: [https://github.com/AzielEliab/az-clce](https://github.com/AzielEliab/az-clce)

Isolated counter: Worker `azclce-download-tracker`, KV `AZCLCE_DOWNLOADS`. Not mixed with any other product. `/v1` does not increment downloads.


## Quick start

1. Install

   ```bash
   python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
   ```

2. Open the local UI (loopback only, no CDN, no telemetry)

   ```bash
   clce ui
   ```

   Then open http://127.0.0.1:8845

3. Fill the four boxes (or click **Fill sample**) and press **Score**.

   Empty boxes are OK. Switch **Simple / Advanced** to see Jaccard and types A–D.
   Import JSON/txt `{r,d,p,n}`. Export a report JSON plus a human `.txt` receipt
   with the sha256 of the inputs.

Counted download: [https://azclce-download-tracker.vibelock.workers.dev/](https://azclce-download-tracker.vibelock.workers.dev/)

Direct tarball (also counted): [az-clce-0.3.0.tar.gz](https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.3.0.tar.gz)

GitHub: [https://github.com/AzielEliab/az-clce](https://github.com/AzielEliab/az-clce)

Self-check: `clce doctor`. Debug: `CLCE_DEBUG=1 clce score --r "a" --d "a" --p "a"`.
Transfer verify: `clce verify-transfer PATH` and `spre verify-transfer PATH`.

---

## Honest scope

- CLCE detects **inconsistency, not intent**. Type D is a label, not a finding of malice.
- SPRE scores **structural similarity** to historically confirmed failures. Never guilt or conspiracy.
- Official narrative is **not evidence**. Official-only stories lower E and raise poison-suspicion flags.
- Human validation required.
- Not a cybersecurity exploit, not a scanner of other people's systems, not a lie detector.
- Advisory scores only. Threshold 0.7 is the paper's "acceptable" line, not a pass/fail of truth.
- Loopback UI, no CDN, no telemetry. Size limits on inputs. Empty fields are OK.
- Standalone from ForgeReceipts, ZionPattern, DecisionGATE, AZ-OS, Glossa Filter, MirageGrid.
- Not a VPN. AzielTether is a software queue, not MirageGrid.

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

Kid-plain result (Simple view): a sixth-grade sentence. Advanced view: Jaccard numbers and types A–D.

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
clce doctor                                      # self-check, no network
clce ui                                          # 127.0.0.1:8845 loopback only
clce score --r "..." --d "..." --p "..." [--n "..."]
clce score --import layers.json --export report.json
clce classify --r ... --d ... --p ... [--n ...]
clce gate --min 0.7 --r ... --d ... --p ...      # exit 0 if triple ≥ min else 1
clce verify-transfer PATH                        # structure + SPRE/CLCE rescore JSON
spre score --official "..." --physics "..." --json
spre verify-transfer PATH
```

`--import` reads JSON or labeled `.txt` `{r,d,p,n}`. `--export` writes the report
JSON and a sibling `.txt` receipt with `input_sha256`. `--json` prints the full
report. `--help` lists `ui`, `doctor`, and `version`. `CLCE_DEBUG=1` logs tokens
and scores to stderr.

## Library

```python
from clce import score, classify, gate

report = score(
    r="login button blue",
    d="login form submits",
    p="login button submits",
)
print(report.triple, report.pairwise_avg, report.plus, report.band)
print(report.kid_plain, report.input_sha256)
print(classify(r="...", d="...", p="...", n="csrf session").types)
ok, report = gate(r="a", d="a", p="a", min_score=0.7)
```

## UI

`clce ui` binds **127.0.0.1:8845** only. Four boxes:

- What it looks like (R)
- What they wrote (D)
- What it actually does (P)
- Missing pieces (N)

Giant Score, kid-plain result, Fill sample, Simple/Advanced (Jaccard, types A–D).
Import JSON/txt. Export report JSON + human receipt. Limitation banner.
Self-contained CSS, no CDN, no telemetry. Dark matte / gold.

## iPhone & Android

Flutter sources: [`mobile/`](mobile/). Application id `com.azieeliab.azclce`.
Offline. No analytics. Dark matte / gold.

Four fields with the same kid-plain labels, giant score, sample fill, paste
import / copy export of JSON + receipt text.

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
Keeps A–D fixtures. Adds import/export roundtrip and `clce doctor`.

## Worker

Isolated download counter for this project only. Worker
`azclce-download-tracker`, project `azclce`, KV `AZCLCE_DOWNLOADS` bound as
`DOWNLOADS`. GET `/download` **serves** `az-clce-0.3.0.tar.gz` (does not 302
to GitHub). See [workers/download-tracker/README.md](workers/download-tracker/README.md).

Counted downloads (number on the button, no user reporting):
[https://azclce-download-tracker.vibelock.workers.dev/](https://azclce-download-tracker.vibelock.workers.dev/)

## Layout

```
clce/                 library (engine, cli, ui, io, doctor, transfer, mesh)
spre/                 SPRE sibling package (SP(c), SSI, PC)
clce/web/             loopback UI
tests/                pytest
docs/whitepaper.md    spec
docs/spre.md          SPRE framework
docs/node-mesh.md     AzielTether hooks (not a VPN)
docs/ingest-hooks.md  upload/download verify + Worker ingest
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
- `POST https://azclce-download-tracker.vibelock.workers.dev/v1/spre` SPRE case JSON
- `POST https://azclce-download-tracker.vibelock.workers.dev/v1/verify-transfer` ingest hook
- OpenAPI 3.1: https://azclce-download-tracker.vibelock.workers.dev/openapi.json
- Help: https://azclce-download-tracker.vibelock.workers.dev/ai

`/v1` does not increment the download counter.

One-URL catalog: https://aziel-runtime.vibelock.workers.dev/openapi.json


## Use with Grok / ChatGPT / Venice

Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
This Worker skill: https://azclce-download-tracker.vibelock.workers.dev/v1/skill
This Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json

Grok: import the catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions (no auth). Venice: HTTP tools. Always send `User-Agent: Mozilla/5.0`.

## Cite this

Aziel Eliab. AZ-CLCE + SPRE. https://github.com/AzielEliab/az-clce. https://azclce-download-tracker.vibelock.workers.dev.

- Catalog: https://aziel-runtime.vibelock.workers.dev/
- Worker homepage: https://azclce-download-tracker.vibelock.workers.dev/
- Counted download (gzip HTTP 200, no 302): https://azclce-download-tracker.vibelock.workers.dev/download
- GitHub: https://github.com/AzielEliab/az-clce
- Citation JSON: https://azclce-download-tracker.vibelock.workers.dev/cite.json

## License

Apache-2.0. See [LICENSE](LICENSE).

Forks are welcome and always allowed.
