import * as engine from "./engine.js";
import * as spre from "./spre.js";
import * as transfer from "./transfer.js";
import * as triad from "./triad.js";
import { handleMeshApi, meshOpenApiPaths, meshPointer } from "./mesh.js";
import { citePayload, llmsTxt, peerListHtml } from "./cite.js";
const EXAMPLE_PAYLOAD = {
  "r": "login button blue",
  "d": "login form submits",
  "p": "login button submits"
};

const SKILL_MARKDOWN = "---\nname: AZ-CLCE\ndescription: Use when calling AZ-CLCE or SPRE hosted /v1 or installing the local package. Dual surface: Worker /v1 + catalog MCP. This Worker /v1/mesh/* PROXY to aziel-runtime via AZIEL_RUNTIME. Suite mesh default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity. Does not merge AZCoherence (peer Softwares product, FragGate slug azcoherence) or AKM-TRIAD-1.0 fabric. Author Aziel Eliab.\n---\n\n# AZ-CLCE + SPRE\n\nCLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. SPRE scores structural similarity to historically confirmed failures and never asserts guilt or conspiracy. Official narrative is not evidence. Author: **Aziel Eliab**.\n\n**THIS IS:** a Cross-Layer Consistency Engine (R/D/P Jaccard) plus SPRE (SP(c) = {P1..P5, E, C, T, D}; PC = SSI × E) — two of three Aziel triad verifiers (PhysLing lives in aziel-corpus). Transfer verify and AzielTether queue hooks included.\n\n**THIS IS NOT:** a finding of malice, a guilt or conspiracy verdict, a cybersecurity exploit, a scanner of other people's systems, a truth verdict, or a VPN (not MirageGrid). Hosted `/v1` does not increment downloads or views.\n\nAlways send `User-Agent: Mozilla/5.0`. Cloudflare Workers may 403 an empty agent.\n\n## Call these URLs\n\n- Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- Live skill (this markdown): `GET https://azclce-download-tracker.vibelock.workers.dev/v1/skill`\n- Suite mesh: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/mesh` (PROXY; default OFF; QNS-CD-1.0 cross-map)\n\nOps (do **not** increment downloads or views):\n\n| Method | Path | What |\n|--------|------|------|\n| GET | `/v1/health` | Liveness. Does not increment downloads. |\n| GET | `/v1/skill` | This markdown. Does not increment downloads. |\n| GET | `/v1/example` | Sample CLCE layers. |\n| GET | `/v1/spre/example` | Synthetic SPRE case. Not a real case. |\n| GET | `/v1/mesh` | PROXY suite mesh status. Default OFF. QNM live|locked|isolated. QNS-CD-1.0 cross-map. Never enables. |\n| GET | `/v1/mesh/nodes` | PROXY Live Nodes roster (5-minute presence). |\n| POST | `/v1/mesh/{enable,disable,join,heartbeat,leave,broadcast}` | PROXY. Bearer required to enable. No auto-heal. Anon-broadcast is not a publish path. |\n| GET | `/v1/triad` | Component score schema for corpus merge (0–1 and 0–100). |\n| POST | `/v1/score` | Jaccard triple, pairwise average, CLCE+. Advisory. |\n| POST | `/v1/classify` | Same as score plus mismatch types. Type D is a label only. |\n| POST | `/v1/gate` | Pass iff triple >= min_score. Advisory, not a truth verdict. |\n| POST | `/v1/spre` | SPRE score. Structural similarity only. |\n| POST | `/v1/spre/score` | Alias of `/v1/spre`. |\n| POST | `/v1/verify-transfer` | Ingest hook: verify posted files, rescore SPRE + CLCE. |\n| POST | `/v1/tether-ingest` | Accept a hash-chained queue item. Zero retention. |\n\nGrok: import OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.\n\n## Example\n\n```bash\ncurl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/health\ncurl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/skill\ncurl -s -A 'Mozilla/5.0' https://azclce-download-tracker.vibelock.workers.dev/v1/mesh\ncurl -s -A 'Mozilla/5.0' -X POST https://azclce-download-tracker.vibelock.workers.dev/v1/score \\\n  -H 'content-type: application/json' \\\n  -d '{\"r\":\"login button blue\",\"d\":\"login form submits\",\"p\":\"login button submits\"}'\ncurl -s -A 'Mozilla/5.0' -X POST https://azclce-download-tracker.vibelock.workers.dev/v1/spre \\\n  -H 'content-type: application/json' \\\n  -d '{\"official\":\"The office says the matter is closed.\",\"physics\":\"Independent chemistry disagrees.\"}'\n```\n\n## Local (after one-click install)\n\n```bash\ncurl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash\nclce ui\nclce doctor\nclce verify-transfer PATH\nclce verify-transfer older_payloads/ --backfill --ndjson\nspre score --import case.json\nspre score older_payloads/ --ndjson\nspre verify-transfer PATH\n```\n\nThen open http://127.0.0.1:8845 (loopback only).\n\nCounted download (gzip HTTP 200, no 302): https://azclce-download-tracker.vibelock.workers.dev/download?asset=az-clce-0.3.0.tar.gz\nGitHub: https://github.com/AzielEliab/az-clce\n\n## Catalog + local UI\n\nAuthor: **Aziel Eliab**. Honest scope: Jaccard triple / pairwise / CLCE+ plus SPRE structural similarity. Detects inconsistency, not intent. Never guilt.\n\n- Catalog product: https://aziel-runtime.vibelock.workers.dev/p/azclce/\n- Catalog OpenAPI: https://aziel-runtime.vibelock.workers.dev/openapi.json\n- Catalog MCP: `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n- This Worker skill: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/skill`\n- This Worker OpenAPI: https://azclce-download-tracker.vibelock.workers.dev/openapi.json\n- Sample payload: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/example`\n- Suite mesh: `GET https://azclce-download-tracker.vibelock.workers.dev/v1/mesh` PROXY (default OFF; QNS-CD-1.0 cross-map)\n\nLocal UI: **Import JSON file** (`type=file`) and **Export JSON**. Then `clce doctor`. Worker homepage Live Nodes strip polls `GET /v1/mesh` (default OFF).\n\nGrok: import catalog or Worker OpenAPI as a custom tool. ChatGPT: GPT Actions. Venice: HTTP tools.\n\n## Suite mesh (hosted Live Nodes)\n\nHosted `GET /v1/mesh` and `/v1/mesh/*` PROXY to aziel-runtime (`AZIEL_RUNTIME` / HTTPS fallback). Default OFF. Bearer required to enable. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 (photon QNS1 packet transfer) is a hub cite / Worker mesh cross-map only — local qnsd in https://github.com/AzielEliab/qnm-node; runtime cites in https://github.com/AzielEliab/aziel-runtime; pair custody in https://github.com/AzielEliab/azinterface. Not a Softwares-tab product. No public qnsd proxy. No Node Gate. No auto-heal. Not anonymity. Catalog MCP `mesh_*` + FragGate `slug=mesh`. This is not AzielTether and not a VPN.\n\n## Node mesh (AzielTether)\n\nLocal software tether only. Prefer the central Worker when healthy. Offline, `clce verify-transfer` / `spre verify-transfer` append hash-chained items to `~/.az-clce/tether-queue.jsonl` (scopes `az-clce` and `spre`). AzielTether batches those items and reconciles to central on restore via `POST /v1/tether-ingest`. Not a VPN. Not MirageGrid.\n\n## Triad scores (for aziel-corpus)\n\nSPRE and CLCE emit `triad_component` plus a package `triad` on `verify-transfer`. Unit is **[0, 1]** (`score_100` is the 0–100 twin). PhysLing is an empty slot (`home: aziel-corpus`). Combined `final.score` is the mean of the three **only when all three have verified**. See `docs/triad.md`.\n\nBatch/backfill older payloads:\n\n```bash\nclce verify-transfer older_payloads/ --backfill --ndjson\nspre score older_payloads/ --ndjson\nspre score --import older_payloads/ --backfill\n```\n\n## Peers (do not merge)\n\nAZCoherence is a **peer Softwares product**, a separate product — not this engine. Alternate-triad / second-pass coherence (PASS/FLAG/NEUTRALIZE/REFUSE). FragGate slug `azcoherence` via aziel-runtime.\n\n- Worker: https://azcoherence-download-tracker.vibelock.workers.dev/\n- GitHub: https://github.com/AzielEliab/AZCoherence\n- Catalog: https://aziel-runtime.vibelock.workers.dev/p/azcoherence/\n- FragGate: slug `azcoherence` via `POST https://aziel-runtime.vibelock.workers.dev/mcp`\n\nAKM-TRIAD-1.0 is LIVE fabric memory on aziel-runtime — not a Softwares slug. Not AZCoherence. Do not merge engines. CLCE is not Coherence.\n";
/**
 * AZ-CLCE download tracker (Cloudflare Worker).
 *
 * GET  /download?repo=AzielEliab/az-clce&tag=latest&asset=...
 *      increments KV, serves the tarball via env.ASSETS.fetch
 *      (does not 302 to GitHub)
 * GET  /stats   JSON totals + per-repo + per-branch breakdown
 * POST /event   forks report a download {owner,repo,branch,fork,asset}
 * /v1, /v1/mesh/* do not increment. Suite mesh PROXY via AZIEL_RUNTIME.
 *
 * KV binding DOWNLOADS. Keys: project|owner|repo|branch|fork
 * totalKey() = azclce|__total__
 * CORS *. No secrets in this tree.
 * Isolated counter: Worker azclce-download-tracker, project azclce.
 * Not mixed with any other product.
 */

const PROJECT = "azclce";
const DEFAULT_ASSET = "az-clce-0.3.0.tar.gz";
const DEFAULT_OWNER = "AzielEliab";
const DEFAULT_REPO = "az-clce";
const DEFAULT_BRANCH = "main";
const HOST = "https://azclce-download-tracker.vibelock.workers.dev";
const GITHUB_REPO = "https://github.com/AzielEliab/az-clce";

const GITHUB_RELEASES = "https://github.com/AzielEliab/az-clce/releases";
const GITHUB_LATEST = "https://github.com/AzielEliab/az-clce/releases/latest";
const INSTALL_LINE = "curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, HEAD, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, X-Aziel-Runtime-Token, User-Agent",
  };
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...corsHeaders() },
  });
}

function redirect(url) {
  return new Response(null, {
    status: 302,
    headers: { Location: url, ...corsHeaders() },
  });
}

function splitOwnerRepo(value, fallbackOwner, fallbackRepo) {
  if (typeof value === "string" && value.includes("/")) {
    const [o, r] = value.split("/").filter(Boolean);
    if (o && r) return { owner: o, repo: r };
  }
  return { owner: fallbackOwner, repo: fallbackRepo };
}

function parseDims(src) {
  const get = (k) => {
    if (src == null) return null;
    if (typeof src.get === "function") {
      const v = src.get(k);
      return v == null || v === "" ? null : v;
    }
    const v = src[k];
    return v == null || v === "" ? null : v;
  };

  let owner = get("owner") || DEFAULT_OWNER;
  let repo = get("repo") || DEFAULT_REPO;
  if (typeof repo === "string" && repo.includes("/")) {
    const split = splitOwnerRepo(repo, owner, DEFAULT_REPO);
    owner = split.owner;
    repo = split.repo;
  }

  const branch = get("branch") || DEFAULT_BRANCH;
  const tag = get("tag") || "latest";
  const asset = get("asset") || "";

  const forkRaw = get("fork");
  let fork = "0";
  if (forkRaw === 1 || forkRaw === true || forkRaw === "1" || forkRaw === "true") {
    fork = "1";
  } else if (typeof forkRaw === "string" && forkRaw.includes("/")) {
    const split = splitOwnerRepo(forkRaw, owner, repo);
    owner = split.owner;
    repo = split.repo;
    fork = "1";
  } else if (forkRaw != null && forkRaw !== 0 && forkRaw !== false && forkRaw !== "0" && forkRaw !== "false") {
    fork = "1";
  }

  if (`${owner}/${repo}`.toLowerCase() !== `${DEFAULT_OWNER}/${DEFAULT_REPO}`.toLowerCase()) {
    fork = "1";
  }

  return { project: PROJECT, owner, repo, branch, fork, tag, asset };
}

function kvKey(dims) {
  return `${dims.project}|${dims.owner}|${dims.repo}|${dims.branch}|${dims.fork}`;
}

function githubAssetUrl(owner, repo, tag, asset) {
  if (!asset) {
    if (owner === DEFAULT_OWNER && repo === DEFAULT_REPO) return GITHUB_RELEASES;
    return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases`;
  }
  if (!tag || tag === "latest") {
    return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases/latest/download/${encodeURIComponent(asset)}`;
  }
  return `https://github.com/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/releases/download/${encodeURIComponent(tag)}/${encodeURIComponent(asset)}`;
}

function totalKey() {
  return PROJECT + "|__total__";
}

async function increment(env, dims) {
  const key = kvKey(dims);
  const n = parseInt((await env.DOWNLOADS.get(key)) || "0", 10) + 1;
  await env.DOWNLOADS.put(key, String(n));
  const tot = parseInt((await env.DOWNLOADS.get(totalKey())) || "0", 10) + 1;
  await env.DOWNLOADS.put(totalKey(), String(tot));
  return tot;
}

async function listAllKeys(env) {
  const keys = [];
  let cursor;
  do {
    const page = await env.DOWNLOADS.list(cursor ? { cursor } : {});
    keys.push(...page.keys);
    cursor = page.list_complete ? undefined : page.cursor;
  } while (cursor);
  return keys;
}

async function collectStats(env) {
  const keys = await listAllKeys(env);
  let total = 0;
  const by_repo = {};
  const by_branch = {};
  const by_fork = { "0": 0, "1": 0 };
  const breakdown = [];

  for (const k of keys) {
    const name = k.name;
    if (name === viewsKey() || name === totalKey() || name === githubCacheKey()) continue;
    const n = parseInt((await env.DOWNLOADS.get(name)) || "0", 10);
    if (!Number.isFinite(n) || n <= 0) continue;
    const parts = name.split("|");
    if (parts.length < 5) continue;
    const [project, owner, repo, branch, fork] = parts;
    total += n;
    const repoId = `${owner}/${repo}`;
    by_repo[repoId] = (by_repo[repoId] || 0) + n;
    by_branch[branch] = (by_branch[branch] || 0) + n;
    const forkFlag = fork === "1" ? "1" : "0";
    by_fork[forkFlag] = (by_fork[forkFlag] || 0) + n;
    breakdown.push({ project, owner, repo, branch, fork: forkFlag, count: n });
  }

  const totalDirect = parseInt((await env.DOWNLOADS.get(totalKey())) || "0", 10);
  const shown = Number.isFinite(totalDirect) && totalDirect > 0 ? totalDirect : total;
  return {
    project: PROJECT,
    total: shown,
    views: parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) || 0,
    downloads: shown,
    by_repo,
    by_branch,
    by_fork,
    breakdown,
    github: (await githubStats(env)),
    note: "Forks identified by GitHub owner/repo. Key layout: project|owner|repo|branch|fork",
  };
}

/** GET /count contract: {project, views, downloads, total}. Does not increment KV. */
function countBody(stats) {
  const views = Number(stats && stats.views) || 0;
  const downloads = Number(stats && (stats.downloads != null ? stats.downloads : stats.total)) || 0;
  const total = Number(stats && stats.total) || 0;
  return { project: PROJECT, views, downloads, total };
}



function viewsKey() {
  return PROJECT + "|__views__";
}

function githubCacheKey() {
  return PROJECT + "|__github__";
}

async function incrementViews(env) {
  const n = parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) + 1;
  await env.DOWNLOADS.put(viewsKey(), String(n));
  return n;
}

async function githubStats(env) {
  const cached = await env.DOWNLOADS.get(githubCacheKey());
  if (cached) {
    try {
      const obj = JSON.parse(cached);
      if (obj && obj.fetched_at && Date.now() - obj.fetched_at < 5 * 60 * 1000) {
        return obj;
      }
    } catch {
      /* ignore */
    }
  }
  const headers = { "User-Agent": "Mozilla/5.0 AZ-CLCE-download-tracker", Accept: "application/vnd.github+json" };
  let stars = 0;
  let forks = 0;
  let watchers = 0;
  let release_download_count = 0;
  try {
    const repoRes = await fetch("https://api.github.com/repos/AzielEliab/az-clce", { headers });
    if (repoRes.ok) {
      const repo = await repoRes.json();
      stars = Number(repo.stargazers_count) || 0;
      forks = Number(repo.forks_count) || 0;
      watchers = Number(repo.subscribers_count != null ? repo.subscribers_count : repo.watchers_count) || 0;
    }
    const relRes = await fetch("https://api.github.com/repos/AzielEliab/az-clce/releases/latest", { headers });
    if (relRes.ok) {
      const rel = await relRes.json();
      const assets = Array.isArray(rel.assets) ? rel.assets : [];
      release_download_count = assets.reduce((s, a) => s + (Number(a.download_count) || 0), 0);
    }
  } catch {
    /* public API; empty is fine */
  }
  const out = { stars, forks, watchers, release_download_count, fetched_at: Date.now() };
  try {
    await env.DOWNLOADS.put(githubCacheKey(), JSON.stringify(out));
  } catch {
    /* ignore */
  }
  return out;
}

function installScript() {
  return `#!/usr/bin/env bash\n# AZ-CLCE one-click install. Counted download via this Worker.\nset -euo pipefail\nHOST="${HOST}"\nASSET="${DEFAULT_ASSET}"\nWORKDIR="\${CLCE_HOME:-\$HOME/az-clce}"\nmkdir -p "\$WORKDIR"\ncd "\$WORKDIR"\necho "Downloading counted tarball from \${HOST}/download (User-Agent Mozilla/5.0)…"\ncurl -fsSL -A 'Mozilla/5.0' "\${HOST}/download?asset=\${ASSET}" -o "\${ASSET}"\ntar -xzf "\${ASSET}"\nDIR=\"\$(find . -maxdepth 1 -type d -name 'az-clce-*' | head -n 1)\"\nif [ -n "\${DIR}" ]; then\n  cd "\${DIR}"\nfi\npython3 -m venv .venv\n. .venv/bin/activate\npython -m pip install -U pip\npython -m pip install -e .\necho\necho "Installed AZ-CLCE."\necho "Run:  clce ui"\necho "Then open http://127.0.0.1:8845  (loopback only)"\necho "Author: Aziel Eliab."\n`;
}

async function serveAsset(request, env, asset, { head = false } = {}) {
  if (!env.ASSETS) {
    return json({ error: "assets binding missing" }, 500);
  }
  const assetUrl = new URL("/" + asset, request.url);
  const assetRes = await env.ASSETS.fetch(new Request(assetUrl, { method: "GET" }));
  if (!assetRes.ok) {
    return json({ error: "asset not hosted", asset, status: assetRes.status }, 404);
  }
  const headers = new Headers();
  headers.set("Content-Type", "application/gzip");
  headers.set("Content-Disposition", 'attachment; filename="' + asset.replaceAll('"', "") + '"');
  headers.set("Cache-Control", "private, no-store");
  const len = assetRes.headers.get("Content-Length");
  if (len) headers.set("Content-Length", len);
  for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
  if (head) {
    return new Response(null, { status: 200, headers });
  }
  return new Response(assetRes.body, { status: 200, headers });
}

async function indexHtml(env) {
  const stats = await collectStats(env);
  const downloads = Number(stats.downloads != null ? stats.downloads : stats.total) || 0;
  const views = parseInt((await env.DOWNLOADS.get(viewsKey())) || "0", 10) || 0;
  const v = views.toLocaleString("en-US");
  const n = downloads.toLocaleString("en-US");
  const breakdown = (stats.breakdown || [])
    .map(
      (b) =>
        `<li><code>${b.owner}/${b.repo}</code> branch <code>${b.branch}</code> fork=${b.fork} → ${b.count}</li>`,
    )
    .join("") || "<li>none yet</li>";
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZ-CLCE — Aziel Eliab</title>
<meta name="description" content="Cross-Layer Consistency Engine by Aziel Eliab that flags inconsistency across representation, description, and reality.">
<meta name="author" content="Aziel Eliab">
<link rel="canonical" href="https://azclce-download-tracker.vibelock.workers.dev/">
<meta property="og:title" content="AZ-CLCE — Aziel Eliab">
<meta property="og:description" content="Cross-Layer Consistency Engine by Aziel Eliab that flags inconsistency across representation, description, and reality.">
<meta property="og:url" content="https://azclce-download-tracker.vibelock.workers.dev/">
<meta property="og:type" content="website">
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "AZ-CLCE",
  "author": {
    "@type": "Person",
    "name": "Aziel Eliab"
  },
  "codeRepository": "https://github.com/AzielEliab/az-clce",
  "downloadUrl": "https://azclce-download-tracker.vibelock.workers.dev/download",
  "license": "https://www.apache.org/licenses/LICENSE-2.0",
  "url": "https://azclce-download-tracker.vibelock.workers.dev/",
  "description": "Cross-Layer Consistency Engine by Aziel Eliab that flags inconsistency across representation, description, and reality."
}
</script>
<!-- gitbaby-seo -->
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 42rem; margin: 3rem auto; padding: 0 1.25rem 4rem; background: #0e1014; color: #e8eaef; }
  h1 { font-size: 1.75rem; margin: 0 0 .35rem; }
  .motto { color: #9aa3b2; margin: 0 0 1.5rem; }
  .card { border: 1px solid #2a3140; border-radius: 12px; padding: 1.25rem 1.35rem; background: #151922; }
  .nums { display: grid; grid-template-columns: 1fr 1fr; gap: .8rem; margin: 0 0 1rem; }
  .count { font-size: 2.2rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { display: block; font-size: .95rem; font-weight: 500; color: #9aa3b2; }
  .kid { font-size: 1.05rem; margin: 0 0 1rem; }
  .btns { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin: 0 0 .85rem; }
  @media (max-width: 520px) { .btns { grid-template-columns: 1fr; } }
  a.btn, button.btn { display: block; width: 100%; box-sizing: border-box; text-align: center; font: inherit; font-size: 1.2rem; font-weight: 750; padding: 1rem 1.1rem; border-radius: 10px; border: 0; cursor: pointer; text-decoration: none; }
  a.btn.primary { background: #e8eaef; color: #0e1014; }
  button.btn.install { background: #c9a227; color: #14110a; }
  button.btn.install.copied { background: #7dcf9a; color: #0e1014; }
  .meta { margin-top: 1.1rem; color: #9aa3b2; font-size: .92rem; }
  .meta a { color: #c9d4ff; }
  .iso { margin-top: .85rem; font-size: .85rem; color: #7d8696; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; margin: 0 0 1.2rem; font-size: .92rem; }
  pre { background: #0e1014; padding: .75rem .9rem; overflow: auto; border-radius: 8px; font-size: .82rem; }
  code { font-size: .88rem; }

  .cite { margin-top: 1.4rem; padding-top: 1rem; border-top: 1px solid #2a3140; }
  .cite h2 { font-size: 1.05rem; margin: 0 0 .4rem; }
  .cite p { color: #c5ccd8; font-size: .95rem; }
  .cite a { color: #c9d4ff; }
  #meshStrip { border: 1px solid #c9a227; border-radius: 12px; padding: .85rem 1rem; background: #151922; margin: 0 0 1.2rem; display: flex; flex-wrap: wrap; align-items: center; gap: .7rem 1rem; font-size: .88rem; color: #9aa3b2; }
  #meshStrip .live { color: #e8eaef; }
  #meshStrip .live b { color: #c9a227; font-size: 1.35rem; margin-right: .35rem; }
  #meshStrip .rollup b { color: #c9a227; }
  #meshStrip button { font: 700 .78rem/1 ui-monospace, Menlo, Consolas, monospace; height: 2rem; padding: 0 .75rem; border-radius: 8px; background: #101010; color: #e8eaef; border: 1px solid #c9a227; cursor: pointer; }
  #meshStrip button:hover { background: #241c0d; color: #c9a227; }
  #meshStrip input { width: 10rem; padding: .4rem .55rem; border: 1px solid #c9a227; border-radius: 8px; background: #0e0e0e; color: #e8eaef; font: inherit; }
  #meshProducts { flex-basis: 100%; margin: 0; }
</style>
<body>
  <h1>AZ-CLCE</h1>
  <p class="motto">Cross-Layer Consistency Engine + SPRE. Inconsistency, not intent. Never guilt. Author Aziel Eliab.</p>
  <p class="banner">CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. Human validation required. Author: Aziel Eliab.</p>
  <div id="meshStrip" aria-label="Suite Live Nodes">
    <div class="live"><b id="meshLiveCount">0</b> Live Nodes</div>
    <div id="meshLine">Suite mesh: off (default). QNM-BUILD-1.0. Not an anonymity network.</div>
    <div class="rollup">live <b id="qnmLive">0</b> · locked <b id="qnmLocked">0</b> · isolated <b id="qnmIsolated">0</b></div>
    <div>No Node Gate · No auto-heal · Aziel Eliab only</div>
    <div>
      <input id="meshBearer" type="text" maxlength="80" placeholder="bearer (required to enable)" aria-label="mesh bearer">
      <button id="meshEnable" type="button" title="Enable suite mesh. Declared bearer required. Default off.">Enable</button>
      <button id="meshDisable" type="button" title="Disable suite mesh (always allowed)">Disable</button>
      <button id="meshJoin" type="button" title="Join as azclce. Refused while mesh is OFF. No auto-join.">Join</button>
      <button id="meshLeave" type="button" title="Leave this node. No auto-heal.">Leave</button>
    </div>
    <p id="meshProducts">Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 · not AnonBroadcast · not AZMail ring · not a Node Gate · no public qnsd proxy</p>
  </div>
  <div class="card">
    <div class="nums">
      <p class="count">${v}<span>Views</span></p>
      <p class="count">${n}<span>Downloads</span></p>
    </div>
    <p class="kid"><strong>Two big buttons.</strong> Download saves the gzip (the Downloads number goes up). One-click install copies a Terminal command. After it finishes, type <code>clce ui</code>.</p>
    <div class="btns">
      <a class="btn primary dl" href="/download?asset=${DEFAULT_ASSET}">Download</a>
      <button type="button" class="btn install" id="install-btn">One-click install</button>
    </div>
    <pre id="install-cmd">curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash</pre>
    <p class="kid">Then run: <code>clce ui</code> and open http://127.0.0.1:8845 (this computer only).</p>
    <p class="meta">The download count ticks on the Download click. The Worker serves the gzip (HTTP 200). No 302 to GitHub. Forks using this same link are counted automatically. ${DEFAULT_ASSET} — ${n} counted.</p>
    <p class="iso">Isolated counter: Worker <code>azclce-download-tracker</code>, project <code>azclce</code>, KV <code>AZCLCE_DOWNLOADS</code>. Not mixed with any other product. /v1 does not increment downloads.</p>
    
    <p class="meta">${peerListHtml()}</p>
    <p class="meta"><a href="/stats">JSON stats</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/v1/skill">Skill</a> · <a href="/llms.txt">llms.txt</a> · <a href="/ai">AI runtime</a> · <a href="${GITHUB_REPO}">GitHub</a> · <a href="${GITHUB_LATEST}">releases</a></p>
    <script>
      (function () {
        var cmd = "curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash";
        var btn = document.getElementById("install-btn");
        var pre = document.getElementById("install-cmd");
        if (!btn) return;
        btn.addEventListener("click", function () {
          function done(ok) {
            btn.textContent = ok ? "Copied! Paste in Terminal, then run clce ui" : "Select the command, copy it, then run clce ui";
            btn.classList.add("copied");
          }
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(cmd).then(function () { done(true); }).catch(function () { done(false); });
          } else {
            done(false);
            if (pre && window.getSelection) {
              var r = document.createRange();
              r.selectNodeContents(pre);
              var sel = window.getSelection();
              sel.removeAllRanges();
              sel.addRange(r);
            }
          }
        });
      })();
      (function () {
        function $(id) { return document.getElementById(id); }
        function meshNum() {
          for (var i = 0; i < arguments.length; i++) {
            var raw = arguments[i];
            if (raw == null || raw === "") continue;
            var n = typeof raw === "number" ? raw : Number(String(raw).replace(/,/g, ""));
            if (Number.isFinite(n) && n >= 0) return Math.floor(n);
          }
          return 0;
        }
        function unwrapMesh(j) {
          if (!j || typeof j !== "object") return {};
          if (j.result && typeof j.result === "object") return Object.assign({}, j, j.result);
          if (j.mesh && typeof j.mesh === "object") return Object.assign({}, j, j.mesh);
          return j;
        }
        function paintMesh(raw) {
          var j = unwrapMesh(raw);
          var on = j.enabled === true || j.enabled === 1 || String(j.status || "").toLowerCase() === "on";
          var r = (j.rollup && typeof j.rollup === "object") ? j.rollup : {};
          var live = on ? meshNum(r.live, j.live_nodes, j.live) : 0;
          var locked = on ? meshNum(r.locked, j.locked_nodes, j.locked) : 0;
          var isolated = on ? meshNum(r.isolated, j.isolated_nodes, j.isolated) : 0;
          $("meshLiveCount").textContent = String(live);
          $("qnmLive").textContent = String(live);
          $("qnmLocked").textContent = String(locked);
          $("qnmIsolated").textContent = String(isolated);
          var line = $("meshLine");
          if (on) line.textContent = "Suite mesh: on · live " + live + " · locked " + locked + " · isolated " + isolated + ". Not an anonymity network.";
          else if (j.status === "unavailable" || (j.ok === false && j.error)) line.textContent = "Suite mesh: off (unavailable). QNM-BUILD-1.0. Not an anonymity network.";
          else line.textContent = "Suite mesh: off (default). QNM-BUILD-1.0. Not an anonymity network.";
          var products = j.products_present || j.products || [];
          var names = Array.isArray(products) ? products.map(function (p) { return typeof p === "string" ? p : (p && (p.product || p.slug)) || ""; }).filter(Boolean) : [];
          var nodes = Array.isArray(j.nodes) ? j.nodes : [];
          var extra = names.length ? " · products " + names.join(", ") : (nodes.length ? " · " + nodes.length + " node labels" : "");
          $("meshProducts").textContent = "Catalog MCP mesh_* · FragGate slug=mesh · /v1/mesh/* PROXY · QNS-CD-1.0 · not AnonBroadcast · not AZMail ring · not a Node Gate · no public qnsd proxy" + extra;
        }
        async function meshGet(path) {
          var r = await fetch(path, { headers: { "user-agent": "Mozilla/5.0", accept: "application/json" } });
          return r.json();
        }
        async function meshPost(path, payload) {
          var r = await fetch(path, { method: "POST", headers: { "content-type": "application/json", "user-agent": "Mozilla/5.0" }, body: JSON.stringify(payload || {}) });
          return r.json();
        }
        async function refreshMesh() {
          try {
            var status = await meshGet("/v1/mesh");
            var merged = status;
            var inner = unwrapMesh(status);
            var on = inner.enabled === true;
            if (on) {
              try {
                var nodes = await meshGet("/v1/mesh/nodes");
                merged = Object.assign({}, inner, unwrapMesh(nodes));
              } catch (e) { /* status is enough */ }
            }
            paintMesh(merged);
            var nodeId = sessionStorage.getItem("azclce_mesh_node");
            if (on && nodeId) {
              try { await meshPost("/v1/mesh/heartbeat", { node_id: nodeId }); } catch (e) { /* no auto-heal */ }
            }
          } catch (e) {
            paintMesh({ ok: false, enabled: false, status: "unavailable", error: "mesh_unavailable" });
          }
        }
        $("meshEnable").onclick = async function () {
          var bearer = ($("meshBearer").value || "").trim();
          paintMesh(await meshPost("/v1/mesh/enable", bearer ? { bearer: bearer } : {}));
          refreshMesh();
        };
        $("meshDisable").onclick = async function () {
          sessionStorage.removeItem("azclce_mesh_node");
          paintMesh(await meshPost("/v1/mesh/disable", {}));
          refreshMesh();
        };
        $("meshJoin").onclick = async function () {
          var j = await meshPost("/v1/mesh/join", { product: "azclce", label: "AZ-CLCE Worker" });
          var inner = unwrapMesh(j);
          var id = inner.node_id || inner.id || (inner.session && inner.session.node_id);
          if (id) sessionStorage.setItem("azclce_mesh_node", String(id));
          paintMesh(j);
          refreshMesh();
        };
        $("meshLeave").onclick = async function () {
          var id = sessionStorage.getItem("azclce_mesh_node");
          if (id) await meshPost("/v1/mesh/leave", { node_id: id });
          sessionStorage.removeItem("azclce_mesh_node");
          refreshMesh();
        };
        window.addEventListener("pagehide", function () {
          var id = sessionStorage.getItem("azclce_mesh_node");
          if (!id || typeof navigator.sendBeacon !== "function") return;
          try { navigator.sendBeacon("/v1/mesh/leave", new Blob([JSON.stringify({ node_id: id })], { type: "application/json" })); } catch (e) { /* leave expires in 5 minutes */ }
        });
        refreshMesh();
        setInterval(refreshMesh, 30000);
        document.addEventListener("visibilitychange", function () { if (!document.hidden) refreshMesh(); });
      })();
    </script>
    <h2>Per repo / branch / fork</h2>
    <ul>${breakdown}</ul>
  </div>

<section class="cite" id="cite">
  <h2>How to cite</h2>
  <p>Aziel Eliab. AZ-CLCE. https://github.com/AzielEliab/az-clce. https://azclce-download-tracker.vibelock.workers.dev.</p>
  <p><a href="https://aziel-runtime.vibelock.workers.dev/">Catalog</a> · <a href="https://github.com/AzielEliab/az-clce">GitHub</a> · <a href="https://azclce-download-tracker.vibelock.workers.dev/download">Download</a> · <a href="https://azclce-download-tracker.vibelock.workers.dev/cite.json">cite.json</a> · <a href="/llms.txt">llms.txt</a></p>
  <p class="meta">${peerListHtml()}</p>
</section>
<!-- /gitbaby-seo -->
</body>
</html>`;
}



function html(body) {
  return new Response(body, {
    headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
  });
}

function originOf(request) {
  try {
    return new URL(request.url).origin;
  } catch {
    return "https://azclce-download-tracker.vibelock.workers.dev";
  }
}

function openapiSpec(request) {
  const origin = originOf(request);
  const layers = {
    type: "object",
    properties: {
      r: { description: "Representation layer (string or token array)" },
      d: { description: "Description layer" },
      p: { description: "Reality / performance layer" },
      n: { description: "Optional negative space" },
    },
  };
  return {
    openapi: "3.1.0",
    info: {
      title: "AZ-CLCE runtime",
      version: "0.3.0",
      summary: "Cross-Layer Consistency Engine + SPRE. Inconsistency, not intent. Never guilt.",
      description: engine.LIMITATION + " Suite mesh /v1/mesh/* PROXY to aziel-runtime (AZIEL_RUNTIME). Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity. Aziel Eliab only.",
    },
    servers: [{ url: origin }],
    paths: {
            "/count": {
        get: {
          operationId: "azclce_count",
          summary: "Isolated counter JSON {project, views, downloads, total}. Does not increment KV.",
          responses: { "200": { description: "{project, views, downloads, total}" } },
        },
      },
      "/v1/example": { get: { operationId: "azclceExample", summary: "Sample JSON payload. Does not increment downloads.", responses: { "200": { description: "OK" } } } },
      "/v1/health": { get: { operationId: "azclce_health", summary: "Liveness. Does not increment download KV.", responses: { "200": { description: "ok" } } } },
      "/v1/skill": { get: { operationId: "azclce_skill", summary: "Return AZ-CLCE skill markdown. Does not increment downloads or views.", responses: { "200": { description: "text/markdown skill body" } } } },
      "/v1/score": {
        post: {
          operationId: "azclce_score",
          summary: "Jaccard triple, pairwise average, CLCE+. Advisory. Threshold 0.7.",
          requestBody: { required: true, content: { "application/json": { schema: layers } } },
          responses: { "200": { description: "report" } },
        },
      },
      "/v1/classify": {
        post: {
          operationId: "azclce_classify",
          summary: "Same as score plus mismatch types. Type D is a label only.",
          requestBody: { required: true, content: { "application/json": { schema: layers } } },
          responses: { "200": { description: "report" } },
        },
      },
      "/v1/gate": {
        post: {
          operationId: "azclce_gate",
          summary: "Pass iff triple ≥ min_score (default 0.7). Advisory, not a truth verdict.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { r: {}, d: {}, p: {}, n: {}, min: {}, min_score: {} } } } } },
          responses: { "200": { description: "passed + report" } },
        },
      },
      "/v1/spre": {
        post: {
          operationId: "azclce_spre",
          summary: "SPRE score. Structural similarity only. Official narrative is not evidence.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object" } } } },
          responses: { "200": { description: "spre report" } },
        },
      },
      "/v1/spre/score": {
        post: {
          operationId: "azclce_spre_score",
          summary: "Alias of /v1/spre.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object" } } } },
          responses: { "200": { description: "spre report" } },
        },
      },
      "/v1/spre/example": { get: { operationId: "azclceSpreExample", summary: "Synthetic SPRE case. Not a real case. Does not increment downloads.", responses: { "200": { description: "OK" } } } },
      "/v1/verify-transfer": {
        post: {
          operationId: "azclce_verify_transfer",
          summary: "Ingest hook: verify posted files, rescore SPRE + CLCE. No KV increment.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object", properties: { direction: {}, files: { type: "array" } } } } } },
          responses: { "200": { description: "transfer report" } },
        },
      },
      "/v1/tether-ingest": {
        post: {
          operationId: "azclce_tether_ingest",
          summary: "Accept a hash-chained AzielTether item. Zero retention. Not a VPN.",
          requestBody: { required: true, content: { "application/json": { schema: { type: "object" } } } },
          responses: { "200": { description: "ack" } },
        },
      },
      ...meshOpenApiPaths(),
      "/v1/triad": { get: { operationId: "azclce_triad", summary: "Triad component score schema for corpus merge (SPRE + CLCE; PhysLing in aziel-corpus).", responses: { "200": { description: "ok" } } } },
    },
  };
}

function aiHelpPage(request) {
  const origin = originOf(request);
  return `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZ-CLCE — AI runtime</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 44rem; margin: 3rem auto; padding: 0 1.25rem; background: #0e1014; color: #e8eaef; }
  a { color: #c9d4ff; }
  code, pre { background: #151922; padding: .15rem .35rem; border-radius: 4px; }
  pre { padding: .85rem 1rem; overflow: auto; }
  .banner { border: 1px solid #5c4a1a; background: #241c0d; color: #f0d78c; padding: .85rem 1rem; border-radius: 8px; }
</style>
<body>
<h1>AZ-CLCE runtime</h1>
<p class="banner">${engine.LIMITATION}</p>
<p>OpenAPI: <a href="${origin}/openapi.json">${origin}/openapi.json</a></p>
<p>Catalog: <a href="https://aziel-runtime.vibelock.workers.dev/">aziel-runtime.vibelock.workers.dev</a> (catalog <code>mesh_*</code> + FragGate <code>slug=mesh</code>).</p>
<p>Suite mesh: <code>GET ${origin}/v1/mesh</code> PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. QNS-CD-1.0 photon QNS1 packet transfer is a hub cite / Worker mesh cross-map only (no public qnsd proxy). No Node Gate. No auto-heal. Not anonymity. Author: Aziel Eliab only.</p>
<pre>curl -X POST ${origin}/v1/score -H 'content-type: application/json' \\
  -d '{"r":"login button blue","d":"login form submits","p":"login button submits"}'
curl -X POST ${origin}/v1/classify -H 'content-type: application/json' \\
  -d '{"r":"...","d":"...","p":"...","n":"csrf session"}'
curl -X POST ${origin}/v1/gate -H 'content-type: application/json' \\
  -d '{"r":"a","d":"a","p":"a","min":0.7}'
</pre>
<p>GET/POST under <code>/v1</code> never increment the download counter.</p>
<p><a href="/openapi.json">openapi.json</a> · <a href="/v1/health">health</a> · <a href="/v1/mesh">/v1/mesh</a> · <a href="/">Downloads</a></p>
</body></html>`;
}


async function inputSha256(r, d, p, n) {
  const canonical = JSON.stringify({ d, n, p, r });
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function layersFrom(body) {
  const { r, d, p, n } = engine.parseLayers(body || {});
  return { r, d, p, n };
}

async function handleRuntime(request, url) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/v1/mesh" || path.startsWith("/v1/mesh/")) return null;
  if (path === "/v1/health" && request.method === "GET") {
    return json({
      ok: true, author: "Aziel Eliab",
      product: "azclce",
      runtime: true,
      kv_increment: false,
      limitation: engine.LIMITATION,
      threshold: engine.THRESHOLD,
      advisory: true,
      version: "0.3.0",
      spre: true,
      mesh: meshPointer(),
    });
  }
  if ((path === "/v1/example" || path === "/v1/example/") && (request.method === "GET" || request.method === "HEAD")) {
    return json({
      ok: true,
      product: "azclce",
      author: "Aziel Eliab",
      example: EXAMPLE_PAYLOAD,
      note: "Sample payload only. Does not increment downloads.",
    });
  }


  if (path === "/v1/skill" && request.method === "GET") {
    return new Response(SKILL_MARKDOWN, {
      status: 200,
      headers: {
        "Content-Type": "text/markdown; charset=utf-8",
        "Cache-Control": "private, no-store",
        "X-KV-Increment": "false",
        "Access-Control-Allow-Origin": "*",
      },
    });
  }

  if (path === "/openapi.json" && request.method === "GET") {
    return json(openapiSpec(request));
  }
  if ((path === "/ai" || url.pathname === "/ai/") && request.method === "GET") {
    return html(aiHelpPage(request));
  }
  if ((path === "/v1/score" || path === "/v1/classify" || path === "/v1/gate") && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required", limitation: engine.LIMITATION }, 400);
    }
    let r, d, p, n;
    try {
      ({ r, d, p, n } = layersFrom(body));
    } catch (err) {
      const status = err && err.code === "SIZE_LIMIT" ? 413 : 400;
      return json({ error: String(err && err.message ? err.message : err), limitation: engine.LIMITATION }, status);
    }
    const digest = await inputSha256(
      Array.isArray(r) ? r.join(" ") : r == null ? "" : String(r),
      Array.isArray(d) ? d.join(" ") : d == null ? "" : String(d),
      Array.isArray(p) ? p.join(" ") : p == null ? "" : String(p),
      Array.isArray(n) ? n.join(" ") : n == null ? "" : String(n),
    );
    if (path === "/v1/gate") {
      const min = body.min_score != null ? body.min_score : body.min;
      const out = engine.gate(r, d, p, n, min);
      if (out && out.report) out.report.input_sha256 = digest;
      out.input_sha256 = digest;
      return json(out);
    }
    const report = engine.score(r, d, p, n);
    report.input_sha256 = digest;
    return json(report);
  }
    if ((path === "/v1/spre/example" || path === "/v1/spre/example/") && (request.method === "GET" || request.method === "HEAD")) {
    return json({
      ok: true,
      product: "spre",
      author: "Aziel Eliab",
      example: spre.EXAMPLE_CASE,
      note: "Synthetic structural example. Not a real case. Does not increment downloads.",
    });
  }

  if ((path === "/v1/triad" || path === "/v1/triad/") && request.method === "GET") {
    return json({
      ok: true,
      author: "Aziel Eliab",
      ...triad.schemaDoc(),
      example: triad.assemble({}),
    });
  }

  if ((path === "/v1/spre" || path === "/v1/spre/" || path === "/v1/spre/score" || path === "/v1/spre/score/") && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required", limitation: spre.LIMITATION }, 400);
    }
    try {
      return json(spre.score(body || {}));
    } catch (err) {
      const status = err && err.code === "SIZE_LIMIT" ? 413 : 400;
      return json({ error: String(err && err.message ? err.message : err), limitation: spre.LIMITATION }, status);
    }
  }

  if ((path === "/v1/verify-transfer" || path === "/v1/verify-transfer/") && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required", limitation: engine.LIMITATION }, 400);
    }
    return json(await transfer.verifyTransfer(body || {}));
  }

  if ((path === "/v1/tether-ingest" || path === "/v1/tether-ingest/") && request.method === "POST") {
    let body;
    try { body = await request.json(); } catch {
      return json({ error: "JSON body required" }, 400);
    }
    const item = body || {};
    const scope = item.scope;
    const okScope = scope === "az-clce" || scope === "spre";
    return json({
      ok: Boolean(okScope && item.hash && item.prev_hash && item.report_hash),
      accepted: Boolean(okScope && item.hash && item.prev_hash && item.report_hash),
      stored: false,
      kv_increment: false,
      scope: okScope ? scope : null,
      note: "Zero retention ingest. Hash-chain item acknowledged only. Not a VPN. Author Aziel Eliab.",
    });
  }

  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "POST /v1/score /v1/classify /v1/gate /v1/spre /v1/verify-transfer GET /v1/mesh", limitation: engine.LIMITATION }, 404);
  }
  return null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const mesh = await handleMeshApi(request, url, env);
    if (mesh) return mesh;

    const runtime = await handleRuntime(request, url);
    if (runtime) return runtime;

    if ((url.pathname === "/install.sh" || url.pathname === "/install.sh/") && request.method === "GET") {
      return new Response(installScript(), {
        status: 200,
        headers: {
          "Content-Type": "text/x-shellscript; charset=utf-8",
          "Cache-Control": "private, no-store",
          ...corsHeaders(),
        },
      });
    }

    if (url.pathname === "/" && request.method === "GET") {
      await incrementViews(env);
      return new Response(await indexHtml(env), {
        headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
      });
    }

    if ((url.pathname === "/count" || url.pathname === "/count/") && request.method === "GET") {
      return json(countBody(await collectStats(env)));
    }

    if (url.pathname === "/stats" && request.method === "GET") {
      return json(await collectStats(env));
    }

    if (url.pathname === "/event" && request.method === "POST") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "JSON body required" }, 400);
      }
      const dims = parseDims(body || {});
      const count = await increment(env, dims);
      return json({
        ok: true,
        key: kvKey(dims),
        count,
        owner: dims.owner,
        repo: dims.repo,
        branch: dims.branch,
        fork: dims.fork,
        asset: dims.asset || null,
      });
    }

    if (url.pathname === "/go" && (request.method === "GET" || request.method === "HEAD")) {
      const dims = parseDims(url.searchParams);
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      if (request.method === "GET") await increment(env, dims);
      return serveAsset(request, env, asset, { head: request.method === "HEAD" });
    }

    if ((url.pathname === "/download" || url.pathname.startsWith("/download/")) && (request.method === "GET" || request.method === "HEAD")) {
      const dims = parseDims(url.searchParams);
      if (!dims.asset && url.pathname.startsWith("/download/")) {
        dims.asset = decodeURIComponent(url.pathname.slice("/download/".length));
      }
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      if (request.method === "GET") await increment(env, dims);
      return serveAsset(request, env, asset, { head: request.method === "HEAD" });
    }


    // gitbaby-seo-routes
    if ((url.pathname === "/robots.txt" || url.pathname === "/robots.txt/") && request.method === "GET") {
      const body = "User-agent: *\nAllow: /\nSitemap: " + HOST + "/sitemap.xml\n";
      return new Response(body, {
        status: 200,
        headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() },
      });
    }
    if ((url.pathname === "/sitemap.xml" || url.pathname === "/sitemap.xml/") && request.method === "GET") {
      const locs = [HOST + "/", HOST + "/download", HOST + "/install.sh", HOST + "/v1/skill", HOST + "/v1/mesh", HOST + "/openapi.json", HOST + "/cite.json", HOST + "/llms.txt", GITHUB_REPO];
      const xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + locs.map((u) => "  <url><loc>" + u + "</loc></url>").join("\n")
        + "\n</urlset>\n";
      return new Response(xml, {
        status: 200,
        headers: { "Content-Type": "application/xml; charset=utf-8", ...corsHeaders() },
      });
    }
    if ((url.pathname === "/cite.json" || url.pathname === "/cite.json/") && request.method === "GET") {
      return json(citePayload());
    }
    if ((url.pathname === "/llms.txt" || url.pathname === "/llms.txt/" || url.pathname === "/ai.txt" || url.pathname === "/ai.txt/") && request.method === "GET") {
      return new Response(llmsTxt(), {
        status: 200,
        headers: { "Content-Type": "text/plain; charset=utf-8", ...corsHeaders() },
      });
    }
    // /gitbaby-seo-routes
    return json({ error: "not found" }, 404);
  },
};
