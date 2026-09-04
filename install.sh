#!/usr/bin/env bash
# AZ-CLCE one-click install. Counted download via this project's Worker.
# Usage: curl -fsSL https://azclce-download-tracker.vibelock.workers.dev/install.sh | bash
set -euo pipefail

HOST="${CLCE_HOME_HOST:-https://azclce-download-tracker.vibelock.workers.dev}"
ASSET="${CLCE_HOME_ASSET:-az-clce-0.3.0.tar.gz}"
WORKDIR="${CLCE_HOME:-$HOME/az-clce}"

mkdir -p "$WORKDIR"
cd "$WORKDIR"

echo "Downloading counted tarball from ${HOST}/download (User-Agent Mozilla/5.0)…"
curl -fsSL -A 'Mozilla/5.0' "${HOST}/download?asset=${ASSET}" -o "${ASSET}"

tar -xzf "${ASSET}"
DIR="$(find . -maxdepth 1 -type d -name 'az-clce-*' | head -n 1)"
if [ -n "${DIR}" ]; then
  cd "${DIR}"
fi

python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .

echo
echo "Installed AZ-CLCE."
echo "Run:  clce ui"
echo "Then open http://127.0.0.1:8845  (loopback only)"
echo "Author: Aziel Eliab."
