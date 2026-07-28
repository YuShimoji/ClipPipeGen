from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "docs" / "RUNTIME_STATE.md"
HANDOFF_PATH = ROOT / "docs" / "CURRENT_HANDOFF.md"
ARCHIVE_MARKER = "<!-- HISTORICAL_RUNTIME_ARCHIVE_START -->"
ALIGNED_FIELDS = (
    "current_slice",
    "active_branch",
    "active_artifact",
    "human_entrypoint",
    "portable_entrypoint",
    "local_artifact_role",
    "cross_machine_resume_class",
    "review_status",
    "base_main_revision",
    "implementation_revision",
    "artifact_output_sha256",
    "artifact_package_tree_digest_sha256",
    "artifact_manifest_self_sha256",
    "package_validation_status",
    "full_suite_status",
    "human_review_pending",
    "rights_approval",
    "production_acceptance",
    "public_use",
    "monetized_use",
    "upload_attempted",
    "upstream_parity",
    "remote_code_complete",
    "decision_required",
    "next_review_due",
    "next_action",
)


@dataclass(frozen=True)
class Section:
    title: str
    body: str


def _parse_frontmatter(text: str) -> tuple[dict[str, str], int]:
    text = text.removeprefix("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise AssertionError("resume surface is missing opening frontmatter")

    try:
        closing_index = lines.index("---", 1)
    except ValueError as exc:
        raise AssertionError("resume surface is missing closing frontmatter") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:closing_index]:
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        value = raw_value.strip().strip("\"'")
        metadata[key.strip()] = "" if value == "null" else value

    body_offset = sum(len(line) + 1 for line in lines[: closing_index + 1])
    return metadata, body_offset


def _parse_live_sections(text: str) -> tuple[dict[str, str], list[Section]]:
    text = text.removeprefix("\ufeff")
    if text.count(ARCHIVE_MARKER) != 1:
        raise AssertionError("runtime needs exactly one historical archive marker")

    metadata, body_offset = _parse_frontmatter(text)
    archive_offset = text.index(ARCHIVE_MARKER)
    if archive_offset <= body_offset:
        raise AssertionError("historical archive marker must follow active content")
    active_body = text[body_offset:archive_offset]

    matches = list(re.finditer(r"(?m)^## (?P<title>.+?)\r?$", active_body))
    sections: list[Section] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(active_body)
        sections.append(
            Section(
                title=match.group("title").strip(),
                body=active_body[match.end() : end],
            )
        )
    return metadata, sections


def _semantic_bullets(section: Section) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for match in re.finditer(
        r"(?m)^-\s+(?P<key>[A-Za-z][A-Za-z ]+):\s+"
        r"`?(?P<value>[^`\r\n]+)`?\s*$",
        section.body,
    ):
        key = " ".join(match.group("key").lower().split())
        fields.setdefault(key, []).append(match.group("value").strip())
    return fields


def _authority_errors(runtime_text: str, handoff_text: str) -> list[str]:
    runtime, sections = _parse_live_sections(runtime_text)
    handoff, _ = _parse_frontmatter(handoff_text)
    errors: list[str] = []

    capsule_sections = [
        section
        for section in sections
        if section.title.lower().startswith("current capsule")
    ]
    next_sections = [
        section for section in sections if section.title.lower().startswith("next action")
    ]
    if len(capsule_sections) != 1:
        errors.append(f"live_current_capsule_count={len(capsule_sections)}")
    if len(next_sections) != 1:
        errors.append(f"live_next_action_count={len(next_sections)}")

    for section in sections:
        title = section.title.lower()
        if title.startswith("current") and (
            "ed-10" in title or re.search(r"\br3\b", title)
        ):
            errors.append(f"legacy_current_section={section.title}")

    if len(capsule_sections) == 1:
        fields = _semantic_bullets(capsule_sections[0])
        for key in (
            "active slice",
            "active artifact",
            "review status",
            "portable receipt",
            "local artifact role",
            "human review pending",
        ):
            if len(fields.get(key, [])) != 1:
                errors.append(f"capsule_{key.replace(' ', '_')}_count={len(fields.get(key, []))}")
        expected_capsule_values = {
            "active slice": runtime.get("current_slice", ""),
            "active artifact": runtime.get("active_artifact", ""),
            "review status": runtime.get("review_status", ""),
            "portable receipt": runtime.get("portable_entrypoint", ""),
            "local artifact role": runtime.get("local_artifact_role", ""),
            "human review pending": runtime.get("human_review_pending", ""),
        }
        for key, expected in expected_capsule_values.items():
            values = fields.get(key, [])
            if len(values) == 1 and values[0] != expected:
                errors.append(
                    f"capsule_{key.replace(' ', '_')}_mismatch="
                    f"{values[0]}!={expected}"
                )

    if len(next_sections) == 1:
        fields = _semantic_bullets(next_sections[0])
        actions = fields.get("action", [])
        if len(actions) != 1:
            errors.append(f"next_action_value_count={len(actions)}")
        elif actions[0] != runtime.get("next_action", ""):
            errors.append(
                f"next_action_mismatch={actions[0]}!={runtime.get('next_action', '')}"
            )

    if runtime.get("current_slice") != "ED-13":
        errors.append(f"runtime_current_slice={runtime.get('current_slice', '')}")
    if runtime.get("active_artifact") != "clip-s2-subaru-evidence-linked-comparison-v1-002":
        errors.append(f"runtime_active_artifact={runtime.get('active_artifact', '')}")

    expected_runtime_values = {
        "active_branch": "codex/s2-evidence-linked-comparison-v1",
        "base_main_revision": "40fe3fbdf13631948d03641e33325e7f01ed9e56",
        "implementation_revision": "commit_containing_this_document",
        "artifact_output_sha256": (
            "a959dc50a0b1b36d37644195fab9105403afdbc7e5f60dfc42ca90c70c72d00f"
        ),
        "artifact_package_tree_digest_sha256": (
            "ea2e6cb359325210ed2e1f267d5f3a0b9f6ca22d31b229cbe8b569a24b508090"
        ),
        "artifact_manifest_self_sha256": (
            "4eda3d7f01a4fc1abc4c1d863a03d5dec2b061d3708149ba00259515d51b5479"
        ),
        "package_validation_status": "passed",
        "full_suite_status": "not_run_by_mission_authority_focused_15_passed",
        "human_review_pending": "true",
        "rights_approval": "not_granted",
        "production_acceptance": "false",
        "public_use": "false",
        "monetized_use": "false",
        "upload_attempted": "false",
        "upstream_parity": "no_upstream_local_only",
        "remote_code_complete": "false",
        "decision_required": "human_editorial_verdict_on_exact_evidence_linked_comparison",
        "next_review_due": "exact_evidence_linked_comparison_human_review",
    }
    for field, expected in expected_runtime_values.items():
        if runtime.get(field, "") != expected:
            errors.append(f"runtime_{field}={runtime.get(field, '')}!={expected}")

    for field in ALIGNED_FIELDS:
        if runtime.get(field, "") != handoff.get(field, ""):
            errors.append(
                f"surface_mismatch_{field}="
                f"{runtime.get(field, '')}!={handoff.get(field, '')}"
            )

    return errors


def _insert_before_archive(runtime_text: str, addition: str) -> str:
    return runtime_text.replace(
        ARCHIVE_MARKER,
        f"{addition.rstrip()}\n\n{ARCHIVE_MARKER}",
        1,
    )


def test_current_resume_surfaces_have_one_semantically_aligned_live_authority() -> (
    None
):
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")

    assert _authority_errors(runtime, handoff) == []


def test_s2_resume_rejects_stale_local_only_state() -> None:
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")
    stale_runtime = (
        runtime.replace(
            "active_branch: codex/s2-evidence-linked-comparison-v1",
            "active_branch: codex/stale-s2",
            1,
        )
        .replace(
            "upstream_parity: no_upstream_local_only",
            "upstream_parity: 1 0",
            1,
        )
        .replace(
            "remote_code_complete: false",
            "remote_code_complete: true",
            1,
        )
    )

    errors = _authority_errors(stale_runtime, handoff)

    assert any(error.startswith("runtime_active_branch=") for error in errors)
    assert any(error.startswith("runtime_upstream_parity=") for error in errors)
    assert any(
        error.startswith("runtime_remote_code_complete=")
        for error in errors
    )
    assert any(error.startswith("surface_mismatch_active_branch=") for error in errors)


def test_duplicate_live_capsule_and_artifact_fail_semantic_authority_check() -> None:
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")
    duplicate = """
## Current Capsule — ED-10ax stale route

- active slice: `ED-10ax`
- active artifact: `clip-ed10ax-review-frame-clarification-surface-001`
"""

    errors = _authority_errors(_insert_before_archive(runtime, duplicate), handoff)

    assert "live_current_capsule_count=2" in errors
    assert any(error.startswith("legacy_current_section=") for error in errors)


def test_multiple_live_next_actions_fail_semantic_authority_check() -> None:
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")
    stale_next = """
## Next Actions

- action: `resume_r3_review`
"""

    errors = _authority_errors(_insert_before_archive(runtime, stale_next), handoff)

    assert "live_next_action_count=2" in errors


def test_runtime_handoff_portability_role_disagreement_fails_semantic_check() -> None:
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8").replace(
        "local_artifact_role: active_private_human_review_target_same_machine_only",
        "local_artifact_role: stale_review_target",
        1,
    )

    errors = _authority_errors(runtime, handoff)

    assert any(
        error.startswith("surface_mismatch_local_artifact_role=") for error in errors
    )


def test_runtime_handoff_package_status_disagreement_fails_semantic_check() -> None:
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8").replace(
        "package_validation_status: passed",
        "package_validation_status: failed",
        1,
    )

    errors = _authority_errors(runtime, handoff)

    assert any(
        error.startswith("surface_mismatch_package_validation_status=")
        for error in errors
    )


def test_archived_legacy_sections_do_not_enter_live_semantics() -> None:
    runtime = RUNTIME_PATH.read_text(encoding="utf-8")
    handoff = HANDOFF_PATH.read_text(encoding="utf-8")
    archived_fixture = runtime + """

## Current Capsule — historical fixture

- active slice: `R3`
- active artifact: `clip-r3-historical-fixture`

## Next Actions

- action: `historical_only`
"""

    assert _authority_errors(archived_fixture, handoff) == []
