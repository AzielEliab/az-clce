#!/usr/bin/env bash
# Rebuild the counted Worker tarball (az-clce-VERSION.tar.gz).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="$(python3 - <<'PY'
import pathlib, re
text = pathlib.Path("pyproject.toml").read_text()
print(re.search(r'^version = "([^"]+)"', text, re.M).group(1))
PY
)"
cd "$ROOT"
STAGE="$(mktemp -d)"
NAME="az-clce-${VERSION}"
DEST="${STAGE}/${NAME}"
mkdir -p "$DEST"
# Ship the installable tree, not git or local venvs.
for item in clce spre tests docs examples mobile workers SKILL.md README.md \
  CONTRIBUTING.md LICENSE MANIFEST.in pyproject.toml install.sh scripts; do
  if [ -e "$item" ]; then
    cp -a "$item" "$DEST/"
  fi
done
# Do not nest previous counted gzips inside the new one.
rm -f "$DEST/workers/download-tracker/public/"*.tar.gz
mkdir -p "$ROOT/workers/download-tracker/public"
OUT="$ROOT/workers/download-tracker/public/${NAME}.tar.gz"
tar -C "$STAGE" -czf "$OUT" "$NAME"
rm -rf "$STAGE"
echo "Wrote $OUT"
