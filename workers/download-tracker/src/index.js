import * as engine from "./engine.js";
/**
 * AZ-CLCE download tracker (Cloudflare Worker).
 *
 * GET  /download?repo=AzielEliab/az-clce&tag=latest&asset=...
 *      increments KV, serves the tarball via env.ASSETS.fetch
 *      (does not 302 to GitHub)
 * GET  /stats   JSON totals + per-repo + per-branch breakdown
 * POST /event   forks report a download {owner,repo,branch,fork,asset}
 *
 * KV binding DOWNLOADS. Keys: project|owner|repo|branch|fork
 * totalKey() = azclce|__total__
 * CORS *. No secrets in this tree.
 * Isolated counter: Worker azclce-download-tracker, project azclce.
 * Not mixed with any other product.
 */

const PROJECT = "azclce";
const DEFAULT_ASSET = "az-clce-0.1.0.tar.gz";
const DEFAULT_OWNER = "AzielEliab";
const DEFAULT_REPO = "az-clce";
const DEFAULT_BRANCH = "main";
const GITHUB_RELEASES = "https://github.com/AzielEliab/az-clce/releases";
const GITHUB_LATEST = "https://github.com/AzielEliab/az-clce/releases/latest";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
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
    by_repo,
    by_branch,
    by_fork,
    breakdown,
    note: "Forks identified by GitHub owner/repo. Key layout: project|owner|repo|branch|fork",
  };
}

async function indexHtml(env) {
  const stats = await collectStats(env);
  const total = Number(stats.total) || 0;
  const n = total.toLocaleString("en-US");
  const github = (typeof GITHUB_LATEST !== "undefined" && GITHUB_LATEST)
    ? GITHUB_LATEST
    : GITHUB_RELEASES;
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AZ-CLCE downloads</title>
<style>
  :root { color-scheme: dark; }
  body { font: 16px/1.45 system-ui, sans-serif; max-width: 40rem; margin: 3rem auto; padding: 0 1.25rem; background: #0b0b0b; color: #e8e0d0; }
  h1 { font-size: 1.75rem; margin: 0 0 .35rem; color: #c9a227; }
  .motto { color: #c9a227; font-style: italic; margin: 0 0 1.5rem; }
  .card { border: 1px solid #2a261c; border-radius: 12px; padding: 1.25rem 1.35rem; background: #141414; }
  .count { font-size: 2.4rem; font-variant-numeric: tabular-nums; font-weight: 700; margin: 0; }
  .count span { font-size: 1rem; font-weight: 500; color: #8a8070; }
  a.dl { display: inline-block; margin-top: 1rem; background: #c9a227; color: #0b0b0b; text-decoration: none; font-weight: 650; padding: .65rem 1rem; border-radius: 8px; }
  .meta { margin-top: 1.1rem; color: #8a8070; font-size: .92rem; }
  .meta a { color: #c9a227; }
  .iso { margin-top: .85rem; font-size: .85rem; color: #7d8696; }
  .limit { margin-top: .85rem; font-size: .85rem; color: #8a8070; }
</style>
<body>
  <h1>AZ-CLCE</h1>
  <p class="motto">Cross-Layer Consistency Engine. Inconsistency, not intent.</p>
  <div class="card">
    <p class="count">${n}<span> downloads of this project</span></p>
    <a class="dl" href="/download?asset=az-clce-0.1.0.tar.gz">Download az-clce-0.1.0.tar.gz — ${n} counted</a>
    <p class="meta">The count ticks on this click. Nobody reports anything. Forks using this same link are counted automatically.</p>
    <p class="iso">Isolated counter: Worker <code>azclce-download-tracker</code>, project <code>azclce</code>. Not mixed with any other product.</p>
    <p class="limit">CLCE detects inconsistency, not intent. Type D is a label, not a finding of malice. Human validation required. Advisory scores only. Forks welcome and always allowed.</p>
    <p class="meta"><a href="/ai">AI runtime</a> · <a href="/openapi.json">OpenAPI</a> · <a href="/stats">JSON stats</a> · <a href="${github}">GitHub releases</a></p>
  </div>
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
      version: "0.1.0",
      summary: "Cross-Layer Consistency Engine. Inconsistency, not intent.",
      description: engine.LIMITATION,
    },
    servers: [{ url: origin }],
    paths: {
      "/v1/health": { get: { operationId: "azclce_health", summary: "Liveness. Does not increment download KV.", responses: { "200": { description: "ok" } } } },
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
<p>Catalog: <a href="https://aziel-runtime.vibelock.workers.dev/">aziel-runtime.vibelock.workers.dev</a></p>
<pre>curl -X POST ${origin}/v1/score -H 'content-type: application/json' \\
  -d '{"r":"login button blue","d":"login form submits","p":"login button submits"}'
curl -X POST ${origin}/v1/classify -H 'content-type: application/json' \\
  -d '{"r":"...","d":"...","p":"...","n":"csrf session"}'
curl -X POST ${origin}/v1/gate -H 'content-type: application/json' \\
  -d '{"r":"a","d":"a","p":"a","min":0.7}'
</pre>
<p>GET/POST under <code>/v1</code> never increment the download counter.</p>
<p><a href="/">Downloads</a></p>
</body></html>`;
}

function layersFrom(body) {
  const { r, d, p, n } = engine.parseLayers(body || {});
  return { r, d, p, n };
}

async function handleRuntime(request, url) {
  const path = url.pathname.replace(/\/+$/, "") || "/";
  if (path === "/v1/health" && request.method === "GET") {
    return json({
      ok: true,
      product: "azclce",
      runtime: true,
      kv_increment: false,
      limitation: engine.LIMITATION,
      threshold: engine.THRESHOLD,
      advisory: true,
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
    const { r, d, p, n } = layersFrom(body);
    if (path === "/v1/gate") {
      const min = body.min_score != null ? body.min_score : body.min;
      return json(engine.gate(r, d, p, n, min));
    }
    return json(engine.score(r, d, p, n));
  }
  if (path.startsWith("/v1/") || path === "/v1") {
    return json({ error: "not found", hint: "POST /v1/score /v1/classify /v1/gate", limitation: engine.LIMITATION }, 404);
  }
  return null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }

    const runtime = await handleRuntime(request, url);
    if (runtime) return runtime;

    if (url.pathname === "/" && request.method === "GET") {
      return new Response(await indexHtml(env), {
        headers: { "Content-Type": "text/html; charset=utf-8", ...corsHeaders() },
      });
    }

    if (url.pathname === "/count" && request.method === "GET") {
      const stats = await collectStats(env);
      return json({ project: PROJECT, total: stats.total || 0 });
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

    if (url.pathname === "/go" && request.method === "GET") {
      const dims = parseDims(url.searchParams);
      await increment(env, dims);
      const asset = dims.asset || DEFAULT_ASSET;
      return redirect(githubAssetUrl(dims.owner, dims.repo, dims.tag, asset));
    }

    if ((url.pathname === "/download" || url.pathname.startsWith("/download/")) && request.method === "GET") {
      const dims = parseDims(url.searchParams);
      if (!dims.asset && url.pathname.startsWith("/download/")) {
        dims.asset = decodeURIComponent(url.pathname.slice("/download/".length));
      }
      const asset = dims.asset || DEFAULT_ASSET;
      dims.asset = asset;
      await increment(env, dims);
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
      for (const [k, v] of Object.entries(corsHeaders())) headers.set(k, v);
      return new Response(assetRes.body, { status: 200, headers });
    }

    return json({ error: "not found" }, 404);
  },
};
