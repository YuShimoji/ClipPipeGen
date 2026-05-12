"""ClipPipeGen CLI dispatcher.

Usage:
    python -m src.cli.main <subcommand> [args...]

Subcommands:
    init-episode             Create a new episode skeleton with rights_manifest.
    validate-rights          Validate a rights_manifest.json against schema v1.
    set-compliance           Update compliance_check.status readback.
    register-material        Register a material into the episode ledger (sidecar required).
    audit-material-ledger    Integrity check for an episode material_ledger.json.
    audit-thumbnail          Audit YMM4 thumbnail template via NLMYTGen subprocess (read-only).
    patch-thumbnail          Apply thumbnail_patch_input end-to-end (rights readback + material + NLMYTGen patch).
    status-episode           Summarize one episode's Slice 1 artifact status for the GUI MVP.
    measure-subtitle-width   ED-05: measure subtitle text in EAW units (optional wrap).
    init-edit-pack           Create an edit_pack skeleton for the Editing lane.
    validate-edit-pack       Validate edit_pack.json against schema v1.
    add-cut-candidate        Append one manual/imported cut candidate to edit_pack.
    validate-transcript      Validate transcript.json against schema v1.
    transcribe-audio         ED-07: local audio -> transcript.json (fake or optional Vosk).
    fetch-source-audio       INT-02: create/register source_audio WAV material.
    generate-cuts            ED-02: transcript.json -> edit_pack.cut_candidates[].
    check-cut-context        ED-03: review cut boundaries against transcript context.
    generate-subtitles       ED-04: transcript.json -> edit_pack.subtitles[] drafts.
    export-nle               ED-06: edit_pack.json -> human-readable NLE CSV cut list.
    build-local-preview-pack SH-05: local media -> read-only artifact preview pack.
"""

from __future__ import annotations

import sys
from typing import Callable

from . import (
    add_cut_candidate,
    audit_material_ledger,
    audit_thumbnail,
    build_local_preview_pack,
    check_cut_context,
    export_nle,
    fetch_source_audio,
    generate_cuts,
    generate_subtitles,
    init_edit_pack,
    init_episode,
    measure_subtitle_width,
    patch_thumbnail,
    register_material,
    set_compliance,
    status_episode,
    transcribe_audio,
    validate_edit_pack,
    validate_rights,
    validate_transcript,
)

SUBCOMMANDS: dict[str, Callable[[list[str]], int]] = {
    "init-episode": init_episode.run,
    "validate-rights": validate_rights.run,
    "set-compliance": set_compliance.run,
    "register-material": register_material.run,
    "audit-material-ledger": audit_material_ledger.run,
    "audit-thumbnail": audit_thumbnail.run,
    "patch-thumbnail": patch_thumbnail.run,
    "status-episode": status_episode.run,
    "measure-subtitle-width": measure_subtitle_width.run,
    "init-edit-pack": init_edit_pack.run,
    "validate-edit-pack": validate_edit_pack.run,
    "add-cut-candidate": add_cut_candidate.run,
    "validate-transcript": validate_transcript.run,
    "transcribe-audio": transcribe_audio.run,
    "fetch-source-audio": fetch_source_audio.run,
    "generate-cuts": generate_cuts.run,
    "check-cut-context": check_cut_context.run,
    "generate-subtitles": generate_subtitles.run,
    "export-nle": export_nle.run,
    "build-local-preview-pack": build_local_preview_pack.run,
}


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args[0] in ("-h", "--help"):
        _print_help()
        return 0 if args else 2

    sub = args[0]
    handler = SUBCOMMANDS.get(sub)
    if handler is None:
        print(f"unknown subcommand: {sub}", file=sys.stderr)
        _print_help()
        return 2

    return handler(args[1:])


def _print_help() -> None:
    print(__doc__ or "")


if __name__ == "__main__":
    raise SystemExit(main())
