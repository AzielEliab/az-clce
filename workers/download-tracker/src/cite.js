/**
 * AZ-CLCE citation + Softwares peer cross-map.
 * Author: Aziel Eliab only.
 *
 * AZCoherence is a peer Softwares product (separate). Not this engine.
 * AKM-TRIAD-1.0 is fabric memory, not a Softwares slug.
 */

export const AUTHOR = "Aziel Eliab";
export const IDENTITY = "Aziel Eliab only";
export const HOST = "https://azclce-download-tracker.vibelock.workers.dev";
export const GITHUB_REPO = "https://github.com/AzielEliab/az-clce";
export const CATALOG = "https://aziel-runtime.vibelock.workers.dev/";
export const CATALOG_PRODUCT = "https://aziel-runtime.vibelock.workers.dev/p/azclce/";
export const FRAGGATE_SLUG = "azclce";

export const AZCOHERENCE_NAME = "AZCoherence";
export const AZCOHERENCE_SLUG = "azcoherence";
export const AZCOHERENCE_HOST = "https://azcoherence-download-tracker.vibelock.workers.dev";
export const AZCOHERENCE_GITHUB = "https://github.com/AzielEliab/AZCoherence";
export const AZCOHERENCE_CATALOG = "https://aziel-runtime.vibelock.workers.dev/p/azcoherence/";

/** Reciprocal Softwares peer. Separate product. Do not merge engines. CLCE is not Coherence. */
export const AZCOHERENCE_PEER = Object.freeze({
  name: AZCOHERENCE_NAME,
  slug: AZCOHERENCE_SLUG,
  relation: "peer",
  separate_product: true,
  merged: false,
  note: "Peer Softwares product. Alternate-triad / second-pass coherence (PASS/FLAG/NEUTRALIZE/REFUSE). Not AZ-CLCE. Do not merge engines. CLCE is not Coherence.",
  github: AZCOHERENCE_GITHUB,
  worker: AZCOHERENCE_HOST + "/",
  catalog: AZCOHERENCE_CATALOG,
  fraggate_slug: AZCOHERENCE_SLUG,
  fraggate_via: "aziel-runtime",
  mcp: CATALOG + "mcp",
});

export const AKM_TRIAD_FABRIC = Object.freeze({
  name: "AKM-TRIAD-1.0",
  spec: "AKM-TRIAD-1.0",
  relation: "fabric",
  softwares_slug: false,
  note: "LIVE fabric memory on aziel-runtime. Not a Softwares slug. Not AZCoherence. Do not merge.",
});

export const PEERS = Object.freeze({
  azcoherence: AZCOHERENCE_PEER,
  akm_triad: AKM_TRIAD_FABRIC,
});

export function citePayload() {
  return {
    author: AUTHOR,
    title: "AZ-CLCE",
    identity: IDENTITY,
    github: GITHUB_REPO,
    homepage: HOST + "/",
    download: HOST + "/download",
    skill: HOST + "/v1/skill",
    openapi: HOST + "/openapi.json",
    llms: HOST + "/llms.txt",
    doi: null,
    license: "Apache-2.0",
    catalog: CATALOG,
    catalog_product: CATALOG_PRODUCT,
    fraggate_slug: FRAGGATE_SLUG,
    fraggate_via: "aziel-runtime",
    peers: PEERS,
    peer_softwares: [AZCOHERENCE_PEER],
    note: "AZCoherence is a peer Softwares product (separate). FragGate slug azcoherence via aziel-runtime. Do not merge engines. CLCE is not Coherence. AKM-TRIAD-1.0 stays fabric. Identity is Aziel Eliab only.",
  };
}

export function llmsTxt() {
  return `# AZ-CLCE

Author: Aziel Eliab
Identity: Aziel Eliab only
One-line: Cross-Layer Consistency Engine + SPRE. Jaccard triple / pairwise / CLCE+. Detects inconsistency, not intent. Never guilt.
GitHub: ${GITHUB_REPO}
Homepage: ${HOST}/
Download: ${HOST}/download
Install: ${HOST}/install.sh
OpenAPI: ${HOST}/openapi.json
Skill: ${HOST}/v1/skill
Cite: ${HOST}/cite.json
Catalog: ${CATALOG}
Catalog product: ${CATALOG_PRODUCT}
Catalog MCP: ${CATALOG}mcp (FragGate slug ${FRAGGATE_SLUG})
Ops: POST /v1/score, POST /v1/classify, POST /v1/gate, POST /v1/spre, POST /v1/verify-transfer, GET /v1/health, GET /v1/skill, GET /v1/triad, GET /v1/mesh
Suite mesh: GET ${HOST}/v1/mesh PROXY to aziel-runtime. Default OFF. QNM-BUILD-1.0 live|locked|isolated. No Node Gate. No auto-heal. Not anonymity. Catalog MCP mesh_* + FragGate slug=mesh.

Peer Softwares product (separate; do not merge):
- AZCoherence — alternate-triad / second-pass coherence (PASS/FLAG/NEUTRALIZE/REFUSE). Not this engine. CLCE is not Coherence.
- Worker: ${AZCOHERENCE_HOST}/
- GitHub: ${AZCOHERENCE_GITHUB}
- Catalog: ${AZCOHERENCE_CATALOG}
- FragGate slug: ${AZCOHERENCE_SLUG} via aziel-runtime (${CATALOG}mcp)

AKM-TRIAD-1.0 is LIVE fabric memory on aziel-runtime — not a Softwares slug. Not AZCoherence.

Identity: Aziel Eliab only
License: Apache-2.0
Forks: welcome and always allowed
DOI: none invented.

Indexing, metadata scrape, and AI grounding of public pages are allowed.
`;
}

export function peerListHtml() {
  return `Peers (separate Softwares products, do not merge): <a href="${AZCOHERENCE_HOST}/">AZCoherence</a> · Worker <a href="${AZCOHERENCE_HOST}/">${AZCOHERENCE_HOST.replace("https://", "")}</a> · <a href="${AZCOHERENCE_GITHUB}">GitHub</a> · FragGate slug <code>${AZCOHERENCE_SLUG}</code> via <a href="${CATALOG}">aziel-runtime</a> · AKM-TRIAD-1.0 (fabric, not Softwares)`;
}
