# Worker ingest hooks (upload / download)

Author: **Aziel Eliab**

On any sensed **upload** or **download**, re-verify the whole structure
of every file in the transfer package, re-run SPRE + CLCE, and emit a
machine-readable JSON report (`schema: az-clce.transfer.v0.3`).

## Local

```bash
clce verify-transfer PATH          # file, directory, or .tar.gz
spre verify-transfer PATH
clce verify-transfer PATH --direction download
clce verify-transfer PATH --direction upload
```

After a counted Worker download, the install path should run
`clce verify-transfer` on the extracted tree (or the gzip) before use.

## Hosted ingest (`/v1`, no KV increment)

```http
POST /v1/verify-transfer
Content-Type: application/json
User-Agent: Mozilla/5.0
```

```json
{
  "direction": "upload",
  "files": [
    {"name": "layers.json", "text": "{\"r\":\"a\",\"d\":\"a\",\"p\":\"a\"}"}
  ]
}
```

`GET /download` still serves the counted tarball and increments KV.
It does **not** silently rescore the asset on the Worker (that would
mix download counting with analysis). Clients and catalog ingest
call `/v1/verify-transfer` as the hook.

`POST /v1/tether-ingest` accepts a hash-chained queue item from an
offline node. Zero retention.

See [node-mesh.md](node-mesh.md).
