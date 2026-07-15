# Planner007 OUT-08 private review package recovery receipt — 2026-07-15

This non-authoritative host receipt reports the recovery implementation for
`DESKTOP-U9P4LKJ`. Portable current state remains in
[RUNTIME_STATE.md](RUNTIME_STATE.md), and execution resumes from
[CURRENT_HANDOFF.md](CURRENT_HANDOFF.md).

## Outcome for supervising AI

The exact OUT-08 candidates are preserved as Thank-host evidence and now have a
host-aware recovery path. The implementation does not regenerate media or use
Git as transport. It validates the 17-file/16-payload package, manifest
self-integrity, both candidate hashes, Thank source identity, closed gates, and
the full `cut_009` exclusion before export and at import staging. Export is a
deterministic ZIP to an explicit repository-external new path; import rejects
unsafe archive structures and promotes only a fully verified sibling stage.

| Supervisor question | Current answer | Workflow effect |
|---|---|---|
| Are the product candidates lost? | No. Thank evidence preserves candidate 01 `f7ea3f...388a`, candidate 02 `47c844...593b`, and manifest self-integrity `22c713...b4a4`. | Recovery transports those exact bytes; it does not create a new revision. |
| Can Planner007 review now? | No. The current probe is `package_missing` / `server_stopped`; no current human entrypoint is claimed. | One private package transfer is required before playback review. |
| Is transfer implemented safely? | Yes. The kit provides host-gated deterministic export, strict archive/receipt validation, fail-closed atomic import, existing-package preservation, and HTTP 200/Range 206 probe. | Thank can export; after a user-owned private copy, Planner007 can import and verify without reopening generation. |
| Did scope expand into delivery or acceptance? | No. No upload, transfer-channel operation, media mutation, GUI opening, candidate acceptance, or production/public gate change occurred. | Human review and all downstream gates stay pending. |

## Verified current-host classification

`uvx python -m src.cli.main recover-out08-private-review-package --format json probe`
observed host `DESKTOP-U9P4LKJ`, package `package_missing`, and port 8071
`server_stopped`. It wrote a sanitized receipt under ignored `episodes/` storage;
the receipt contains repository-relative paths and hashes rather than absolute
private paths. A generic localhost URL has therefore been removed from current
Runtime, Handoff, dashboard, and registry surfaces; Thank's former URL remains
last-verified historical evidence only.

The recovery-specific suite passes 21 tests covering deterministic
export, exact allowlists, missing/extra files, traversal, unknown files,
duplicate and case-colliding entries, corrupt archives, candidate/manifest
identity failure, `cut_009` overlap, atomic promotion, invalid-existing-package
preservation, and sanitized missing-state probe. The combined recovery, OUT-08
builder, active-rebuild, and dashboard focus is 58 passing tests. CLI
import/help, PowerShell parsing, changed-scope Ruff, and dashboard regeneration
also pass.

## Remaining operator-owned move

On Thank, export to a new explicit repository-external ZIP. The user then copies
that ZIP through a private channel they choose. On Planner007, import with
`--start-server`; proceed to direct playback/seek only when the receiving probe
reports `package_verified_exact` and `server_running_verified`. Rights,
production render, production subtitle design, public/publishing, upload,
OUT-07 thumbnail iteration, and source-byte equivalence remain closed or
unestablished.

---

# OUT-07 parked closure receipt — 2026-07-14

This non-authoritative receipt records the consumed human review. OUT-07 is
closed as `PARK_PROVISIONAL_USABLE`: the current cover is natural, balanced, and
provisionally usable for this episode, but it is not selected, canonical,
default, reusable as a standard, or accepted as a final thumbnail system.
Only one example exists, so reproducibility is unknown and accidental success
is not ruled out. The reference-collection process remains valid while the
reference-to-output lineage remains weak.

The Thank proxy package below is retained unchanged as historical local
evidence. It is no longer the current human entrypoint, and its review server is
stopped. Additional OUT-07 thumbnail iteration is prohibited. Revisit thumbnail
exploration only after 3–5 real Shorts exist, treating the reference corpus as
concrete examples rather than canonical design rules. Rights, production,
public/publishing, upload, and other external gates remain closed or pending.

---

# Historical Thank OUT-07 semantic direction proxy host receipt — 2026-07-14

This is a non-authoritative host receipt. The portable current state and next
action remain in [RUNTIME_STATE.md](RUNTIME_STATE.md). The current host verified
pre-closure state was `OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY`.

Thank has the known source SHA
`6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`
and official caption SHA
`3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`.
The separate semantic proxy route validated provider `7J5aS_pcBj4`, source
`22.858s`, nearest decoded frame `22.866667s`, sequence `11.930s`, `cut_003`,
and `sub_010`, then reused the established vertical reframe, Keifont, and
subtitle treatment. It did not add an abstract poster background, headline,
mask, collage, or third-party pixel.

The output is
`episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/`.
The proxy PNG SHA is
`e7aaae24401b5b6c75e13926329af19c8a59008dd3c93229735d7465da2f18da`.
Its source and proxy fingerprints differ from the Planner-known fingerprints,
so the classification is `cover_direction_semantic_proxy`, not exact or
pixel-equivalent. Local scene/cue/timing evidence was directly observed;
continuity to Planner is inferred from provider identity and authoritative
mapping because Planner pixels are unavailable on Thank. Two consecutive builds matched every package byte; core and
package digests are `deb93e2f...652` and `0eeb4958...832`, with manifest
inventory and self-integrity passing.

The historical local entrypoint was `http://127.0.0.1:8071/index.html` on
`DESKTOP-H53P1T4`; it is not portable. The page presents list preview, one
1080x1920 proxy, UI overlap, 4:5 crop, mapped source frame, folded evidence, and
one question. It contains no exact baseline video or former candidate set.

Planner007's accepted baseline SHA `2c1c59bc...2d18` remains an accepted
historical fact but is absent on Thank. The strict exact route is unchanged and
still requires its exact SHA/size/duration and byte-copy acceptance gate. The
proxy is only a cover-direction decision surface. Rights, production,
public/publishing, upload, metadata mutation, visibility, made-for-kids, and
all external actions remain pending, false, closed, or unattempted.

The consumed human question was:

> このThank source revisionによる同一時刻・同一字幕のShorts一覧cover方向を採用してよいか。違和感があれば自由記述してください。

---

# Historical Planner007 OUT-07 host receipt — 2026-07-13

The section below records what Planner007 verified before the cross-device
pause. It is lineage evidence, not the current Thank entrypoint.

## What is true on this host

Planner007 explicitly accepted the current 38.633333-second vertical baseline
on 2026-07-13 JST for content/narrative, timing/tempo, cut continuity, A/V
continuity, subtitle timing/readability, and visual integrity. The accepted
baseline SHA-256 is
`2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`;
the qualified source is YouTube `7J5aS_pcBj4`, SHA-256
`e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`.
The official JSON3 caption authority is SHA-256
`3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`, with
payload digest `e9a18053baf3b6d042f35a91bb18ee7c5b28c878ef9e9d66ce649563ce11c23b`;
the current tracked tip retains hashes and IDs, not caption plaintext.
This acceptance is explicit for the current bytes and does not inherit the
historical OUT-06 acceptance.

The last verified local package is
`episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/`.
Its builder verifies and copies the accepted MP4 byte-for-byte; it does not
render, remux, transcode, edit, retime, or alter subtitles/audio. The sole
recommended cover is the accepted vertical video's 11.930-second frame, mapped
to source time 22.858 seconds and retaining only the existing burn-in
`sub_010`. Its PNG SHA-256 is
`6d8cf92ae49658a9eacb98e7a6e584aa69d2a4ecbb56b553c93eec69e6a3a174`.

The review page provided list-scale, generic Shorts-UI overlap, full 9:16,
center-4:5, mapped-source-frame, metadata, accepted-baseline hash, provenance,
gate, and superseded-candidate readbacks. It was last opened through
`http://127.0.0.1:8071/index.html` on Planner007. PID `41872` was verified as
the OUT-07 `src.cli.serve_review` process serving that directory, then stopped;
port 8071 is now released. The URL and package are not portable current
entrypoints. The portable local artifact flag is `false`; `human_entrypoint`,
`review_open_command`, and `machine_readback` are all `null` in the durable
state. The last-host-only URL above is evidence, not a cross-device promise.

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

## Durable handoff classification

| Class | Handoff meaning |
|---|---|
| tracked | builders, CLI, tests, hash-only caption/timing contract, accepted baseline SHA/size/duration, cover timestamp/SHA/fingerprints, Runtime/Handoff/dashboard/contracts, source/caption identity and recovery commands |
| ignored_local_retained | source media, exact accepted baseline MP4, official JSON3, native cover, review package, manifests/readbacks/previews, local reference cache on Planner007 |
| conditional_reacquire | source identity `7J5aS_pcBj4`, official caption authority, and dependencies; hash mismatch creates a new revision and never inherits acceptance |
| retained_artifact_reacquire | exact baseline SHA `2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`; absence stops as `accepted_baseline_reacquire_required` |
| derive | cover, previews, readbacks, package, and manifests only after exact baseline restoration |
| private_only | media bytes, caption plaintext, third-party pixels/cache, credentials, OAuth information |

H1 is cover acceptance followed by closure/full-suite work. H2 is a real
other-host recovery proof. H3 is rights, production, public/publishing, or
external-system work. None is executed by this closeout.
