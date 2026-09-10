# Node-mesh awareness (AzielTether)

Author: **Aziel Eliab**

AZ-CLCE + SPRE integrate with [AzielTether](https://github.com/AzielEliab/azieltether)
as a **software tether**, not a network overlay.

Hosted suite Live Nodes are a **different door**: `/v1/mesh/*` PROXY to
aziel-runtime (`AZIEL_RUNTIME` / HTTPS fallback). Default OFF. Bearer
required to enable. QNM-BUILD-1.0 public rollup is live|locked|isolated
counts only. QNS-CD-1.0 (photon QNS1 packet transfer) is a hub cite /
Worker mesh cross-map only — local qnsd in
[qnm-node](https://github.com/AzielEliab/qnm-node); runtime cites in
[aziel-runtime](https://github.com/AzielEliab/aziel-runtime); pair
custody in [azinterface](https://github.com/AzielEliab/azinterface).
Not a Softwares-tab product. No public qnsd proxy. No Node Gate. No
auto-heal. Not anonymity. Not AzielTether. Not a VPN. Not MirageGrid.

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

Hosted `GET /v1/mesh` is the suite mesh PROXY (Live Nodes / QNM +
QNS-CD-1.0 cross-map), not this AzielTether hook.
`POST /v1/tether-ingest` accepts one item, checks
the hash fields, and **does not store** the report (zero retention).
`/v1` never increments download KV.
