# Aziel triad (SPRE + CLCE + PhysLing)

Author: **Aziel Eliab**

Three verifiers. This package ships **two**. The third lives in
[aziel-corpus](https://github.com/AzielEliab/aziel-corpus).

| Verifier | Home | Merge field | Meaning (higher = stronger verification) |
|----------|------|-------------|------------------------------------------|
| SPRE | `az-clce` | `components.spre.score` | `1 − PC` on **[0, 1]** |
| CLCE | `az-clce` | `components.clce.score` | Jaccard triple on **[0, 1]** |
| PhysLing | `aziel-corpus` | `components.physling.score` | Corpus fills this **[0, 1]** slot |

Each component also emits `score_100` (0–100) as a display twin.
Canonical compositing uses **0–1**.

## Combined final score

```
final.score = (spre.score + clce.score + physling.score) / 3
```

**only when all three have `verified: true`.** Otherwise `final.score`
is `null` and `final.ready` is `false`. aziel-corpus forms the combined
score after PhysLing has verified.

Schema: `aziel.triad.v0.3`. Hosted: `GET /v1/triad`.

## Polarity

- CLCE triple high = layers agree (consistency).
- SPRE raw `PC = SSI × E` high = closer to a confirmed-failure **shape**.
  The merge field inverts that (`1 − PC`) so all three components point
  the same way. Raw `pc` / `ssi` / `e` stay in `components.spre.raw`.
- Official narrative is not evidence. Never guilt. Type D is a label.

## CLI (batch / backfill)

Older payloads (v0.2 reports, layer JSON, SPRE cases) can be rescored
in place:

```bash
clce verify-transfer older_payloads/ --backfill
clce verify-transfer older_payloads/ --backfill --ndjson --out triad.jsonl
spre score older_payloads/ --ndjson
spre score --import older_payloads/ --backfill
```

`verify-transfer` already walks a directory. `--backfill` raises the
file cap and keeps triad fields on every record for corpus merge.
