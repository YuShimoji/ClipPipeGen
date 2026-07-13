# Planner007 OUT-07 host receipt — 2026-07-13

This is a non-authoritative host receipt. The current portable state and next
action live in [RUNTIME_STATE.md](RUNTIME_STATE.md); do not use this file as a
second current ledger.

Planner007 has the tracked OUT-07 builder, CLI, tests, and reference corpus, but
does not have a reviewable local A/B/C package. The retained source at the
canonical episode path hashes to
`e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`,
while the builder requires
`6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`.
An inventory of every episode MP4 also found no accepted OUT-06 video matching
`02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0`.
The accepted OUT-06 package and frozen reference cache are absent.

Restore the exact retained source at
`episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4`
and the complete accepted OUT-06 package at
`episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/`.
The reference cache does not need transfer: after fixed-input recovery, the
tracked public corpus permits an explicit new freeze with a new cache revision.
Until regeneration, determinism, media, and browser QA pass on this host, port
8071 is not a valid review entrypoint.
