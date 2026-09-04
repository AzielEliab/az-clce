/**
 * Aziel triad component scores for Worker /v1.
 * SPRE + CLCE here; PhysLing lives in aziel-corpus.
 * Author: Aziel Eliab.
 */

export const SCHEMA_TRIAD = "aziel.triad.v0.3";
export const SCHEMA_COMPONENT = "aziel.triad.component.v0.3";
export const VERIFIERS = ["spre", "clce", "physling"];

function clip01(value) {
  if (value == null || !Number.isFinite(Number(value))) return null;
  const n = Number(value);
  if (n < 0) return 0;
  if (n > 1) return 1;
  return n;
}

function score100(value) {
  const unit = clip01(value);
  if (unit == null) return null;
  return Number((unit * 100).toFixed(4));
}

function base(id, home, verified, score, note, raw) {
  const unit = verified ? clip01(score) : null;
  return {
    schema: SCHEMA_COMPONENT,
    id,
    home,
    verified: Boolean(verified && unit != null),
    score: unit,
    score_100: score100(unit),
    unit: "unit_interval",
    unit_100: "percent_0_100",
    polarity: "higher_is_stronger_verification",
    raw: raw || {},
    note,
  };
}

export function unverified(id) {
  const homes = { spre: "az-clce", clce: "az-clce", physling: "aziel-corpus" };
  const notes = {
    spre: "SPRE has not verified this payload.",
    clce: "CLCE has not verified this payload.",
    physling: "PhysLing lives in aziel-corpus. Empty slot for corpus merge.",
  };
  return base(id, homes[id] || "az-clce", false, null, notes[id] || "", {});
}

export function clceComponent(triple, extra) {
  const x = extra || {};
  return base("clce", "az-clce", true, triple, "CLCE triple on [0, 1]. Higher = more cross-layer consistency. Type D is a label, not malice.", {
    triple,
    plus: x.plus,
    pairwise_avg: x.pairwise_avg,
    band: x.band,
  });
}

export function spreComponent(pc, extra) {
  const x = extra || {};
  return base("spre", "az-clce", true, 1 - Number(pc), "Merge score is 1−PC on [0, 1]. Raw PC is suppression-pattern confidence. Not guilt.", {
    pc,
    ssi: x.ssi,
    e: x.e,
    flags: x.flags || [],
    pc_is_suppression_confidence: true,
    merge_score: "1 - pc",
  });
}

export function assemble(parts) {
  const clce = parts && parts.clce && parts.clce.id === "clce" ? parts.clce : unverified("clce");
  const spre = parts && parts.spre && parts.spre.id === "spre" ? parts.spre : unverified("spre");
  const physling = parts && parts.physling && parts.physling.id === "physling" ? parts.physling : unverified("physling");
  const components = { spre, clce, physling };
  const verified = VERIFIERS.filter((k) => components[k].verified && components[k].score != null);
  const ready = verified.length === 3;
  let finalScore = null;
  if (ready) finalScore = clip01((spre.score + clce.score + physling.score) / 3);
  return {
    schema: SCHEMA_TRIAD,
    author: "Aziel Eliab",
    verifiers: VERIFIERS.slice(),
    physling_home: "aziel-corpus",
    combine_when: "all_three_verified",
    unit: "unit_interval",
    unit_100: "percent_0_100",
    polarity: "higher_is_stronger_verification",
    formula: "final.score = (spre.score + clce.score + physling.score) / 3 when all three verified; else null",
    components,
    final: {
      score: finalScore,
      score_100: score100(finalScore),
      verified_count: verified.length,
      verified,
      ready,
      note: "aziel-corpus / PhysLing fills the physling slot. Combined final is computed only when all three have verified.",
    },
    limitation: "Triad components are advisory. CLCE detects inconsistency, not intent. Type D is a label, not malice. SPRE never asserts guilt. PhysLing lives in aziel-corpus. Official narrative is not evidence. Author: Aziel Eliab.",
    advisory: true,
    asserts_guilt: false,
  };
}

export function clceFromMapping(obj) {
  if (!obj || obj.triple == null) return null;
  const pairwise = obj.pairwise || {};
  let avg = obj.pairwise_avg;
  if (avg == null && pairwise) {
    const vals = ["rd", "dp", "rp"].map((k) => pairwise[k]).filter((v) => v != null);
    avg = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
  }
  return clceComponent(obj.triple, { plus: obj.plus, pairwise_avg: avg, band: obj.band });
}

export function spreFromMapping(obj) {
  if (!obj) return null;
  let pc = obj.pc;
  if (pc == null && obj.sp && obj.ssi != null && obj.sp.e != null) pc = obj.ssi * obj.sp.e;
  if (pc == null) return null;
  return spreComponent(pc, { ssi: obj.ssi, e: obj.sp && obj.sp.e, flags: obj.flags || [] });
}

export function meanComponent(id, parts) {
  const ok = (parts || []).filter((p) => p && p.verified && p.score != null);
  if (!ok.length) return null;
  const avg = ok.reduce((s, p) => s + Number(p.score), 0) / ok.length;
  if (id === "clce") {
    const triples = ok.map((p) => p.raw && p.raw.triple).filter((v) => v != null);
    return clceComponent(triples.length ? triples.reduce((a, b) => a + b, 0) / triples.length : avg);
  }
  if (id === "spre") {
    const pcs = ok.map((p) => p.raw && p.raw.pc).filter((v) => v != null);
    return spreComponent(pcs.length ? pcs.reduce((a, b) => a + b, 0) / pcs.length : 1 - avg);
  }
  return null;
}

export function schemaDoc() {
  return {
    schema: SCHEMA_TRIAD,
    author: "Aziel Eliab",
    verifiers: VERIFIERS.slice(),
    physling_home: "aziel-corpus",
    unit: "unit_interval",
    range: { min: 0, max: 1 },
    unit_100: "percent_0_100",
    range_100: { min: 0, max: 100 },
    polarity: "higher_is_stronger_verification",
    combine_when: "all_three_verified",
    formula: "final.score = (spre.score + clce.score + physling.score) / 3 when all three verified; else null",
    fields: {
      "components.spre.score": "1 − PC (0–1). PC = SSI × E.",
      "components.clce.score": "Jaccard triple (0–1).",
      "components.physling.score": "Filled by aziel-corpus PhysLing (0–1).",
      "final.score": "Mean of the three scores when all verified; else null.",
      "score_100": "score × 100 (display twin).",
    },
  };
}
