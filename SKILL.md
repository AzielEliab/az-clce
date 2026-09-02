---
name: AZ-CLCE
description: Use when calling AZ-CLCE hosted /v1 or installing the local package. Author Aziel Eliab.
---

# AZ-CLCE

CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. Human validation required. Author: Aziel Eliab.

**THIS IS:** a Cross-Layer Consistency Engine that scores inconsistency across representation (R), description (D), and reality (P).

**THIS IS NOT:** a finding of malice, a cybersecurity exploit, a scanner of other people's systems, or a truth verdict. Type D is a label only.

Author: **Aziel Eliab**. Forks are welcome and always allowed. Apache-2.0.

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
| POST | `/v1/score` | Jaccard triple, pairwise average, CLCE+. Advisory. |
| POST | `/v1/classify` | Same as score plus mismatch types. Type D is a label only. |
| POST | `/v1/gate` | Pass iff triple >= min_score. Advisory, not a truth verdict. |

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/skill
curl -s -A 'Mozilla/5.0' -X POST https://azclce-download-tracker.vibelock.workers.dev/v1/score \
  -H 'content-type: application/json' \
  -d '{"r":"login button blue","d":"login form submits","p":"login button submits"}'
```

## Local (after one-click install)

```bash
curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash
clce ui
```

Then open http://127.0.0.1:8845 (loopback only).

Counted download (gzip HTTP 200, no 302): https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/az-clce
