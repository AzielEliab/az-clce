# AZ-CLCE

**Cross-Layer Consistency Engine (CLCE)**

Aziel Eliab
2026
License: Apache-2.0

> CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice.

This document is the specification implemented by the `az-clce` Python
package (CLI `clce` / `spre`), version 0.3.0. Source papers in `docs/source/`
are shipped here as **Aziel Eliab**. Forks are welcome and always allowed.

SPRE (see [spre.md](spre.md)) is a sibling scorer: structural similarity
only. Official narrative is not evidence. Never guilt. SPRE and CLCE are
two of three triad verifiers; PhysLing lives in aziel-corpus
([triad.md](triad.md)).

This product is standalone. It is not ForgeReceipts. It is not
ZionPattern Solver. It is not DecisionGATE. It is not AZ-OS. It is not
Glossa Filter. It is not merged into those trees.

---

## Abstract

The Cross-Layer Consistency Engine (CLCE) formalizes mismatch detection
across representation, description, and reality layers. It transforms
intuitive analysis into a structured, repeatable system applicable
across engineering, documentation QA, and system validation.

## Core principle

All systems can be evaluated across three primary layers:

- **R — Representation** (visuals, diagrams, UI)
- **D — Description** (text, instructions, claims)
- **P — Reality** (physical or functional truth)

Consistency exists when all three align.

## Mathematical model

Layers are represented as normalized token sets (lowercase, split on
non-alphanumeric characters).

**Jaccard triple**

```
score = |R ∩ D ∩ P| / |R ∪ D ∪ P|
```

Empty-all → 1.0. Empty union with some tokens → 0.0.

**Score interpretation**

- 1.0 = perfect alignment
- ≥0.7 = acceptable
- <0.7 = structural inconsistency

Threshold 0.7 is the paper's "acceptable" line, not a pass/fail of truth.

## Operational process

1. Extract layers (R, D, P)
2. Define expected alignment (optional N = missing expected tokens)
3. Run mismatch scan (R↔D, D↔P, R↔P)
4. Classify result

## Scoring model (Section 5)

Pairwise Jaccard:

- R↔D (0–1)
- D↔P (0–1)
- R↔P (0–1)

Final (pairwise) = average of the three.

The implementation reports **both** the triple score and this pairwise
average. CLI `gate` uses the triple score.

## Negative space extension (CLCE+)

N = missing expected elements.

```
CLCE+ = |R ∩ D ∩ P| / (|R ∪ D ∪ P| + |N|)
```

Higher N reduces the plus score, signaling hidden gaps.

## Mismatch classification

Deterministic. Prefer the most severe matching type (D > C > B > A);
include all matching types in the report.

### Type A — Surface Error

R↔D low (<0.7) while D↔P and R↔P are higher. Docs/UI disagree; function
is closer to one layer.

### Type B — Functional Error

R↔D high (≥0.7) while D↔P or R↔P is low. Pretty alignment, function
diverges.

### Type C — Structural Gap

High |N| relative to the union (`|N| / max(|union|, 1) ≥ 0.5`), or all
pairwise mediocre (each <0.7) and the triple score <0.7.

### Type D — Intentional Obfuscation (LABEL ONLY)

High N AND D↔P very low (<0.3) AND R↔D high (≥0.7): representation
matches description while reality and missing-elements diverge.

**Never claim you proved intent.** Type D is a label, not a finding of
malice. Human validation required.

## Applications

- Engineering validation of one's own systems
- Technical documentation QA
- Product/system debugging
- Structured analysis of representation vs description vs function

Not a cybersecurity exploit. Not a scanner of other people's systems.
Not a lie detector.

## Limitations

CLCE detects inconsistency, not intent. Interpretation requires human
validation. Scores are advisory. The local UI binds loopback only
(127.0.0.1:8845). No CDN. No telemetry.

## Conclusion

CLCE enables consistent detection of structural misalignment across
layers, converting intuitive pattern recognition into a testable
analytical tool. Advisory only.

Forks are welcome and always allowed.
