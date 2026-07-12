# OUT-06 Complete Narrative Short Delivery Candidate

OUT-06 preserves the user-accepted OUT-05 opening and appends only the existing
authoritative `cut_003` range to create one complete introduction-development-
close internal narrative short. The 2026-07-12 bounded repair for six subtitle
wraps and localhost seekability is now accepted as
`accepted_after_bounded_repair`. This package is the immutable internal video
predecessor for OUT-07, but it is still an ignored same-machine review package,
not a production render, production subtitle-design acceptance, rights
clearance, public-ready asset, thumbnail upload approval, metadata publication,
visibility decision, made-for-kids decision, or publishing action.

## Observable result

The only artifact ID is
`clip-out06-complete-narrative-short-delivery-candidate-v0-001`. The package is:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/
```

`open_preview.ps1` is the single entrypoint; `-Serve` starts the byte-range
localhost route for seekable review.
The page puts one vertical video first, asks only three whole-candidate questions,
uses no card grid, and keeps timeline, frame, subtitle, media/provenance, and gate
details folded.

## Build command

```powershell
uvx --with Pillow python -m src.cli.main build-complete-narrative-short `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate `
  --predecessor-readback episodes/jp_pilot01_hololive_bancho_20260525/review/out05_vertical_short_internal_candidate/candidate_readback.json `
  --format json
```

The builder validates the exact accepted OUT-05 readback and MP4, the accepted
OUT-04 source timeline, the current edit pack/transcript, the cut decision
packet, and the existing operator proxy authority. It stages the full package,
checks protected trees and input hashes before/after rendering, validates every
required file and manifest hash, then atomically promotes the result.
On Windows, an active localhost preview can hold the output directory; the
builder then preserves the existing package and reports that the retained
preview server must be stopped before regeneration.

The normal page keeps audio review manual. `index.html?qa-playback=1` is a
muted-autoplay-only local QA route used to prove a full browser decode when the
automation browser does not grant trusted media gestures; `index.html?qa-seek=0.6`
is a muted seek QA route used only to record `seeked` and resume behavior. These
QA query routes are not the human audio-review route.

## Exact sequence authority

| Cut | Source range | Sequence range | Narrative role | Authority |
|---|---:|---:|---|---|
| `cut_001` | `2.453–9.293` | `0.000–6.840` | introduction | accepted OUT-05 opening |
| `cut_002` | `12.329–17.167` | `6.840–11.678` | development | accepted OUT-05 opening |
| `cut_003` | `22.606–49.566` | `11.678–38.638` | resolution and close | `keep`, `needs_review`, `proceed_with_limitations` |

The joins are hard cuts at `6.840s` and `11.678s`. No transition, padding, BGM,
or SFX is added. `sub_001..sub_029` are included; `sub_030` remains excluded.
The 29 cues retain source timing/provenance, then use the existing presentation
replacement rule for the one source overlap before ASS rendering.

`cut_003` remains `needs_review`; the existing manual override and
`proceed_with_limitations / keep_retained_risk_visible` authority are read and
reported, not rewritten. That retained limitation does not block this internal
diagnostic candidate and does not become production acceptance.

## Reused render boundary

OUT-06 does not copy the OUT-05 builder. It reuses the extracted data-driven
vertical boundary for:

- Keifont / ED-10w Candidate 2 body treatment with Candidate 0 reference,
- font-bbox measured wrapping and explicit ASS line breaks,
- maximum three-line internal safe envelope,
- full 16:9 fit over a same-source blurred/toned 1080x1920 canvas,
- per-cut source video/audio trim, shared hard-cut concat, ASS/libass burn-in,
- H.264/AAC 30fps yuv420p faststart output,
- loudness/true-peak measurement and conditional normalization,
- full decode and multi-frame QA contact sheet.

No speaker identity is verified, so no `SPK`, diagnostic label, technical label,
or other visible placeholder is rendered. No reframe comparison or typography
micro-tuning loop is reopened.

## Actual local readback

The 2026-07-12 JST user review accepted the narrative tempo and audio/video
continuity, then requested bounded subtitle-wrap and seekability repair. The
same artifact ID now carries repaired display wraps for `sub_013`, `sub_014`,
`sub_019`, `sub_024`, `sub_028`, and `sub_029`; authoritative text, timing,
IDs, and source mappings are unchanged.

The final repaired MP4 SHA-256 is
`02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0`.
It probes as H.264/AAC, 1080x1920, 30fps, yuv420p, faststart, with one video and
one audio stream. Media duration is `38.633333s`, within `0.20s` of the
`38.638s` semantic authority. Full FFmpeg decode passed.

The source sequence measured `-19.21 LUFS / -2.11 dBTP`; normalization was
applied and the final output measures `-14.39 LUFS / -1.49 dBTP`. Decoded PCM
windows at both `6.840s` and `11.678s` passed without click risk or digital
dropout risk. The 16-point contact sheet contains real frames at the required
start/boundary/cut_003/dense/repaired-cue/end positions with no black/corrupt
sample or visible placeholder.

Browser seek QA on the localhost byte-range route reached 25%, 60%, and 90%
with `seeked`, max target delta about `0.0008s`, `playStatus=resumed`,
readyState `4`, no media error, no horizontal overflow, and all details folded.
Native pointer-drag proof is not claimed. The normal review page starts paused
and keeps all five details folded.

## Package files

- `assets/complete_narrative_short.mp4`
- `complete_narrative_short_subtitles.ass`
- `complete_narrative_short_subtitles.srt`
- `narrative_sequence_plan.json`
- `candidate_readback.json`
- `delivery_manifest.json`
- `assets/poster_frame.jpg`
- `assets/frame_qa_contact_sheet.jpg`
- `index.html`
- `open_preview.ps1`
- `serve_preview.ps1`

The poster is a frame extracted from the final video and is explicitly not a
decorated thumbnail. The delivery manifest carries byte SHA-256 for every other
package file and a declared canonical self-integrity SHA-256 with only its own
hash value omitted, avoiding a false self-referential byte-hash claim.

## Review boundary

The only human questions are:

1. Whether the roughly 38-second whole reads as introduction, development, and
   close without `cut_003` feeling redundant.
2. Whether the `cut_002 -> cut_003` tempo/boundary and audio/video continuity
   feel natural.
3. Whether the vertical treatment and all 29 subtitles remain natural and
   readable through `cut_003`.

The machine flags remain:

- `internal_review_only=true`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights_status=pending`
- `public_ready=false`
- `publishing_acceptance=false`
- `publish_attempted=false`
