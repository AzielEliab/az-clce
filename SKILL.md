---
name: AZ-CLCE
description: Use when calling AZ-CLCE hosted /v1 or installing the local package. Author Aziel Eliab.
---

# AZ-CLCE

CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. Author: **Aziel Eliab**.

**THIS IS:** a Cross-Layer Consistency Engine that scores inconsistency across representation (R), description (D), and reality (P).

**THIS IS NOT:** a finding of malice, a cybersecurity exploit, a scanner of other people's systems, or a truth verdict. Hosted `/v1` does not increment downloads or views.

Always send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.

## Call these URLs

- Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- Live skill (this markdown): `GET https://azclce-download-tracker.vibelock.workers.dev/v1/skill`

Ops (do **not** increment downloads or views):

- `GET /v1/health` — liveness
- `GET /v1/skill` — this file
- Product POSTs listed in OpenAPI

Grok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.

## Example

```bash
curl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/health
curl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/skill
```

## Local (after one-click install)

```bash
curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash
clce ui
clce doctor
```

Then open http://127.0.0.1:8845 (loopback only).

Counted download (gzip HTTP 200, no 302): https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.2.0.tar.gz
GitHub: https://github.com/AzielEliab/az-clce

## Catalog + local UI

Author: **Aziel Eliab**. Honest scope: Jaccard triple / pairwise / CLCE+. Detects inconsistency, not intent.

- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/azclce/
- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json
- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`
- This Worker skill: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/skill`
- This Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json
- Sample payload: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/example`

Local UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `clce doctor`.

Grok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.
