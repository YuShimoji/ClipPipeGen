#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.."
project_python="${CLIPPIPEGEN_PYTHON:-.venv/bin/python}"
export PYTHONUTF8=1
if [[ ! -x "$project_python" ]]; then
  echo 'Python environment is missing. Run bash scripts/codex/setup.sh first.' >&2
  exit 2
fi

"$project_python" -B -m src.cli.main --help >/dev/null
"$project_python" -B -m pytest -q \
  tests/test_rights_manifest.py \
  tests/test_edit_pack.py \
  tests/test_transcript.py \
  tests/test_subtitle_generation.py \
  tests/test_private_artifact_transfer.py
npm run smoke
git diff --check
echo 'ClipPipeGen Cloud development checks passed (CLI, fixture tests, GUI structure).'
