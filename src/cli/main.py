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
    apply-boundary-recommendation ED-10e: validate/apply one cut boundary recommendation with receipt.
    validate-transcript      Validate transcript.json against schema v1.
    review-transcript        ED-09: apply human review/correction patch to transcript.json.
    import-subtitle-track    ED-10: subtitle track -> transcript.json-compatible artifact.
    build-cut-review-packet  ED-10/R3: selected cuts -> review packet/report.
    build-chapter-revision-board R3: operator-editable chapter board + patch templates.
    build-cut-decision-packet R3: classify selected cuts for next acceptance slice.
    build-operator-proxy-decision-handoff R3: cut-scoped proxy decision handoff.
    build-subtitle-overlay-visual-proof R3: cut-scoped diagnostic subtitle-overlay proof.
    build-subtitle-typography-decoration-comparison ED-10g: review-only font/decor comparison.
    build-content-candidate-dashboard CPD-01: fixture -> content candidate/channel strategy dashboard.
    build-episode-seed-drafts CPD-02: content candidates -> non-fetching episode seed drafts.
    resolve-episode-seed-sources CPD-03: episode seed drafts -> source resolution/manual intake.
    build-episode-init-plan CPD-04: source resolution -> dry-run episode init plans.
    build-source-inspection-packet CPD-05: dry-run plans -> source inspection packets.
    build-operator-cockpit CPD-07: dark-mode vertical operator cockpit UX.
    build-episode-workspace-plan EWS-01: CPD current work item -> local workspace plan.
    init-episode-workspace EWS-01: materialize explicit-target local skeleton files.
    inspect-episode-workspace EWS-02: read explicit workspace skeleton status.
    prepare-source-identity-decision EWS-03: create pending local decision template.
    record-source-identity-decision EWS-03: validate/write local decision record.
    plan-source-fetch-prep EWS-04: decision-gated local source fetch-prep plan.
    build-episode-review-bundle SH-08: existing artifacts -> single diagnostic review bundle.
    build-human-preview-session SH-08: alias for the single human preview session bundle.
    build-docs-dashboard     Docs v1.5: wiki/dashboard status and doc-health findings.
    build-external-source-registry HUB-01: local RSS/manual fixtures -> source registry.
    build-output-layer-gap-report OUT-02: output fixture proof package and gap log.
    build-selected-cut-proof OUT-03: one real-local selected-cut playable review proof.
    build-editorial-sequence OUT-04: one real-local ordered multi-cut editorial sequence.
    build-vertical-short-candidate OUT-05: one accepted-timeline internal 1080x1920 candidate.
    build-complete-narrative-short OUT-06: one complete three-cut internal delivery candidate.
    build-real-unused-range-short-minibatch OUT-08: unused real ranges -> 1-2 vertical review candidates.
    build-operator-delivery-pack OUT-07: accepted OUT-06 video + thumbnail/metadata operator pack.
    build-shorts-poster-frame-proof OUT-07: reference-derived 9:16 poster directions + end-cap proofs.
    reconstitute-out07-review OUT-07: current media revision -> baseline-first combined poster review.
    build-out07-direction-proxy OUT-07: Thank source -> one native-cover direction proxy.
    build-non-repo-handoff   SH: local binary artifact -> handoff manifest/report.
    transcribe-audio         ED-07: local audio -> transcript.json (fake or optional Vosk).
    fetch-source-audio       INT-02: create/register source_audio WAV material.
    fetch-source-video       INT-02f: create/register source_video material.
    render-tiny-proof        OUT-01: source video/audio + edit_pack -> diagnostic video.
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
    apply_boundary_recommendation,
    audit_material_ledger,
    audit_thumbnail,
    build_editorial_sequence,
    build_complete_narrative_short,
    build_real_unused_range_short_minibatch,
    build_vertical_short_candidate,
    build_chapter_revision_board,
    build_content_candidate_dashboard,
    build_cut_decision_packet,
    build_cut_review_packet,
    build_episode_review_bundle,
    build_episode_init_plan,
    build_external_source_registry,
    build_output_layer_gap_report,
    build_operator_delivery_pack,
    build_out07_direction_proxy,
    build_shorts_poster_frame_proof,
    reconstitute_out07_review,
    build_selected_cut_proof,
    build_episode_workspace_plan,
    build_operator_cockpit,
    build_source_inspection_packet,
    build_episode_seed_drafts,
    build_docs_dashboard,
    build_local_preview_pack,
    build_non_repo_handoff,
    build_operator_proxy_decision_handoff,
    build_subtitle_overlay_visual_proof,
    build_subtitle_typography_decoration_comparison,
    check_cut_context,
    export_nle,
    fetch_source_audio,
    fetch_source_video,
    generate_cuts,
    generate_subtitles,
    import_subtitle_track,
    init_edit_pack,
    init_episode,
    init_episode_workspace,
    inspect_episode_workspace,
    measure_subtitle_width,
    patch_thumbnail,
    plan_source_fetch_prep,
    prepare_source_identity_decision,
    register_material,
    render_tiny_proof,
    record_source_identity_decision,
    resolve_episode_seed_sources,
    review_transcript,
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
    "apply-boundary-recommendation": apply_boundary_recommendation.run,
    "validate-transcript": validate_transcript.run,
    "review-transcript": review_transcript.run,
    "import-subtitle-track": import_subtitle_track.run,
    "build-cut-review-packet": build_cut_review_packet.run,
    "build-chapter-revision-board": build_chapter_revision_board.run,
    "build-cut-decision-packet": build_cut_decision_packet.run,
    "build-operator-proxy-decision-handoff": build_operator_proxy_decision_handoff.run,
    "build-subtitle-overlay-visual-proof": build_subtitle_overlay_visual_proof.run,
    "build-subtitle-typography-decoration-comparison": build_subtitle_typography_decoration_comparison.run,
    "build-content-candidate-dashboard": build_content_candidate_dashboard.run,
    "build-episode-seed-drafts": build_episode_seed_drafts.run,
    "resolve-episode-seed-sources": resolve_episode_seed_sources.run,
    "build-episode-init-plan": build_episode_init_plan.run,
    "build-source-inspection-packet": build_source_inspection_packet.run,
    "build-operator-cockpit": build_operator_cockpit.run,
    "build-episode-workspace-plan": build_episode_workspace_plan.run,
    "init-episode-workspace": init_episode_workspace.run,
    "inspect-episode-workspace": inspect_episode_workspace.run,
    "prepare-source-identity-decision": prepare_source_identity_decision.run,
    "record-source-identity-decision": record_source_identity_decision.run,
    "plan-source-fetch-prep": plan_source_fetch_prep.run,
    "build-episode-review-bundle": build_episode_review_bundle.run,
    "build-human-preview-session": build_episode_review_bundle.run_human_preview_session,
    "build-docs-dashboard": build_docs_dashboard.run,
    "build-external-source-registry": build_external_source_registry.run,
    "build-output-layer-gap-report": build_output_layer_gap_report.run,
    "build-selected-cut-proof": build_selected_cut_proof.run,
    "build-editorial-sequence": build_editorial_sequence.run,
    "build-vertical-short-candidate": build_vertical_short_candidate.run,
    "build-complete-narrative-short": build_complete_narrative_short.run,
    "build-real-unused-range-short-minibatch": build_real_unused_range_short_minibatch.run,
    "build-operator-delivery-pack": build_operator_delivery_pack.run,
    "build-shorts-poster-frame-proof": build_shorts_poster_frame_proof.run,
    "reconstitute-out07-review": reconstitute_out07_review.run,
    "build-out07-direction-proxy": build_out07_direction_proxy.run,
    "build-non-repo-handoff": build_non_repo_handoff.run,
    "transcribe-audio": transcribe_audio.run,
    "fetch-source-audio": fetch_source_audio.run,
    "fetch-source-video": fetch_source_video.run,
    "render-tiny-proof": render_tiny_proof.run,
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
