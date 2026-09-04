# AZ-CLCE download tracker (Cloudflare Worker)

Counts GitHub-release downloads for AZ-CLCE across the canonical
repository, other branches, and forks. Forks are identified by GitHub
`owner/repo`.

Homepage is an **isolated counter**: the number is on the download
button. Nobody reports a download. The click is the count.

GET `/download` **serves** the tarball via `env.ASSETS.fetch`. It does
not 302 to GitHub. `Cache-Control: private, no-store`.

`totalKey()` = `azclce|__total__`. PROJECT `azclce`. Worker
`azclce-download-tracker`. KV namespace `AZCLCE_DOWNLOADS` bound as
`DOWNLOADS`.

No secrets belong in this directory.

CLCE detects inconsistency, not intent. Type D is a label, not a
finding of malice. Forks are welcome and always allowed.

This worker is AZ-CLCE only. It is not mixed with ForgeReceipts,
ZionPattern Solver, DecisionGATE, AZ-OS, Glossa Filter, StaticClock,
or any other product.

Isolated counter: Worker `azclce-download-tracker`, project `azclce`.

## Bindings

| Binding     | Type | Purpose |
|-------------|------|---------|
| `DOWNLOADS` | KV   | Counters keyed `project|owner|repo|branch|fork` |

KV id in `wrangler.toml`: `ad135ca4a0c64353bc70367869db9936`.
Binding name MUST stay `DOWNLOADS` (not `AZCLCE_DOWNLOADS` — that is
the Cloudflare namespace title).

## Routes

| Method | Path | Behavior |
|--------|------|----------|
| GET | `/` | Isolated homepage: live count on the download button |
| GET | `/download?repo=&tag=&asset=` | Increment KV, serve the asset from `ASSETS` |
| GET | `/count` | JSON `{project, total}` |
| GET | `/stats` | JSON totals plus per-repo and per-branch breakdown |
| POST | `/event` | A fork reports a download |

Tracked asset URL:

```
https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.3.0.tar.gz
```

`POST /v1/spre` and `POST /v1/verify-transfer` are ingest hooks. They
do not increment KV. See [docs/ingest-hooks.md](../../docs/ingest-hooks.md).
Not a VPN.

## CORS

All responses include `Access-Control-Allow-Origin: *`.

`POST /v1/score` `POST /v1/classify` `POST /v1/gate` `POST /v1/spre`
`POST /v1/verify-transfer`. Inconsistency not intent. SPRE never guilt.

## AI runtime (`/v1`)

CORS `*`. `GET /v1/health`, `GET /openapi.json` (OpenAPI 3.1), `GET /ai`.
Routes under `/v1` **do not** increment download KV.

Help page: `/ai`. Combined catalog: https://aziel-runtime.vibelock.workers.dev/
