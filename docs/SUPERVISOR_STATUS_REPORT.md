# Planner007 OUT-07 host receipt — 2026-07-13

This is a non-authoritative host receipt. The portable current state and next
action remain in [RUNTIME_STATE.md](RUNTIME_STATE.md); this page records what
the supervising host can actually open and verify.

## What is true on this host

Planner007 explicitly accepted the current 38.633333-second vertical baseline
on 2026-07-13 JST for content/narrative, timing/tempo, cut continuity, A/V
continuity, subtitle timing/readability, and visual integrity. The accepted
baseline SHA-256 is
`2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`;
the qualified source is YouTube `7J5aS_pcBj4`, SHA-256
`e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`.
This acceptance is explicit for the current bytes and does not inherit the
historical OUT-06 acceptance.

The active local package is
`episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/`.
Its builder verifies and copies the accepted MP4 byte-for-byte; it does not
render, remux, transcode, edit, retime, or alter subtitles/audio. The sole
recommended cover is the accepted vertical video's 11.930-second frame, mapped
to source time 22.858 seconds and retaining only the existing burn-in
`sub_010`. Its PNG SHA-256 is
`6d8cf92ae49658a9eacb98e7a6e584aa69d2a4ecbb56b553c93eec69e6a3a174`.

The review page provides list-scale, generic Shorts-UI overlap, full 9:16,
center-4:5, mapped-source-frame, metadata, accepted-baseline hash, provenance,
gate, and superseded-candidate readbacks. It is opened through the byte-range
localhost route at `http://127.0.0.1:8071/index.html`; the process ID is runtime
evidence and is reported at handoff rather than frozen in this tracked file.

## Decision boundary

The previous active A/B/C are
`superseded_by_user_short_context_reframe`, not quality-rejected, and must not
be offered again. Historical `context` / `tension` / `payoff` directions remain
separately `user_rejected`. The only remaining human judgment is whether the
single native-frame cover direction works for the Shorts list surface.

`selected_thumbnail=null`, `selected_by_human=false`, and
`publish_ready=false`. Rights, production, public/publishing,
upload/visibility, metadata mutation, made-for-kids, and every external-system
action remain closed, pending, or unattempted; baseline acceptance does not
open any of those gates.

## Portability limit

The tracked rebuild contract retains subtitle IDs, cut/timing/segment
locators, text hashes, digest, and wrap break indices, but not the former bulk
caption plaintext. Another host must conditionally reacquire the official JSON3
caption authority when absent and must restore the exact accepted baseline
bytes; missing captions stop as `caption_authority_reacquire_required`, and the
active route is forbidden from recreating the accepted baseline by rendering.
Cross-machine resume therefore remains `conditional_reacquire`. Earlier commits
may contain the former plaintext snapshot; no history scrub is claimed.
