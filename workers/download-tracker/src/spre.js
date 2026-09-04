/**
 * SPRE Worker port of spre/engine.py.
 *
 * Structural similarity only. Never guilt or conspiracy.
 * Official narrative is not evidence.
 * Author: Aziel Eliab.
 */
import { jaccardTokens, tokenize } from "./engine.js";

export const ENGINE_VERSION = "0.3.0";
export const SCHEMA_REPORT = "spre.report.v0.3";
export const LIMITATION =
  "SPRE scores structural similarity to historically confirmed failures. It never asserts guilt, conspiracy, or intent. Official narrative is not evidence. Official narrative without independent evidence or physics lowers E and raises poison-suspicion flags. Human validation required. Advisory only. Not a court, not a lie detector, not CLCE Type D (CLCE Type D remains a label, not malice).";

const MIN_VECTOR_NORM = 0.15;
const CUE_FLOOR = 0.4;
const MIN_CUES = 2;
const MIN_TOKENS_FOR_SSI = 24;
const WEAK_CUE_SUM = 0.8;

const DESTROY_TOKENS = new Set([
  "destroyed",
  "incinerated",
  "overwritten",
  "discarded",
  "wiped",
  "shredded",
  "deleted",
  "unexamined",
  "burned",
  "lost",
  "missing",
]);
const DESTROY_PHRASES = [
  "never collected",
  "never filed",
  "tape missing",
  "files burned",
  "evidence lost",
  "body missing",
];
const BLAME_TOKENS = new Set([
  "reckless",
  "crazy",
  "suicide",
  "deserved",
  "noncompliant",
  "resisted",
  "lifestyle",
  "hysterical",
  "uncooperative",
  "junkie",
  "drunk",
  "fault",
  "blamed",
]);
const BLAME_PHRASES = ["brought it on", "brought this on", "their own fault", "asked for it"];
const ERASURE_TOKENS = new Set(["unlogged", "shredded", "unfiled", "redacted", "gap", "gaps", "neverfiled"]);
const ERASURE_PHRASES = [
  "no log",
  "no record",
  "never filed",
  "pages missing",
  "destroyed logs",
  "broken chain",
  "chain of custody broken",
  "custody was broken",
  "custody broken",
];
const LOOP_TOKENS = new Set(["inhouse", "in-house", "attached", "same", "department"]);
const LOOP_PHRASES = [
  "same office",
  "same authority",
  "employed by",
  "in-house",
  "police coroner",
  "department coroner",
];
const AFTER_FACT_PHRASES = ["years later", "after the fact", "later reconstructed", "from memory", "reconstructed later"];

export const TRAINING_CASES = [
  {
    id: "tuskegee-usphs",
    official: "Official health narrative: a treatment study for rural patients under public health supervision.",
    internal: "Internal protocol withheld treatment, tracked untreated disease, and instructed staff not to give the standard cure.",
    physics: "Independent medical review later showed non-treatment was the actual protocol.",
    coroner: "In-house public-health clinicians wrote the medical notes.",
    authority: "The same public-health office both studied and oversaw the men.",
    evidence: ["later independent medical review", "surviving protocol memos after disclosure"],
    destroyed: ["early adverse notes never filed with the families"],
    victim_framing: "Patients were described as noncompliant and lucky to have any care.",
    records: "Key consent and treatment logs were missing or never filed.",
    contemporaneous: "",
    note: "Structural shape only. Not an identification of any new case.",
  },
  {
    id: "cointelpro-church",
    official: "Official narrative: ordinary lawful investigations of threats.",
    internal: "Internal program disrupted lawful groups, used anonymous smears, and hid the program from the stated mission.",
    physics: "",
    coroner: "",
    authority: "The investigating office certified its own legality.",
    evidence: ["Church Committee documentary record"],
    destroyed: ["files shredded when the program was exposed"],
    victim_framing: "Targets were framed as reckless extremists who brought scrutiny on themselves.",
    records: "Paper trail was shredded; contemporaneous logs had gaps.",
    contemporaneous: "",
    note: "Structural shape only. Not an identification of any new case.",
  },
  {
    id: "iran-contra",
    official: "Official narrative: no third-country arms diversion and no extra legal channel.",
    internal: "Internal channel moved arms proceeds off-book and wrote a second story that contradicted the public line.",
    physics: "",
    coroner: "",
    authority: "The same offices that ran the channel also briefed oversight.",
    evidence: ["Tower Commission record", "later contemporaneous notes that survived"],
    destroyed: ["shredded diversion papers", "overwritten message traffic"],
    victim_framing: "",
    records: "Chain of custody on cables was broken; pages were shredded.",
    contemporaneous: "A few contemporaneous notes survived outside the official file.",
    note: "Structural shape only. Not an identification of any new case.",
  },
  {
    id: "flint-water",
    official: "Official narrative: the switched water was safe to drink and met rules.",
    internal: "Internal emails treated resident complaints as overreaction while corrosion control was not applied.",
    physics: "Independent lab chemistry found lead and corrosion far above the official safety claim.",
    coroner: "City and state health offices issued the medical-sounding all-clear.",
    authority: "The same authorities certified the water and investigated complaints.",
    evidence: ["independent university water tests", "resident samples"],
    destroyed: ["early test sets that failed were not kept in the public file"],
    victim_framing: "Residents were called hysterical and told their lifestyle explained the rash.",
    records: "Some early failing tests were unlogged in the public record.",
    contemporaneous: "Resident contemporaneous samples contradicted the later official line.",
    note: "Structural shape only. Not an identification of any new case.",
  },
  {
    id: "thalidomide-regulatory",
    official: "Official narrative: the sedative was safe for pregnant patients.",
    internal: "Internal safety files lacked the expected birth-defect trials and treated the gap as unimportant.",
    physics: "Independent clinical observations later showed a physical harm pattern.",
    coroner: "",
    authority: "The approving office also explained away early harm reports.",
    evidence: ["later independent clinical series"],
    destroyed: ["unexamined adverse reports sat outside the approval file"],
    victim_framing: "Mothers were implied to have other lifestyle causes.",
    records: "Required safety trials were missing from the approval paper trail.",
    contemporaneous: "",
    note: "Structural shape only. Not an identification of any new case.",
  },
];

function clip(v) {
  if (v < 0) return 0;
  if (v > 1) return 1;
  return v;
}

function asList(value) {
  if (value == null) return [];
  if (Array.isArray(value)) return value.filter((v) => v != null && String(v).trim()).map(String);
  const text = String(value).trim();
  return text ? [text] : [];
}

function pick(src, keys) {
  const layers = src && typeof src.layers === "object" ? src.layers : {};
  for (const key of keys) {
    if (src && src[key] != null) return String(src[key]);
    if (layers[key] != null) return String(layers[key]);
  }
  return "";
}

export function parseCase(src) {
  const obj = src && typeof src === "object" ? src : {};
  return {
    official: pick(obj, ["official", "official_narrative", "narrative"]),
    internal: pick(obj, ["internal", "internal_account", "whistle"]),
    physics: pick(obj, ["physics", "physical", "independent_physics"]),
    coroner: pick(obj, ["coroner", "medical", "forensic"]),
    authority: pick(obj, ["authority", "investigator", "investigating_authority"]),
    evidence: asList(obj.evidence || obj.independent_evidence),
    destroyed: asList(obj.destroyed || obj.missing),
    victim_framing: pick(obj, ["victim_framing", "framing", "victim"]),
    records: pick(obj, ["records", "paper_trail", "chain_of_custody"]),
    contemporaneous: pick(obj, ["contemporaneous", "at_the_time"]),
    notes: pick(obj, ["notes", "text", "body"]),
  };
}

function join(parts) {
  return parts.filter(Boolean).join(" ");
}

function hasPhrase(text, phrases) {
  const blob = String(text || "").toLowerCase();
  return phrases.some((p) => blob.includes(p));
}

function tokenHits(text, wanted) {
  let n = 0;
  for (const tok of tokenize(text)) if (wanted.has(tok)) n += 1;
  return n;
}

function independentEvidence(c) {
  const official = tokenize(c.official);
  const kept = [];
  for (const item of c.evidence) {
    const tokens = tokenize(item);
    if (!tokens.size) continue;
    if (official.size && jaccardTokens(tokens, official) >= 0.85) continue;
    kept.push(item);
  }
  if (c.physics.trim()) kept.push(c.physics);
  if (c.internal.trim() && official.size) {
    if (jaccardTokens(tokenize(c.internal), official) < 0.7) kept.push(c.internal);
  } else if (c.internal.trim() && !official.size) {
    kept.push(c.internal);
  }
  return kept;
}

function scoreP1(c) {
  const flags = [];
  const second = join([c.internal, c.physics, c.contemporaneous]);
  const officialOnly = Boolean(c.official.trim()) && !second.trim();
  if (officialOnly) {
    flags.push("official_narrative_only");
    return { p1: 0.72, flags };
  }
  if (!c.official.trim() || !second.trim()) return { p1: 0, flags };
  const overlap = jaccardTokens(tokenize(c.official), tokenize(second));
  return { p1: clip(1 - overlap), flags };
}

function scoreP2(c) {
  const coroner = c.coroner.trim();
  const authority = c.authority.trim();
  const loopText = join([coroner, authority, c.notes]);
  const phrase = hasPhrase(loopText, LOOP_PHRASES);
  const hits = tokenHits(loopText, LOOP_TOKENS);
  const independentMed = Boolean(c.physics.trim()) || c.evidence.some((item) => {
    const low = item.toLowerCase();
    return low.includes("independent") && (low.includes("medical") || low.includes("hospital") || low.includes("lab") || low.includes("chemistry") || low.includes("clinical"));
  });
  if (coroner && authority) {
    const overlap = jaccardTokens(tokenize(coroner), tokenize(authority));
    let base = 0.35 + 0.5 * overlap;
    if (phrase || hits) base = Math.max(base, 0.7);
    if (independentMed) base *= 0.45;
    return clip(base);
  }
  if (authority && !coroner && (phrase || hits)) return independentMed ? 0.2 : 0.45;
  return 0;
}

function scoreP3(c) {
  const listed = c.destroyed.length;
  const blob = join([c.destroyed.join(" "), c.records, c.notes, c.internal]);
  const hits = tokenHits(blob, DESTROY_TOKENS);
  const phrases = DESTROY_PHRASES.filter((p) => blob.toLowerCase().includes(p)).length;
  if (!listed && !hits && !phrases) return 0;
  const raw = 0.22 * listed + 0.12 * hits + 0.18 * phrases;
  return clip(listed || phrases || hits >= 2 ? Math.min(1, 0.35 + raw) : raw);
}

function scoreP4(c) {
  const framing = join([c.victim_framing, c.official, c.notes]);
  const hits = tokenHits(framing, BLAME_TOKENS);
  const phrases = BLAME_PHRASES.filter((p) => framing.toLowerCase().includes(p)).length;
  if (!hits && !phrases) return 0;
  const support = join([c.physics, c.evidence.join(" ")]);
  const supported = support.trim() && jaccardTokens(tokenize(c.victim_framing), tokenize(support)) >= 0.5;
  let raw = clip(0.28 * hits + 0.35 * phrases + (hits ? 0.25 : 0));
  if (supported) raw *= 0.35;
  return clip(raw);
}

function scoreP5(c) {
  const blob = join([c.records, c.notes, c.destroyed.join(" ")]);
  const hits = tokenHits(blob, ERASURE_TOKENS);
  let phrases = ERASURE_PHRASES.filter((p) => blob.toLowerCase().includes(p)).length;
  const emptyRecords = Boolean(c.official.trim()) && !c.records.trim();
  if (emptyRecords) phrases += 1;
  if (!hits && !phrases && !emptyRecords) return 0;
  const toks = tokenize(blob);
  const custodyBroken = toks.has("chain") && toks.has("custody") && (toks.has("broken") || toks.has("gap") || toks.has("gaps") || toks.has("missing"));
  let raw = 0.2 * hits + 0.22 * phrases + (custodyBroken ? 0.25 : 0);
  if (emptyRecords) raw = Math.max(raw, 0.4);
  return clip(raw);
}

function scoreE(c, officialOnly) {
  const flags = [];
  const independent = independentEvidence(c);
  const physics = Boolean(c.physics.trim());
  let e = 0.12 * Math.min(independent.length, 6);
  if (physics) e += 0.35;
  if (c.contemporaneous.trim()) e += 0.1;
  if (officialOnly || (c.official.trim() && !independent.length && !physics)) {
    flags.push("poison_suspicion");
    e = Math.min(e, 0.22);
  }
  return { e: clip(e), flags };
}

function scoreC(c) {
  let kinds = 0;
  if (c.physics.trim()) kinds += 1;
  if (independentEvidence(c).length) kinds += 1;
  if (c.internal.trim()) kinds += 1;
  if (c.contemporaneous.trim()) kinds += 1;
  return clip(kinds / 4);
}

function scoreT(c) {
  let t = 0;
  if (c.contemporaneous.trim()) t = 0.85;
  else if (c.internal.trim()) t = 0.45;
  else t = c.official.trim() ? 0.15 : 0;
  if (hasPhrase(join([c.official, c.notes, c.records]), AFTER_FACT_PHRASES)) t *= 0.5;
  return clip(t);
}

function scoreD(c) {
  const parts = [
    Boolean(c.records.trim()),
    Boolean(c.physics.trim()),
    Boolean(c.internal.trim()),
    Boolean(independentEvidence(c).length),
    Boolean(c.contemporaneous.trim()),
  ];
  return clip(parts.filter(Boolean).length / 5);
}

function cosine(a, b) {
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let i = 0; i < a.length; i += 1) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  na = Math.sqrt(na);
  nb = Math.sqrt(nb);
  if (na < MIN_VECTOR_NORM || nb < MIN_VECTOR_NORM) return 0;
  return clip(dot / (na * nb));
}

function tokenCount(c) {
  return tokenize(
    join([
      c.official,
      c.internal,
      c.physics,
      c.coroner,
      c.authority,
      c.evidence.join(" "),
      c.destroyed.join(" "),
      c.victim_framing,
      c.records,
      c.contemporaneous,
      c.notes,
    ]),
  ).size;
}

function rawPatterns(c) {
  const p1s = scoreP1(c);
  const officialOnly = p1s.flags.includes("official_narrative_only");
  const e = scoreE(c, officialOnly);
  return {
    sp: {
      p1: p1s.p1,
      p2: scoreP2(c),
      p3: scoreP3(c),
      p4: scoreP4(c),
      p5: scoreP5(c),
      e: e.e,
      c: scoreC(c),
      t: scoreT(c),
      d: scoreD(c),
    },
    flags: [...p1s.flags, ...e.flags],
  };
}

function antiApophenia(ssi, vec, tokens) {
  const cues = vec.filter((x) => x >= CUE_FLOOR).length;
  if (tokens < MIN_TOKENS_FOR_SSI) ssi *= 0.3;
  if (cues < MIN_CUES) ssi *= 0.5;
  if (vec.reduce((a, b) => a + b, 0) < WEAK_CUE_SUM) ssi *= 0.4;
  return clip(ssi);
}

function vectorOf(c) {
  const { sp } = rawPatterns(c);
  return [sp.p1, sp.p2, sp.p3, sp.p4, sp.p5];
}

function nearest(vec) {
  let best = { id: null, similarity: 0, note: "No training shape was close enough to name." };
  for (const proto of TRAINING_CASES) {
    const sim = cosine(vec, vectorOf(parseCase(proto)));
    if (sim > best.similarity) {
      best = {
        id: proto.id,
        similarity: Number(sim.toFixed(6)),
        note: `${proto.note} Testing reports structural similarity only. This is not an identification and not a charge.`,
      };
    }
  }
  return best;
}

function plain(sp, ssi, pc, flags) {
  if (ssi < 0.25 && !flags.length) {
    return "No structural pattern rose above the quiet line. A few matching words are not a pattern. SPRE stays quiet on purpose.";
  }
  const bits = [];
  if (flags.includes("official_narrative_only")) {
    bits.push("Only the official story was given. That story is not treated as evidence.");
  }
  if (flags.includes("poison_suspicion")) {
    bits.push("Independent evidence and physics are thin, so confidence stays low.");
  }
  const labels = { p1: "Two-Story Narrative", p2: "Coroner–Authority Loop", p3: "Evidence Destruction", p4: "Victim-Blame Inversion", p5: "Paper-Trail Erasure" };
  const raised = ["p1", "p2", "p3", "p4", "p5"].filter((k) => sp[k] >= CUE_FLOOR);
  if (raised.length) bits.push("Structural cues that lined up: " + raised.map((k) => labels[k]).join(", ") + ".");
  bits.push(`Similarity to past confirmed failure-shapes is ${ssi.toFixed(2)}. Confidence (similarity times independent evidence) is ${pc.toFixed(2)}.`);
  bits.push("This is a shape match, not a verdict. Nobody is named guilty.");
  return bits.join(" ");
}

export function score(body) {
  const c = parseCase(body || {});
  const { sp, flags } = rawPatterns(c);
  const vec = [sp.p1, sp.p2, sp.p3, sp.p4, sp.p5];
  const near = nearest(vec);
  let ssi = antiApophenia(near.similarity, vec, tokenCount(c));
  if (flags.includes("official_narrative_only")) ssi = Math.min(ssi, 0.55);
  const pc = clip(ssi * sp.e);
  const unique = [...new Set(flags)];
  return {
    schema: SCHEMA_REPORT,
    version: ENGINE_VERSION,
    author: "Aziel Eliab",
    sp,
    labels: {
      p1: "Two-Story Narrative",
      p2: "Coroner–Authority Loop",
      p3: "Evidence Destruction",
      p4: "Victim-Blame Inversion",
      p5: "Paper-Trail Erasure",
    },
    ssi,
    pc,
    flags: unique,
    nearest_training: near,
    plain: plain(sp, ssi, pc, unique),
    kid_plain: plain(sp, ssi, pc, unique),
    limitation: LIMITATION,
    advisory: true,
    asserts_guilt: false,
    asserts_conspiracy: false,
    training_set: "historically_confirmed_failures_only",
    official_narrative_is_evidence: false,
    clce_type_d: "label_only_not_malice",
  };
}

export const EXAMPLE_CASE = {
  official: "The office says the water is safe and the matter is closed.",
  internal: "Internal notes skipped the expected control step and hid failing tests.",
  physics: "Independent lab chemistry found lead far above the official safety claim.",
  evidence: ["independent university water tests"],
  note: "Synthetic structural example. Not a real case. Not a charge.",
};
