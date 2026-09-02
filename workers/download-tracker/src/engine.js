/**
 * AZ-CLCE engine (Worker port of clce/engine.py).
 *
 * CLCE detects inconsistency, not intent. Type D is a label, not a
 * finding of malice. Advisory scores only. Threshold 0.7 is the paper's
 * acceptable line, not a pass/fail of truth.
 */
export const THRESHOLD = 0.7;
export const VERY_LOW = 0.3;
export const HIGH_N_RATIO = 0.5;

export const TYPE_LABELS = {
  A: "Surface Error",
  B: "Functional Error",
  C: "Structural Gap",
  D: "Intentional Obfuscation (label only)",
};

export const TYPE_NOTES = {
  A: "R↔D is low while D↔P and R↔P are higher: docs/UI disagree; function is closer to one layer.",
  B: "R↔D is high while D↔P or R↔P is low: pretty alignment, function diverges.",
  C: "High |N| relative to the union, or all pairwise mediocre and the triple score is below 0.7.",
  D: "LABEL ONLY. High N and D↔P very low and R↔D high: representation matches description while reality and missing-elements diverge. CLCE detects inconsistency, not intent. This is not a finding of malice.",
};


export const MAX_FIELD_CHARS = 64 * 1024;
export const ENGINE_VERSION = "0.2.0";

export const KID_PLAIN_BAND = {
  perfect: "These three stories match. What it looks like, what they wrote, and what it actually does use the same words.",
  acceptable: "These stories are close enough. A grown-up should still check, because close is not the same as perfect.",
  structural_inconsistency: "These stories do not match. The picture, the writing, and the real thing are talking about different stuff.",
};

export const KID_PLAIN_TYPES = {
  A: "The picture and the writing do not match, but the real thing is closer to one of them.",
  B: "The picture and the writing match, but the real thing is different.",
  C: "Important pieces are missing, or none of the three stories really agree.",
  D: "LABEL ONLY. The picture matches the writing, but the real thing is very different and lots of pieces are missing. This does not mean anyone was trying to trick you. CLCE finds mismatches, not motives.",
};

function checkField(name, value) {
  const text = value == null ? "" : String(value);
  if (text.length > MAX_FIELD_CHARS) {
    const err = new Error(name + " exceeds size limit (" + text.length + " > " + MAX_FIELD_CHARS + " characters)");
    err.code = "SIZE_LIMIT";
    throw err;
  }
  return text;
}

function kidPlainText(bandName, types) {
  const parts = [KID_PLAIN_BAND[bandName] || KID_PLAIN_BAND.structural_inconsistency];
  if (types && types.length) {
    for (const code of types) {
      if (KID_PLAIN_TYPES[code]) parts.push("Type " + code + ": " + KID_PLAIN_TYPES[code]);
    }
  } else {
    parts.push("No mismatch type matched. A grown-up should still check.");
  }
  parts.push("CLCE detects inconsistency, not intent. Type D is a label only.");
  return parts.join(" ");
}

export const LIMITATION =
  "CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. Human validation required. Not a cybersecurity exploit, not a scanner of other people's systems, not a lie detector. Advisory scores only. Threshold 0.7 is the paper's acceptable line, not a pass/fail of truth.";

function tokenize(text) {
  if (text == null) return new Set();
  const src = typeof text === "string" ? text : Array.isArray(text) ? text.join(" ") : String(text);
  const out = new Set();
  for (const tok of src.toLowerCase().split(/[^a-z0-9]+/)) {
    if (tok) out.add(tok);
  }
  return out;
}

function tokensFrom(value) {
  if (Array.isArray(value)) {
    const out = new Set();
    for (const v of value) {
      if (v == null || v === "") continue;
      String(v)
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .forEach((tok) => {
          if (tok) out.add(tok);
        });
    }
    return out;
  }
  return tokenize(value);
}

function jaccard(...groups) {
  const sets = groups.map((g) => (g instanceof Set ? g : new Set(g || [])));
  if (!sets.some((s) => s.size)) return 1.0;
  const union = new Set();
  for (const s of sets) for (const x of s) union.add(x);
  if (!union.size) return 1.0;
  let inter = new Set(sets[0]);
  for (const s of sets.slice(1)) {
    inter = new Set([...inter].filter((x) => s.has(x)));
  }
  return inter.size / union.size;
}

function sorted(tokens) {
  return [...tokens].sort();
}

export function band(triple) {
  if (triple >= 1.0 - 1e-12) return "perfect";
  if (triple >= THRESHOLD) return "acceptable";
  return "structural_inconsistency";
}

function plusScore(interTriple, unionSize, nSize) {
  const denom = unionSize + nSize;
  if (denom === 0) return 1.0;
  return interTriple / denom;
}

function nRatio(nSize, unionSize) {
  return nSize / Math.max(unionSize, 1);
}

function matchingTypes(rd, dp, rp, triple, ratio) {
  const highN = ratio >= HIGH_N_RATIO;
  const matched = [];
  if (highN && dp < VERY_LOW && rd >= THRESHOLD) matched.push("D");
  const allMediocre = rd < THRESHOLD && dp < THRESHOLD && rp < THRESHOLD;
  if (highN || (allMediocre && triple < THRESHOLD)) matched.push("C");
  if (rd >= THRESHOLD && (dp < THRESHOLD || rp < THRESHOLD)) matched.push("B");
  if (rd < THRESHOLD && dp > rd && rp > rd) matched.push("A");
  return matched;
}

function layerField(body, names) {
  if (!body || typeof body !== "object") return "";
  for (const n of names) {
    if (body[n] != null) return body[n];
  }
  const layers = body.layers;
  if (layers && typeof layers === "object") {
    for (const n of names) {
      if (layers[n] != null) return layers[n];
    }
  }
  return "";
}

export function parseLayers(body) {
  const r = layerField(body, ["r", "R", "representation"]);
  const d = layerField(body, ["d", "D", "description"]);
  const p = layerField(body, ["p", "P", "reality"]);
  const n = layerField(body, ["n", "N", "negative", "negative_space"]);
  return { r, d, p, n };
}

export function score(r = "", d = "", p = "", n = "") {
  const tr = tokensFrom(r);
  const td = tokensFrom(d);
  const tp = tokensFrom(p);
  const tn = tokensFrom(n);
  const rText = checkField("r", Array.isArray(r) ? r.join(" ") : r == null ? "" : String(r));
  const dText = checkField("d", Array.isArray(d) ? d.join(" ") : d == null ? "" : String(d));
  const pText = checkField("p", Array.isArray(p) ? p.join(" ") : p == null ? "" : String(p));
  const nText = checkField("n", Array.isArray(n) ? n.join(" ") : n == null ? "" : String(n));
  const union = new Set([...tr, ...td, ...tp]);
  const inter = new Set([...tr].filter((x) => td.has(x) && tp.has(x)));
  const triple = jaccard(tr, td, tp);
  const rd = jaccard(tr, td);
  const dp = jaccard(td, tp);
  const rp = jaccard(tr, tp);
  const avg = (rd + dp + rp) / 3.0;
  const plus = plusScore(inter.size, union.size, tn.size);
  const ratio = nRatio(tn.size, union.size);
  const types = matchingTypes(rd, dp, rp, triple, ratio);
  const primary = types.length ? types[0] : null;
  const type_labels = {};
  const type_notes = {};
  for (const code of types) {
    type_labels[code] = TYPE_LABELS[code];
    type_notes[code] = TYPE_NOTES[code];
  }
  return {
    r: rText,
    d: dText,
    p: pText,
    n: nText,
    tokens: { r: sorted(tr), d: sorted(td), p: sorted(tp), n: sorted(tn) },
    triple,
    pairwise: { rd, dp, rp },
    pairwise_avg: avg,
    plus,
    n_ratio: ratio,
    band: band(triple),
    types,
    primary,
    type_labels,
    type_notes,
    kid_plain: kidPlainText(band(triple), types),
    kid_plain_types: Object.fromEntries(types.filter((c) => KID_PLAIN_TYPES[c]).map((c) => [c, KID_PLAIN_TYPES[c]])),
    schema: "az-clce.report.v0.2",
    version: ENGINE_VERSION,
    limitation: LIMITATION,
    threshold: THRESHOLD,
    advisory: true,
  };
}

export function classify(r, d, p, n) {
  return score(r, d, p, n);
}

export function gate(r, d, p, n, minScore = THRESHOLD) {
  const min = Number(minScore);
  const floor = Number.isFinite(min) ? min : THRESHOLD;
  const report = score(r, d, p, n);
  return { passed: report.triple >= floor, min_score: floor, report };
}
