# OUT-05 Vertical Short Internal Candidate

OUT-05 preserves the user-accepted OUT-04 `cut_001 -> cut_002` timeline and
produces one same-machine 1080x1920 internal review candidate. It is a bounded
vertical-format review surface, not a production render, subtitle-design
acceptance, rights clearance, public-ready asset, or publishing action.

## Observable result

The only artifact ID is
`clip-out05-vertical-short-internal-candidate-v0-001`. The ignored local bundle
is written directly under:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out05_vertical_short_internal_candidate/
```

Use `open_preview.ps1` as the single entrypoint; add `-Serve` when localhost
playback is needed. The page places one vertical video first, then three review
questions, with reframe specimens, frame QA, subtitle readback, probe,
provenance, and closed gates in disclosure sections.

## Build command

Pillow is supplied to the command so the existing Keifont font-bbox wrapper can
choose explicit measured line breaks before ASS/libass rendering:

```powershell
uvx --with Pillow python -m src.cli.main build-vertical-short-candidate `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out05_vertical_short_internal_candidate `
  --predecessor-readback episodes/jp_pilot01_hololive_bancho_20260525/review/out04_editorial_representative_sequence/sequence_readback.json `
  --format json
```

The builder renders into a sibling staging directory, validates the complete
bundle, and then promotes it. A render failure leaves an existing output bundle
unchanged. Traversal, non-`out05_*` output names, input/output overlap, and
overlap with OUT-03, OUT-04, or the retained human preview are rejected.

## Reframe and subtitle decision

Only still-frame specimens compare the three bounded routes: cut-level anchor
crop, full 16:9 fit over a source-derived blurred/toned canvas, and bounded
hybrid. The full-fit route is selected because both accepted cuts use meaningful
left/right composition; the crop can remove the phone counterpart or action
entry, while the hybrid still loses edge context without a clear focal gain.
No three full comparison videos are rendered.

The nine accepted subtitle events keep their OUT-04 timing. The route reuses
the semantic selector, Keifont/Candidate 2 body treatment with Candidate 0 as
fallback reference, existing font-bbox measurement, explicit ASS line breaks,
and FFmpeg/libass. No verified speaker identity exists for these events, so no
speaker badge, identity layer, diagnostic label, or technical placeholder is
visible. The vertical balancing pass chooses only measured-width-valid lines,
keeps cues within a conservative internal safe envelope, and limits them to
three lines. This does not claim platform-production-safe typography.

## Actual local readback

The final candidate probes as H.264/AAC, 1080x1920, 30fps, yuv420p, faststart,
with one video and one audio stream and duration `11.700s`, inside the `0.20s`
tolerance around the accepted `11.678s` timeline. Full decode passed. The
accepted boundary remains `6.840s`; `cut_003`, transitions, and sound effects
remain absent.

The source sequence measured `-19.22 LUFS` / `-2.11 dBTP`, which was a clear
level gap for this candidate. The rendered output measures `-14.06 LUFS` /
`-1.49 dBTP`. Browser validation found one video, readyState `4`, duration
`11.700`, intrinsic size 1080x1920, no media error, no console warning/error,
no horizontal overflow, and a height-bounded desktop presentation.

## Package files

- `assets/vertical_short_candidate.mp4`
- `vertical_short_subtitles.ass`
- `vertical_short_subtitles.srt`
- `reframe_plan.json`
- `candidate_readback.json`
- `assets/reframe_comparison_contact_sheet.jpg`
- `assets/frame_qa_contact_sheet.jpg`
- `index.html`
- `open_preview.ps1`
- `serve_preview.ps1`

The final MP4 SHA-256 is
`d2a75ed5f85a0869d4178917c258624ccf083bbefce33ab468549f93a982b827`.
OUT-03, OUT-04, and the retained human-preview tree digests are preserved in
`candidate_readback.json`. Nothing under `episodes/` is tracked.

## Review boundary

The only requested human judgement is:

1. Whether the vertical framing preserves the subject/action and reads as a
   natural Shorts candidate.
2. Whether subtitle position, wrapping, and readability stay consistent and
   avoid obstructing the image.
3. Whether audio, the hard-cut boundary, and the screen show any dropout,
   corruption, or export anomaly.

The machine flags remain:

- `internal_review_only=true`
- `vertical_format_candidate=true`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights=pending`
- `public_ready=false`
- `publishing=false`
- `publish_attempted=false`
