# OUT-04 Editorial Representative Sequence

OUT-04 composes two or three retained real selected cuts into one 10-30 second
same-machine review video. It is the first output-layer milestone that lets a
reviewer judge editorial order, hard-cut continuity, pacing, and subtitle/audio
continuity in one playback instead of opening separate cut files.

## Observable result

The artifact ID is `clip-out04-editorial-representative-sequence-v0-001`. The
real JP-Pilot run writes one ignored package at:

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out04_editorial_representative_sequence/
```

Its only operator entrypoint is `open_preview.ps1`. Use `-Serve` on the same
script when direct `file://` playback is unavailable. The package contains one
H.264/AAC MP4, one sequence-relative SRT, `sequence_readback.json`, `index.html`,
and the opener/server scripts. Nothing under `episodes/` is tracked.

## Real sequence command

```powershell
uvx python -m src.cli.main build-editorial-sequence `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out04_editorial_representative_sequence `
  --cut-id cut_001 `
  --cut-id cut_002 `
  --cut-decision-readback episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/cut_decision_packet.json `
  --source-video-material-id src_video_jp_pilot01 `
  --source-audio-material-id src_audio_jp_pilot01 `
  --format json
```

The explicit order is `cut_001 -> cut_002`. Current edit/decision evidence marks
both `keep` with context `passed`. Their source ranges are `2.453-9.293s` and
`12.329-17.167s`; the sequence ranges are `0.000-6.840s` and
`6.840-11.678s`, joined by one hard cut. Nine subtitle events are rebased into
the sequence and remain contained within their owning cut. `cut_003` is not
silently included because its current context remains `needs_review` and it
would exceed the 30-second review bound.

## Validation and readback

The builder validates the ordered decisions, context, transcript segments,
subtitle text/timing linkage, material acquisition route and SHA-256, source
stream/window availability, output directory isolation, and final probe. The
readback carries source and sequence ranges, input/output hashes, H.264/AAC
stream metadata, resolution/fps, the `0.20s` output-duration tolerance, and the
three bounded review questions shown by the HTML page.

The output directory must be a direct `episode/review/out04_*` child. Unsafe or
duplicate IDs, traversal, input/output overlap, protected preview overlap,
fixture provenance, missing streams, rejected/needs-review decisions, and
cross-boundary subtitles fail before a successful package is reported. OUT-03
and the retained `human_preview_session/` are sibling evidence and must remain
byte-for-byte unchanged.

Rights remain `pending`. The sequence is diagnostic/representative review
evidence only: production render acceptance, production subtitle design,
creative acceptance beyond this milestone, public use, upload, and publishing
remain false or unopened.
