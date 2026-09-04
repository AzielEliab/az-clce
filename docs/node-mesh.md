# Node-mesh awareness (AzielTether)

Author: **Aziel Eliab**

AZ-CLCE + SPRE integrate with [AzielTether](https://github.com/AzielEliab/azieltether)
as a **software tether**, not a network overlay.

## Rules

1. **Prefer the central Worker** when `GET /v1/health` is ok
   (`https://azclce-download-tracker.vibelock.workers.dev/v1/health`).
2. When central is down, or `CLCE_OFFLINE=1`, score reports append to a
   local hash-chained queue (`~/.az-clce/tether-queue.jsonl`, override
   with `CLCE_TETHER_QUEUE`).
3. Each item has `scope` `az-clce` or `spre`, `prev_hash`, `report_hash`,
   and `hash` (SHA-256 of the canonical item without `hash`).
4. AzielTether batches those items when a downloaded node hits the
   internet, then reconciles back to central via `POST /v1/tether-ingest`.
5. Live public HTTPS boards stay mesh-free. The tether lives in the
   **downloaded software**.
6. **Do not build a VPN.** This is not MirageGrid.

## Local API

```python
from clce.mesh import append_queue, verify_queue, mesh_status

append_queue(report, scope="az-clce")
append_queue(report, scope="spre")
verify_queue()
```

`clce verify-transfer` and `spre verify-transfer` enqueue both scopes
when a SPRE rescore ran.

## Hosted

`GET /v1/mesh` documents the hook. `POST /v1/tether-ingest` accepts one
item, checks the hash fields, and **does not store** the report (zero
retention). `/v1` never increments download KV.
