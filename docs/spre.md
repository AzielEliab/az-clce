# SPRE — Structural Suppression Pattern Recognition Engine

Author: **Aziel Eliab** · 2026 · Apache-2.0 · version 0.3.0

SPRE is a first-class module in the `az-clce` distribution (`spre/`).
It scores **structural similarity** to a training set of historically
confirmed institutional failures. It does not assert guilt, conspiracy,
or intent.

CLCE Type D remains a **label**, not malice. SPRE is a sibling scorer.

## Formula

```
SP(c) = {P1, P2, P3, P4, P5, E, C, T, D}
PC    = SSI × E
```

| Symbol | Meaning |
|--------|---------|
| P1 | Two-Story Narrative — official vs internal/physics. Official-narrative-only is flagged. |
| P2 | Coroner–Authority Loop — circular medical/forensic certification |
| P3 | Evidence Destruction — listed gaps, not a charge |
| P4 | Victim-Blame Inversion — framing without independent support |
| P5 | Paper-Trail Erasure — missing logs / broken chain of custody |
| E | Evidence independence. **Official narrative is never evidence.** |
| C | Coverage of independent source kinds |
| T | Temporal contemporaneity |
| D | Documentation completeness (not CLCE Type D) |
| SSI | Cosine similarity of `{P1..P5}` to training prototypes |
| PC | Pattern confidence = SSI × E |

Official narrative without independent evidence or physics **lowers E**
and raises `official_narrative_only` + `poison_suspicion`.

## Training vs testing

- **Training set** = historically confirmed failures only (government
  acknowledgments / official inquiries). Shapes, not identities.
- **Testing** = structural similarity. Never “this is that case.”
- **Negative controls** (open accident, software login, empty) must stay
  quiet. Anti-apophenia: short text, a single cue, or a near-zero vector
  cannot claim a pattern.

## CLI

```bash
spre score --official "..." --internal "..." --physics "..." --json
spre score --import examples/spre_case.json
spre verify-transfer PATH
```

Hosted: `POST /v1/spre` on the AZ-CLCE Worker. Synthetic example:
`GET /v1/spre/example` — not a real case.

## Honest banner

THIS IS: a structural-similarity engine over confirmed failure-shapes.

THIS IS NOT: a court, a conspiracy detector, a guilt finding, or
permission to treat the official story as proof.
