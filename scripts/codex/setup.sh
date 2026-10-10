#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."

if [[ "$(uname -s)" != Linux ]]; then
  echo 'Cloud setup requires Linux; use the Windows commands in docs/CODEX_CLOUD.md locally.' >&2
  exit 2
fi
command -v uv >/dev/null || { echo 'Install uv before running Cloud setup.' >&2; exit 2; }
node -e 'if (Number(process.versions.node.split(".")[0]) < 22) throw new Error("Node.js 22 or newer is required")'

if [[ ! -x .venv/bin/python ]]; then
  uv venv --python 3.11 .venv
fi
# The existing tests already import pytest; this installs their test runner.
uv pip install --python .venv/bin/python 'pytest==8.4.2'
npm ci --no-audit --no-fund
bash scripts/codex/check.sh
