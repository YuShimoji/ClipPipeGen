"""Regenerate the content_planning chain outputs from the tracked sample fixture.

Several tests read docs/content_planning/*.json as inputs. Those files are
build outputs of the CPD CLI chain, so they are not tracked; they are rebuilt
here from samples/content_planning/content_candidates_fixture.json.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CPD_DIR = REPO_ROOT / "docs" / "content_planning"
CHAIN = (
    ("build-content-candidate-dashboard", "content_candidates.json"),
    ("build-episode-seed-drafts", "episode_seed_drafts.json"),
    ("resolve-episode-seed-sources", "episode_seed_source_resolution.json"),
    ("build-episode-init-plan", "episode_init_plan.json"),
    ("build-source-inspection-packet", "source_inspection_packet.json"),
    ("build-operator-cockpit", "operator_cockpit.json"),
    ("build-episode-workspace-plan", "episode_workspace_plan.json"),
)


def pytest_sessionstart(session) -> None:
    for command, output in CHAIN:
        if (CPD_DIR / output).exists():
            continue
        subprocess.run(
            [sys.executable, "-m", "src.cli.main", command],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
