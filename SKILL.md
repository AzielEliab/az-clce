---
name: AZ-CLCE
description: Use when calling AZ-CLCE or SPRE hosted /v1 or installing the local package. Author Aziel Eliab.
---

# AZ-CLCE + SPRE

CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. SPRE scores structural similarity to historically confirmed failures and never asserts guilt or conspiracy. Official narrative is not evidence. Author: **Aziel Eliab**.

**THIS IS:** a Cross-Layer Consistency Engine (R/D/P Jaccard) plus SPRE (SP(c) = {P1..P5, E, C, T, D}; PC = SSI × E) — two of three Aziel triad verifiers (PhysLing lives in aziel-corpus). Transfer verify and AzielTether queue hooks included.

**THIS IS NOT:** a finding of malice, a guilt or conspiracy verdict, a cybersecurity exploit, a scanner of other people's systems, a truth verdict, or a VPN (not MirageGrid). Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://azclce-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

| Method | Path | What |
|--------|------|------|
| GET | `/v1/health` | Liveness. Does not increment downloads. |
| GET | `/v1/skill` | This markdown. Does not increment downloads. |
| GET | `/v1/example` | Sample CLCE layers. |
| GET | `/v1/spre/example` | Synthetic SPRE case. Not a real case. |
| GET | `/v1/mesh` | AzielTether hook status (no VPN). |
| GET | `/v1/triad` | Component score schema for corpus merge (0–1 and 0–100). |
| POST | `/v1/score` | Jaccard triple, pairwise average, CLCE+. Advisory. |
| POST | `/v1/classify` | Same as score plus mismatch types. Type D is a label only. |
| POST | `/v1/gate` | Pass iff triple >= min_score. Advisory, not a truth verdict. |
| POST | `/v1/spre` | SPRE score. Structural similarity only. |
| POST | `/v1/spre/score` | Alias of `/v1/spre`. |
| POST | `/v1/verify-transfer` | Ingest hook: verify posted files, rescore SPRE + CLCE. |
| POST | `/v1/tether-ingest` | Accept a hash-chained queue item. Zero retention. |

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' -X POST https://azclce-download-tracker.vibelock.workers.dev/v1/score \
  -H 'content-type: application/json' \
  -d '{"r":"login button blue","d":"login form submits","p":"login button submits"}'
curl -s -A 'Mozilla/5.0' -X POST https://azclce-download-tracker.vibelock.workers.dev/v1/spre \
  -H 'content-type: application/json' \
  -d '{"official":"The office says the matter is closed.","physics":"Independent chemistry disagrees."}'
```

## Local (after one-click install)

```bash
curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash
clce ui
clce doctor
clce verify-transfer PATH
clce verify-transfer older_payloads/ --backfill --ndjson
spre score --import case.json
spre score older_payloads/ --ndjson
spre verify-transfer PATH
```

Then open http://127.0.0.1:8845 (loopback only).

Counted download (gzip HTTP 200, no 302): https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.3.0.tar.gz
GitHub: https://github.com/AzielEliab/az-clce

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Jaccard triple / pairwise / CLCE+ plus SPRE structural similarity. Detects inconsistency, not intent. Never guilt.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/azclce/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `clce doctor`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Node mesh (AzielTether)

Prefer the central Worker when healthy. Offline, `clce verify-transfer` / `spre verify-transfer` append hash-chained items to `~/.az-clce/tether-queue.jsonl` (scopes `az-clce` and `spre`). AzielTether batches those items and reconciles to central on restore. Not a VPN. Not MirageGrid.

## Triad scores (for aziel-corpus)

SPRE and CLCE emit `triad_component` plus a package `triad` on `verify-transfer`. Unit is **[0, 1]** (`score_100` is the 0–100 twin). PhysLing is an empty slot (`home: aziel-corpus`). Combined `final.score` is the mean of the three **only when all three have verified**. See `docs/triad.md`.

Batch/backfill older payloads:

```bash
clce verify-transfer older_payloads/ --backfill --ndjson
spre score older_payloads/ --ndjson
spre score --import older_payloads/ --backfill
```
