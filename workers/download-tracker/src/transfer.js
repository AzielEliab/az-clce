/**
 * Worker ingest hook for transfer verify + rescore.
 * Structure-check posted files, re-run CLCE + SPRE. Does not increment KV.
 * Author: Aziel Eliab.
 */
import * as engine from "./engine.js";
import * as spre from "./spre.js";
import * as triad from "./triad.js";

export const SCHEMA_TRANSFER = "az-clce.transfer.v0.3";
export const MAX_FILES = 32;
export const MAX_FILE_CHARS = 64 * 1024;

function sha256HexSync(text) {
  // Filled by caller with Web Crypto when available; fallback djb for structure-only tests.
  let h = 2166136261;
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return ("00000000" + (h >>> 0).toString(16)).slice(-8);
}

export async function sha256Hex(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function looksSpre(obj) {
  const keys = new Set(Object.keys(obj || {}).map((k) => k.toLowerCase()));
  for (const k of ["official", "official_narrative", "internal", "physics", "coroner", "authority", "victim_framing", "destroyed", "records"]) {
    if (keys.has(k)) return true;
  }
  return obj && (obj.schema === "spre.case.v0.3" || obj.schema === "spre.report.v0.3");
}

function looksClce(obj) {
  const keys = new Set(Object.keys(obj || {}).map((k) => k.toLowerCase()));
  return ["r", "d", "p", "n", "representation", "description", "reality"].some((k) => keys.has(k));
}

function verifyOne(name, text) {
  const issues = [];
  const size = text == null ? 0 : String(text).length;
  if (size > MAX_FILE_CHARS) issues.push("exceeds size limit");
  let parseOk = true;
  let kind = "text";
  const raw = text == null ? "" : String(text);
  if (!raw) {
    kind = "empty";
    issues.push("empty file");
  } else if (raw.trim()[0] === "{" || raw.trim()[0] === "[") {
    kind = "json";
    try {
      JSON.parse(raw);
    } catch (err) {
      parseOk = false;
      issues.push("invalid JSON: " + (err && err.message ? err.message : err));
    }
  }
  return {
    name,
    size,
    kind,
    parse_ok: parseOk,
    issues,
    ok: parseOk && !issues.some((i) => i.includes("exceeds")),
    text: raw,
  };
}

function rescore(structure) {
  const notes = [];
  let clceOut = null;
  let spreOut = null;
  if (!structure.ok) return { clce: null, spre: null, notes: structure.issues };
  const raw = structure.text || "";
  if (structure.kind === "json") {
    let obj;
    try {
      obj = JSON.parse(raw);
    } catch {
      obj = null;
    }
    if (obj && typeof obj === "object" && !Array.isArray(obj)) {
      if (looksClce(obj)) {
        try {
          const layers = engine.parseLayers(obj);
          clceOut = engine.score(layers.r, layers.d, layers.p, layers.n);
        } catch (err) {
          notes.push("CLCE rescore skipped: " + String(err && err.message ? err.message : err));
        }
      }
      if (looksSpre(obj)) {
        spreOut = spre.score(obj);
      }
      if (!clceOut && !spreOut) {
        spreOut = spre.score({ notes: raw.slice(0, MAX_FILE_CHARS) });
        notes.push("unlabeled JSON: SPRE notes-only (anti-apophenia)");
      }
    }
  } else {
    spreOut = spre.score({ notes: raw.slice(0, MAX_FILE_CHARS) });
    notes.push("text: SPRE notes-only");
  }
  if (clceOut) notes.push(engine.LIMITATION);
  if (spreOut) notes.push(spre.LIMITATION);
  return { clce: clceOut, spre: spreOut, notes };
}

export async function verifyTransfer(body) {
  const filesIn = Array.isArray(body && body.files) ? body.files.slice(0, MAX_FILES) : [];
  const direction = (body && body.direction) || "upload";
  if (!filesIn.length) {
    return {
      schema: SCHEMA_TRANSFER,
      version: engine.ENGINE_VERSION,
      author: "Aziel Eliab",
      direction,
      ok: false,
      error: "files array required",
      files: [],
      limitation: engine.LIMITATION,
      ingest_hook: true,
      kv_increment: false,
    };
  }
  const rows = [];
  const clceScores = [];
  const spreScores = [];
  for (const item of filesIn) {
    const name = String((item && (item.name || item.path)) || "unnamed");
    const text = item && item.text != null ? String(item.text) : "";
    const structure = verifyOne(name, text);
    const scored = rescore(structure);
    if (scored.clce) clceScores.push(scored.clce);
    if (scored.spre) spreScores.push(scored.spre);
    const digest = await sha256Hex(text);
    const rowTriad = triad.assemble({
      clce: triad.clceFromMapping(scored.clce),
      spre: triad.spreFromMapping(scored.spre),
    });
    rows.push({
      name,
      size: structure.size,
      sha256: digest,
      kind: structure.kind,
      parse_ok: structure.parse_ok,
      issues: structure.issues,
      ok: structure.ok,
      rescore: { clce: scored.clce, spre: scored.spre, notes: scored.notes },
      triad: rowTriad,
    });
  }
  const packageSha = await sha256Hex(rows.map((r) => r.sha256).sort().join(""));
  const ok = rows.every((r) => r.ok);
  const packageTriad = triad.assemble({
    clce: triad.meanComponent("clce", clceScores.map((s) => triad.clceFromMapping(s))),
    spre: triad.meanComponent("spre", spreScores.map((s) => triad.spreFromMapping(s))),
  });
  return {
    schema: SCHEMA_TRANSFER,
    version: engine.ENGINE_VERSION,
    author: "Aziel Eliab",
    direction,
    ok,
    file_count: rows.length,
    package_sha256: packageSha,
    files: rows,
    triad: packageTriad,
    triad_schema: triad.schemaDoc(),
    rescore: {
      clce_count: clceScores.length,
      spre_count: spreScores.length,
      clce: clceScores.length === 1 ? clceScores[0] : clceScores,
      spre: spreScores.length === 1 ? spreScores[0] : spreScores,
    },
    limitation:
      "Transfer verify checks structure and re-scores. CLCE detects inconsistency, not intent. Type D is a label, not malice. SPRE never asserts guilt or conspiracy. Official narrative is not evidence.",
    ingest_hook: true,
    kv_increment: false,
    advisory: true,
    asserts_guilt: false,
    mesh: "Prefer central Worker when healthy. Offline nodes queue hash-chained reports (scope az-clce / spre) for AzielTether batches. Not a VPN. Not MirageGrid.",
  };
}

export { sha256HexSync };
