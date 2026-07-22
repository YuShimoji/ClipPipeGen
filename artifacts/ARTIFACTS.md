# Artifact Registry

This registry points to reviewable artifacts without pretending that ignored
local files are portable across clones. Use `docs/RUNTIME_STATE.md` for the
current artifact and next action; generated dashboard current-focus fields
follow that Runtime metadata.

Normal open order is `.\open-dashboard.ps1` first, choose the Runtime-driven
current artifact, then use an artifact-specific launcher. OUT-13 is currently the
same-machine caption-evidence editorial representative video. OUT-12 is its operational
one-command real-video predecessor. OUT-11 is the
closed five-source Short portfolio with two repaired candidates, one accepted
SOURCE-04 receipt, and a five-source scorecard. OUT-10 is the first repaired review candidate.
OUT-09 is closed accepted-internal canonical evidence. OUT-08 is the earlier closed accepted-internal
baseline evidence. OUT-07 is parked; its Thank native Shorts-cover
semantic direction proxy below is historical local evidence, not an active
review or a selected thumbnail. Historical
ED-10 proof launchers remain retained evidence; for the accepted ED-10o focused
comparison reference, use
`episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1`;
for the supporting regenerated ED-10l real-font comparison, use
`episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1`;
the reviewed ED-10k BIZ proof is now a reference entry, not the current proof
opened by the root launcher.

## `clip-out13-editorial-video-candidate-v1-001`

| Field | Value |
|---|---|
| title | OUT-13 Editorial Video Candidate v1 |
| purpose | Turn one real captioned source into an explicitly selected, chronologically traceable, clearly shortened editorial MP4 so a human can judge composition, subtitle presentation, and picture/audio quality on the same artifact. |
| storage class | Tracked CLI/render integration/tests/docs plus one ignored same-machine source/output package under `episodes/`. No source or generated media is tracked. |
| repo_relative_path | `src/cli/build_editorial_video_candidate.py`; `src/integrations/render/editorial_video_candidate.py`; `tests/test_editorial_video_candidate.py`; `docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md` |
| local_artifact_path | `episodes/out13_editorial_video_candidate_20260722/review/out13_editorial_video_candidate/` |
| state | `EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1` |
| source | `youtube:7J5aS_pcBj4`; provider `https://www.youtube.com/watch?v=7J5aS_pcBj4`; source SHA `e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`; 164.768798s; 1920x1080. |
| authority | Official JA JSON3 SHA `3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`; imported transcript SHA `ef928d4e3b47e5ab522cf8292d08fefdc81fcda9c904551941158814cdfb42d6`; rights snapshot SHA `e6ea94717b3bffceaa7cda9c608d2d2ecb6a0a46233958a9113f058c73464c12`. Wording/timing/cut evidence only; speaker, lyric, singing, and rights conclusions are not inferred. |
| editorial plan | Six non-contiguous chronological cuts across four evidence-bound sections; six omitted spans, four intentional; explicit selection/omission reasons, context, segment IDs, transitions; source utilization 0.74542; mapping coverage 1.0; no uniform sampling or arbitrary thirds. |
| final_video | H.264 High/AAC yuv420p, 1920x1080, 122.866016s, 73,776,611 bytes, SHA `84ed7aa6fc7aa1d478d7fa8f8783e349a5ffa56a7a59dc49c30daafa0791d7e2`. |
| subtitle presentation | 77 official cues; Keifont 100px / 115px line height; white body; speaker badge omitted because identity is unverified; black 8px outline / 2px shadow; 106px side margins / 92px bottom margin; maximum 2 lines; overlap/negative/orphan/overflow/violation 0. |
| validation | Nineteen review-visible checks passed. Full decode/faststart/timestamps/A/V/source mapping/caption containment passed; -14.61 LUFS, -1.58 dBTP, maximum adjacent cut delta 0.94 LU; black and silence events 0. Desktop/mobile overflow false; clean initial paused/muted/time0; seek exact; page 200; MP4 Range 206; console/media error 0. |
| evidence | Selected-source contact sheet, subtitle presentation contact sheet, normal/long-or-multiline/short-cue frames, all-cut boundary sheet, first/middle/last sheet, waveform, plan/readback/manifest on one video-first review page. |
| manifest | 23 payload rows; input fingerprint `051832b95969d8d3e35709f359e82dacb719552343ad40ec39ce35381685e3d8`; self-integrity SHA `8f0be672d847ea7b066a6ec932790f91601fd499956987813ec7edc42b0c02e8`. |
| resume | Same source/plan/settings resumed in 0.328s without render; video and manifest SHA unchanged. |
| preview_url | `http://127.0.0.1:8076/review/index.html`; validation listener stopped after HTTP/browser QA. |
| open_command | `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate\review\open_preview.ps1` |
| decision_required | Internal human review may now judge editorial structure, caption presentation, and picture/audio quality. Rights, production subtitle/design/render, thumbnail, public/publishing, and upload remain closed. |

Boundary flags:

- `internal_review_only=true`
- `human_review_pending=true`
- `rights_status=pending`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `thumbnail_acceptance=false`
- `public_or_publishing_acceptance=false`
- `upload_attempted=false`
- `episodes_tracked=false`

## `clip-supervisor-sync-roadmap-20260722-002`

| Field | Value |
|---|---|
| title | 2026-07-22 OUT-13 Remote Sync, Development Readiness, and Long-Range Goal Report |
| purpose | Give a supervising AI one tracked surface that separates the integrated main baseline, the two-commit-ahead OUT-13 review branch, portable code evidence, available OUT-12 media, absent OUT-13 plan/package, and a dependency-ordered M0-M11 route through human editorial review, production gates, explicit public release, and multi-episode operations. |
| storage class | Tracked Markdown report; portable Git evidence. No source or generated media included. |
| repo_relative_path | `docs/SUPERVISOR_STATUS_REPORT.md` |
| open_command | `Invoke-Item docs\SUPERVISOR_STATUS_REPORT.md` |
| sync_baseline | `main` was fast-forwarded from `8faaab2` to `5d6f69a`; verified OUT-13 implementation head is `c1566b3`, two commits ahead of main with sync-time upstream parity `0 0`. This report commit becomes the later handoff tip. No main merge is claimed. |
| validation | `npm ci` succeeded with 0 vulnerabilities; Electron 42.0.0 dependency tree resolved; `uvx --with Pillow pytest -q` returned 606 passed in 147.15s; Node and Electron GUI smokes passed; `build-editorial-video-candidate --help` resolved. |
| local_boundary | OUT-13 source/transcript/caption/rights inputs exist but the editorial plan and final/review package are absent in this root checkout. OUT-12 final/review package exists and its live MP4 SHA matches `5d391ffd...a584`. Protected R3 preview remains local; `episodes/` has zero tracked files. |
| decision_required | Restore access to the exact OUT-13 package or rebuild under a new hash-bound identity, then obtain human editorial review. Rights, production, private transport, credentials/OAuth, and public release remain separate explicit gates. |

## `clip-out12-one-command-real-video-automation-v1-001`

| Field | Value |
|---|---|
| title | OUT-12 One-Command Real Video Automation v1 |
| purpose | Turn one acquired real source into a chronologically traceable long-form internal MP4, validation readback, manifest, evidence, and review surface through one CLI command; prove fail-closed resume without reopening the Short detour. |
| storage class | Tracked CLI/render integration/tests/docs plus one ignored same-machine source and output package under `episodes/`. Media is not tracked or portable across clones. |
| repo_relative_path | `src/cli/build_real_video.py`; `src/integrations/render/real_video_pipeline.py`; `tests/test_real_video_pipeline.py`; `docs/output_layer/OUT_12_ONE_COMMAND_REAL_VIDEO_AUTOMATION.md` |
| local_artifact_path | `episodes/out12_source05_one_command_real_video_20260721/review/out12_one_command_real_video_automation/` |
| state | `AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1` |
| source | `youtube:gUwJBRUIWow`; acquired full-source MP4 SHA `8decc04ddcd805cadb77100eb5f7cbf2dc9883a32cb42aba0ed4c216fd0037cf`; 260.643991s, 1920x1080. |
| timeline | Full-source scene-boundary partition; 11 chronological cuts; opening/development/resolution; mapping coverage 1.0. Requested 300s was source-duration constrained to the complete 260.643991s source. |
| final_video | H.264 High/AAC, yuv420p, 1920x1080, 260.693767s, 142,789,781 bytes, SHA `5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584`. |
| caption_authority | Existing source-native baked text only; 468 timing cues remapped for containment readback, overlap/negative/orphan 0. No lyrics, singing, speaker, or semantic claim. |
| validation | All 13 checks passed: shipping codec/aspect/duration/start/timestamps/faststart/full decode/AV sync/loudness/cut delta/black-silence/caption containment/mapping. -14.15 LUFS, -1.44 dBTP, max adjacent cut delta 1.27 LU, max black 0.7007s, silence events 0. |
| manifest | 14 payload rows; self-integrity SHA `8c3929e22c41719ee29a565134ef128ad9a75dde7b83ab9e6cd35a526dd3c489`. |
| resume | Cache hits for analysis/caption/render/media validation in 2.095s; `render_executed=false`; final SHA unchanged; manifest revalidated. |
| preview_url | `http://127.0.0.1:8075/review/index.html`; validation listener stopped after HTTP/browser QA. |
| open_command | `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation\review\open_preview.ps1` |
| review_evidence | first/middle/last contact sheet, all-cut boundary contact sheet, waveform, cut seek map; desktop 1280 and mobile 390 no document overflow; initial paused/muted/time0; Range 206; console/media error 0. |
| decision_required | None for OUT-12 automation acceptance. Optional content inspection may record source-specific observations but cannot grant rights, production, subtitle-design, thumbnail, winner, public/publishing, or upload acceptance. |

Boundary flags:

- `internal_review_only=true`
- `automation_acceptance_granted=true`
- `rights_status=pending`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `thumbnail_acceptance=false`
- `winner_selected=false`
- `public_or_publishing_acceptance=false`
- `upload_attempted=false`
- `episodes_tracked=false`

## `clip-out11-five-source-short-portfolio-wave-v0-002`

| Field | Value |
|---|---|
| title | OUT-11 Five-Source Short Portfolio Wave 01 — human-review repairs combined review |
| purpose | Bind the first combined human review to its exact hashes, retain SOURCE-04 exact bytes as an accepted receipt, and present only repaired OUT-10/SOURCE-05 for one final hash-bound review without choosing a winner or production policy. |
| storage class | Tracked generic builders/CLI/tests/docs plus ignored same-machine source and combined packages under `episodes/`. No media is tracked or portable across clones. |
| repo_relative_path | `src/integrations/render/source_adaptive_short_candidate.py`; `src/integrations/render/five_source_short_portfolio.py`; related CLI modules; `docs/output_layer/OUT_11_FIVE_SOURCE_SHORT_PORTFOLIO_WAVE.md` |
| local_artifact_path | `episodes/out11_five_source_short_portfolio_20260720/review/out11_five_source_short_portfolio/` |
| state | `OUT11_ACCEPTED_INTERNAL_CLOSED`; repaired OUT-10/SOURCE-05 exact bytes accepted; winner false. |
| review_candidates | OUT-10 `youtube:TlnviOwLRmk`, `0.000–34.785s`, SHA `62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd`; SOURCE-05 `youtube:gUwJBRUIWow`, `202.586–260.643s`, SHA `b4a01413202e3e177a11dc42754d38f5a4b7b10cd7c7bec0aa43536d440a4969`. |
| accepted_receipt | SOURCE-04 `youtube:PQ54uUV41-k` remains SHA `465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524`, 8,523,260 bytes, `accepted_internal`; no MP4 is copied into the active review. |
| scorecard | Five rows accepted internal; OUT-10 keeps a source-specific light endpoint debt and SOURCE-05 keeps singing/lyrics/speaker unconfirmed; winner and universal production policies false. Historical scorecard SHA `4b388531fb3093fd10449d7722656d2ea8dcae8bf9e4d0783d0b63f61ed0d2c9`. |
| combined_manifest | 13 payload files; file SHA `e72de3fe092aafb72aa7dd59208c2c07e715c307ce9aac92ada61ae8e632a390`; self-integrity SHA `58276967cb2328f3a8b9ea8813bb85a4847f84e26e8bd465206c56d3e87da7bd`. |
| preview_url | clean `http://127.0.0.1:8074/index.html`; validation listener stopped after browser/HTTP QA. |
| open_command | `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out11_five_source_short_portfolio_20260720\review\out11_five_source_short_portfolio\open_preview.ps1 -Serve` |
| validation | Two repaired exact byte copies; SOURCE-04 receipt without MP4 copy; full decode/faststart/signal pass; page 200; two Range 206; desktop/mobile no overflow; clean URL paused/muted/time0; explicit QA query muted playback; exclusive playback; console/media error 0; final-six-second frame/audio evidence inspected. |
| decision_required | None. Acceptance receipt: `docs/output_layer/out11_human_acceptance_receipt.json`. Do not reopen Short repair or infer speech/lyrics, rights, winner, production, thumbnail, public, publishing, or universal subtitle/crop policy. |

Boundary flags remain false or pending:

- `internal_review_only=true`
- `human_review_pending=false`
- `acceptance_granted=true`
- `winner_selected=false`
- `rights_status=pending`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `production_image_quality_acceptance=false`
- `thumbnail_acceptance=false`
- `public_or_publishing_acceptance=false`
- `publish_attempted=false`
- `episodes_tracked=false`

## `clip-out10-third-source-short-portfolio-expansion-v0-001`

| Field | Value |
|---|---|
| title | OUT-10 Third-Source Short Portfolio Expansion v0 — human-review semantic endpoint repair |
| purpose | Preserve the accepted intro/topic/subtitle/audio/composition and extend only the endpoint through the complete consciousness-check scene after the 30.014s human-rejected predecessor. |
| storage class | Tracked builder/CLI/tests/acquisition receipt/contract plus one ignored same-machine package. Source media, official captions, plan, MP4/ASS/SRT/JPG/readback/manifest/page/scorecard remain under ignored `episodes/`. |
| repo_relative_path | `src/integrations/render/third_source_short_portfolio.py`; `src/cli/build_third_source_short_portfolio.py`; `docs/output_layer/out10_external_source_acquisition_receipt.json`; `docs/output_layer/OUT_10_THIRD_SOURCE_PORTFOLIO_EXPANSION.md` |
| local_artifact_path | `episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/` |
| state | `OUT10_ACCEPTED_INTERNAL_WITH_SOURCE_SPECIFIC_DEBT_CLOSED` |
| bounded_acquisition | Official hololive public YouTube only: metadata 5, detailed preflight 3, media download 1, selected candidate 1. No login/cookies/OAuth/DRM/geo/age/bot bypass or third-party downloader. |
| selected_source | YouTube `TlnviOwLRmk`, distinct from OUT-08 `7J5aS_pcBj4` and OUT-09 `D4i4fjs9PWc`; source video SHA `8cbb98eeaa62f539fc0a72c7e587bc961f47cb254a1aaabdb11bba7001c4a3a4`; locally derived audio SHA `159b95ffbe2cfe7c39923fa14fe4637e432683a58a0a22fcf141b8afe81f56c7`. |
| selected_slice | Source `0.000–34.785s`; intro/topic/middle unchanged. The consciousness check, patient reaction, and final punchline complete at 34.785s; a different character-introduction scene begins at 34.800s. |
| composition | Full 1920x1080 source fit on `0x0D1624` neutral matte; crop/blur/source-derived background/native-caption suppression all false. Multiple left/right characters and native name labels remain visible. |
| candidate | H.264/AAC 1080x1920 30fps yuv420p, semantic 34.785s/media 34.800s, 50 burn-in cues, SHA `62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd`; human-review repair render 1, corrective pass 0. |
| predecessor | SHA `a53d0416e17dcc682fa172ca47c7dd268a9dff2cf926bd3c44c6f5a2711134f2`, source end 30.014s, lineage `superseded_human_review_new_examination_scene_did_not_naturally_close`, acceptance false. Earlier 27.711s lineage remains nested evidence. |
| captions | Existing 46 official JA cues unchanged; four official dialogue cues added through 34.785s. |
| candidate_manifest | `candidate_manifest.json`; file SHA `093d7355c16df01aafb099c24a643183c13a11263ba9d9ebc6d1dfc041d71e80`; self-integrity SHA `e1113ae94d7586de2b1f251c38d4479484c0cb67b31bdfd260bd1ed116d4abc2`. |
| portfolio_scorecard | Superseded by OUT-11 five-source scorecard; OUT-10 is its first pending review row and winner remains false. |
| preview_url | Reviewed through the OUT-11 combined clean URL `http://127.0.0.1:8074/index.html`. |
| open_command | Use the OUT-11 combined review launcher above; do not open a separate intermediate review loop. |
| validation | Full decode/faststart/signal passed; 50-cue containment passed; human-review endpoint evidence/selection/manifest hashes bind the source mapping; final six-second frame/audio evidence inspected; exact bytes verified again inside OUT-11 combined package. |
| subtitle_debt | `portfolio_subtitle_differentiation_debt=deferred`; white style is not a general standard. Revisit after 3–5 accepted real Shorts or an explicit production subtitle-design gate. |
| decision_required | None. Exact SHA `62d4b45b...97cdd` accepted with the recorded light post-utterance cut debt; do not re-repair. |
| protected_predecessors | OUT-08 `7J5aS_pcBj4` and OUT-09 `D4i4fjs9PWc` accepted authority/media/packages are unchanged. |

Boundary flags:

- `internal_review_only=true`
- `candidate_generated=true`
- `human_review_pending=true`
- `acceptance_granted=false`
- `external_acquisition_required=false`
- `external_acquisition_authorized=true`
- `rights_status=pending`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `production_image_quality_acceptance=false`
- `thumbnail_acceptance=false`
- `public_ready=false`
- `publishing_acceptance=false`
- `publish_attempted=false`

## `clip-out09-second-source-short-repeatability-v0-001`

| Field | Value |
|---|---|
| title | OUT-09 Second-Source Short Repeatability v0 |
| purpose | Verify that the existing vertical Short path can produce one reviewable 12–60 second candidate from a real source/episode distinct from OUT-08, without a source-specific renderer branch or a broad pipeline rewrite. |
| storage class | Tracked generic builder/CLI/tests/contract plus one ignored same-machine package. Source media, captions, transcript/edit authority, plan, MP4/ASS/SRT/JPG/readback/manifest/page remain under ignored `episodes/`. |
| repo_relative_path | `src/integrations/render/second_source_short_repeatability.py`; `src/cli/build_second_source_short_repeatability.py`; `docs/output_layer/OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md` |
| local_artifact_path | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/` |
| machine_output | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/candidate_readback.json` |
| candidate_plan | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/candidate_plan.json`; original ignored input at episode root. |
| candidate_manifest | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/candidate_manifest.json`; self-integrity `50ff14e5ee9ffae0ab1cb31f33a584c346026d7674c360546302e10de24e62ff`. |
| state | `OUT09_ACCEPTED_INTERNAL_CANONICAL_MAIN`; same logical candidate after caption/access repair; `human_review_pending=false`; `acceptance_granted=true`; `review_status=accepted_internal`. |
| source_identity | YouTube ID `D4i4fjs9PWc`, different from OUT-08 `7J5aS_pcBj4`; title `【Kroniicle Animation】 Wisdom Teeth Removal Woes`; source video SHA-256 `61c06f75cf914deb0f5cc358c9a2405e2206166b10724533aff9c478f49fd938`; source audio SHA-256 `b33b3521e495edf13675b91bbbd6b89642ea28e46cd38555e77862cd6315f81b`. |
| transcript | Base Vosk EN real transcript retained for provenance; displayed text uses imported English Original JSON3 through `subtitle_track/youtube_subtitles`. Human transcript acceptance is not claimed. |
| selection_authority | Continuous `31.160–64.480s`, semantic `33.320s`, `cut_002` + `cut_003`, 12 linked caption segments. Unselected `0.000–31.160s` and `64.480–77.786848s` ranges were overlap-checked before render. Endpoint is unchanged and remains the first scene transition after caption `64.360s` and speech `64.362812s` complete. |
| candidate | Media `33.333008s`, 27 one-to-six-word JSON3 event/token-timed cues burned in over an opaque solid plate, H.264/AAC 1080x1920 30fps yuv420p faststart; MP4 SHA-256 `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`; 5,976,722 bytes. Initial `300ee360...e0c9` and failed repair `3e7ef9d8...2916` have no acceptance. |
| canonical_server_command | `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\serve_preview.ps1 -Port 8072`; run in a human-visible foreground PowerShell, keep open during review, stop with `Ctrl+C`. |
| open_command | `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Serve -Port 8072` |
| preview_url | clean `http://127.0.0.1:8072/index.html`; no QA query. Verified with page HTTP `200`, MP4 Range `206`, three probes over 54 seconds, browser close/reopen, and double-start reuse. Listener was stopped cleanly after validation and is not durable acceptance evidence. |
| media_validation | Full decode and faststart passed; output `-14.80 LUFS / -1.46 dBTP`; blackdetect/silencedetect event 0; ten frame samples extracted. |
| browser_validation | Clean human URL remained paused/muted at currentTime 0 after 2.1 seconds, manual Space play advanced currentTime, close/reopen restored the safe initial state, exact QA query played muted then paused, desktop and 375px-class mobile overflow was false, exactly two review questions were present, and console warning/error count was 0. |
| repair_result | Access-only update changed readback/index/opener/server/manifest while MP4 SHA `b6b90a4b...73da50`, ASS SHA `03df9259...9ea9`, SRT SHA `de1290f2...016f`, 27 cues, source range, endpoint, codec, and duration remained unchanged. Unknown port owners are not killed and no alternate port is selected. Browser media-range disconnects are treated as normal client exits. |
| acceptance | User confirmed subtitle/audio agreement, expected short-cue switching/readability, no immediate autoplay or sudden audio, foreground-server access continuity, and a complete non-mid-speech endpoint; overall accepted for internal review. Bound only to exact MP4 SHA `b6b90a4b...73da50`. |
| source_specific_observation | `source_specific_caption_band_suppression_observed_acceptable_not_generalized`: the upper/lower blurred or mosaic-like canvas is the result of excluding the lower 74px native-caption band and filling 9:16 space from source rect `0,0,640,286`. Acceptable here only; not a shared aesthetic/design rule or production subtitle acceptance. |
| merge_preflight | origin/main `29a1a519` and branch `17436ad` produced the same two known OUT-06 wrap failures; default no-policy vertical render command SHA matched at `a863ee1a...7ebf`; branch-only regression false. |
| review_questions | Consumed by the accepted internal decision; no further OUT-09 review loop is open. |
| next_action | Keep `OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION` as the only data-only successor candidate. Do not implement without explicit approval or infer rights, production/public use, publishing, thumbnail, portability, or generalized caption-suppression acceptance. |

Boundary flags remain false or pending:

- `internal_review_only=true`
- `human_review_pending=false`
- `acceptance_granted=true`
- `candidate_01_acceptance=accepted_internal`
- `human_transcript_acceptance_claimed=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `thumbnail_acceptance=false`
- `public_ready=false`
- `publishing_acceptance=false`
- `publish_attempted=false`
- `out10_successor_data_only=true`

## `clip-out08-real-unused-range-short-minibatch-v0-001`

| Field | Value |
|---|---|
| title | OUT-08 Real Unused-Range Vertical Shorts Mini-Batch v0 |
| purpose | Turn previously unused real source ranges into two content-distinct vertical Shorts candidates on one direct-play review page, so a human can judge each as a whole editing unit without reopening thumbnail work. |
| storage class | Tracked builder/CLI/tests/contract plus one ignored same-machine package. Source media, generated MP4/ASS/SRT/JPG, plan/readback/manifest, and page remain outside Git under `episodes/`. |
| repo_relative_path | `src/integrations/render/real_unused_range_short_minibatch.py`; `src/cli/build_real_unused_range_short_minibatch.py`; `docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/batch_readback.json` |
| scan_readback | `episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/candidate_scan_readback.json` |
| candidate_plan | `episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/candidate_plan.json` |
| batch_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/batch_manifest.json`; all 16 non-manifest package payloads byte-hashed; self-integrity `22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4`. |
| state | `OUT08_ACCEPTED_INTERNAL_CANONICAL_MAIN`; contract repair `OUT08_CUT009_FULLY_EXCLUDED_CONTRACT_REPAIRED_REVIEW_READY`; target `2`, minimum `1`, actual `2`; batch `accepted_all_internal`; both candidates `accepted_internal`; winner none. |
| source_inputs | YouTube ID `7J5aS_pcBj4`; source video SHA-256 `6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`; source audio SHA-256 `46e4bc9e26d52ed8f83b0b4088ddcd6ddac5a873fa1bb4a440c209834f026671`; official caption SHA-256 `3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`; current edit/cut authority read without mutation. |
| candidate_01 | `cut_004` `50.868–60.277` + `cut_005` `60.277–79.163`; semantic `28.295s`, media `28.266667s`, 17 subtitles; MP4 SHA-256 `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a`. |
| candidate_02 | `cut_006` tail `81.298–98.315` + `cut_007` `98.315–116.467` + `cut_008` `116.934–135.219`; semantic `53.454s`, media `53.466667s`, 54 subtitles; MP4 SHA-256 `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b`. |
| rejected_cut_boundary | `cut_009` remains final decision `reject`; its `135.219–144.000` source-time interval is fully excluded from candidate ranges regardless of ID, label, or dependent flag. |
| navigation_images | `candidate_01_navigation.jpg` and `candidate_02_navigation.jpg` are final-video frames for navigation only; no headline/mask/decoration/reference pixels, and no thumbnail acceptance is claimed. |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out08_real_unused_range_short_minibatch\open_preview.ps1 -Port 8071` |
| preview_url | `http://127.0.0.1:8071/index.html`; last verified on port `8071` through the exact `src.cli.serve_review` route with page HTTP `200` and MP4 Range `206`. The listener PID is intentionally not durable state. |
| media_validation | Both H.264/AAC 1080x1920 30fps yuv420p faststart; full decode passed; no black interval >=0.5s; no silence interval >=1.5s at -50dB. |
| browser_validation | Both current videos reached `readyState=4` with media error `null`; desktop/mobile horizontal overflow was absent and console was clean. The repaired package returned HTTP `200` and Range `206`; native-control direct seek/currentTime advance was not observed reliably. |
| review_status | User reply 「両方問題ありません」 accepted both exact candidates for internal use across whole-edit coherence, tempo, boundaries, subtitle readability, and A/V continuity. Missing local package or server does not revoke acceptance. Navigation images do not open a thumbnail decision. |
| optional_recovery_proof | Remote branch `codex/out-08-private-review-package-recovery-v0` at `d1f44d17e9747419f307706cad802aefdd012efd` is parked optional noncanonical infra proof and is not merged into the source lineage or main. |
| next_action | Treat OUT-08 as closed. Keep `OUT09_SECOND_SOURCE_SHORT_REPEATABILITY` as data-only successor until a later implementation approval. |

Boundary flags remain false or pending:

- `internal_review_only=true`
- `human_review_pending=false`
- `acceptance_granted=true`
- `batch_acceptance=accepted_all_internal`
- `candidate_01_acceptance=accepted_internal`
- `candidate_02_acceptance=accepted_internal`
- `authority_mutated=false`
- `cut009_final_cut_decision=reject`
- `navigation_frames_are_thumbnails=false`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights_status=pending`
- `public_ready=false`
- `publishing_acceptance=false`
- `publish_attempted=false`

## `clip-out07-shorts-poster-frame-direction-proof-v0-001`

| Field | Value |
|---|---|
| title | OUT-07 Parked Viable Noncanonical Cover Receipt v0 |
| purpose | Preserve the verified Thank semantic proxy and the human finding that it is natural and provisionally usable for this episode, while closing OUT-07 without selection, canonicalization, standard reuse, or additional thumbnail iteration. |
| storage class | Tracked strict/proxy builders, CLI, tests, hash-only rebuild contract, and docs; ignored Thank source, caption authority, proxy pixels, previews, readbacks, manifest, and page. `episodes/` remains untracked. |
| repo_relative_path | `src/integrations/render/out07_direction_proxy.py`; `src/cli/build_out07_direction_proxy.py`; `src/integrations/render/out07_native_cover.py`; `src/integrations/render/out07_reconstitution.py`; `artifacts/ACTIVE_REBUILD.json` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/cover_direction_proxy_readback.json` |
| combined_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/combined_review_manifest.json` |
| determinism_receipt | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/determinism_receipt.json` |
| evidence_revision | `thank-6f78657e-native-cover-direction-proxy-v1` |
| current_state | `OUT07_PARKED_WITH_VIABLE_NONCANONICAL_COVER_AND_MAIN_LANDED` |
| source_inputs | Thank source `6f78657e...103a`; Planner source `e2206cef...1889`; byte equivalence is not claimed. Official caption SHA is `3c15535f...169919`; its tracked contract contains hashes/timing/segments, not plaintext. |
| mapping | source target `22.858s`, nearest decoded frame `22.866667s`, sequence `11.930s`, `cut_003`, `sub_010` |
| historical_cover_evidence | `native_shorts_cover_direction_proxy_1080x1920.png`; SHA-256 `e7aaae24401b5b6c75e13926329af19c8a59008dd3c93229735d7465da2f18da`; classification `cover_direction_semantic_proxy`; local scene/authority are observed, Planner continuity is inferred, Planner pixel equivalence is unknown, and selected-by-human remains false. |
| preview_artifacts | `cover_list_preview.jpg` (405x720), `cover_shorts_ui_overlay_preview.jpg` (405x720), `cover_center_4x5.jpg` (864x1080), and `mapped_source_frame_1920x1080.png` (1920x1080) |
| pixel_policy | Existing source-derived reframe and subtitle pixels only; poster-specific abstract background, auxiliary copy, masks, collage, and third-party pixels are false. |
| exact_baseline | SHA `2c1c59bc...2d18` remains `accepted_historical_fact`; `exact_baseline_available=false` on Thank. The unchanged strict route retains SHA/size/duration, byte-copy, and acceptance-inheritance gates. |
| availability | `local_artifact_available=true` as historical local evidence; `cover_direction_review_available=false`; `human_entrypoint=null`; `portable_entrypoint=null`; `cover_direction_acceptance=not_granted`. |
| historical_open_command | Thank host receipt only: `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_native_shorts_cover_direction_proxy\open_preview.ps1 -Port 8071`; do not present it as the current review entrypoint. |
| historical_preview_url | Thank host receipt only: `http://127.0.0.1:8071/index.html`; review server stopped after closure. |
| determinism | Same fixed inputs built twice with every package byte equal; core `deb93e2f...652` and package `0eeb4958...832`; manifest inventory and self-integrity pass. |
| review_status | `PARK_PROVISIONAL_USABLE`: viable and provisionally usable for this episode, but not selected, canonical, default, reproducible, or accepted as a thumbnail system. No additional OUT-07 thumbnail iteration is allowed. Revisit only after 3–5 real Shorts exist. |
| next_action | Keep as parked predecessor evidence. Do not reopen OUT-07 thumbnail iteration; revisit only after 3–5 real Shorts and an explicit successor scope. |

Boundary flags remain false or pending:

- `selected_thumbnail=null`
- `viable_candidate=true`
- `provisionally_usable_for_episode=true`
- `selected_by_human=false`
- `human_selected=false`
- `selection_status=deferred`
- `canonical_pattern=false`
- `default_template=false`
- `reuse_as_standard=false`
- `final_thumbnail_system_acceptance=false`
- `reference_collection_process_valid=true`
- `reference_to_output_lineage=weak`
- `accidental_success_not_ruled_out=true`
- `revisit_after_real_short_count=3_to_5`
- `additional_OUT07_thumbnail_iteration=prohibited`
- `exact_baseline_available=false`
- `accepted_baseline_status=accepted_historical_fact`
- `cover_direction_review_available=false`
- `human_review_decision=PARK_PROVISIONAL_USABLE`
- `cover_direction_acceptance=not_granted`
- `h1_full_short_integration=false`
- `publish_ready=false`
- `rights_status=pending`
- `production_acceptance=false`
- `public_or_publishing_acceptance=false`
- `upload_attempted=false`

## `clip-out07-internal-operator-delivery-pack-v0-001`

Historical lineage only; this is not the current review target and its ignored
local package may be absent.

| Field | Value |
|---|---|
| title | OUT-07 Internal Operator Delivery Pack v0 |
| purpose | Bundle the accepted OUT-06 MP4 with source-frame-derived thumbnail directions, clean Japanese audience copy, and separate operator-only attribution/gate readback for internal review. |
| storage class | Tracked historical builder/CLI/tests/contract plus an ignored same-machine delivery package only if retained on the host. Source media, generated MP4 copy, and thumbnails remain outside Git. |
| repo_relative_path | `src/integrations/render/operator_delivery_pack.py`; `src/cli/build_operator_delivery_pack.py`; `docs/output_layer/OUT_07_INTERNAL_OPERATOR_DELIVERY_PACK.md` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/operator_delivery_readback.json` |
| delivery_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/delivery_manifest.json` |
| source_inputs | Accepted OUT-06 readback/video and retained source video frame evidence. |
| open_command | If the historical local package is retained: `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out07_internal_operator_delivery_pack\open_delivery.ps1` |
| preview_url | Historical `http://127.0.0.1:8070/index.html` only while that optional retained package server is running; it is not the current review URL. |
| recommended_thumbnail | `null`; the former context/tension/payoff directions are all `user_rejected`. |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_internal_operator_delivery_pack/assets/thumbnail_direction_contact_sheet.jpg` |
| validation_command | `uvx --with Pillow pytest -q tests/test_operator_delivery_pack.py tests/test_complete_narrative_short.py tests/test_vertical_short_candidate.py tests/test_review_range_server.py tests/test_docs_dashboard.py`; required-field and copy-separation assertions; actual package generation twice for byte-stability; protected OUT-03..OUT-06/human-preview digest equality; unchanged media hashes; manifest self-integrity; Range 206; browser Japanese copy/fallback/folded-details/image/video/seek/no-overflow QA; deterministic dashboard regeneration; `git diff --check`; `git ls-files episodes`. |
| review_status | Historical lineage only. Context/tension/payoff are rejected evidence and this artifact must not be reopened as the current selection surface. |
| recommended_thumbnail_sha256 | `null` |
| contact_sheet_sha256 | Rebuilt rejected-evidence sheet; candidate review moved to `clip-out07-shorts-poster-frame-direction-proof-v0-001`. |
| output_video_sha256 | `02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0` |
| operator_delivery_readback_sha256 | `1d62964e3b8ed5b7b7ff6f6fe5f0ca6d098cf08b12fdaca5e670d6fd68a47211` |
| delivery_manifest_sha256 | `77187a87ba77b2aa8bb7c1256a7d7ba3e96ef51bf80dc91ea978ca575ac486a3` |
| next_action | Use only as accepted-video/metadata and rejected-thumbnail predecessor evidence for the current 9:16 poster proof. |

Boundary flags remain false or pending:

- `status=internal_operator_draft`
- `selected_thumbnail=null`
- `poster_decision_status=human_selection_required`
- `legacy_thumbnail_status=user_rejected`
- `operator_copy_ready=true`
- `publish_ready=false`
- `source_attribution_status=operator_decision_required`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `public_or_publishing_acceptance=false`
- `rights_status=pending`
- `upload_attempted=false`
- `thumbnail_upload_attempted=false`
- `metadata_update_attempted=false`
- `visibility_update_attempted=false`
- `visibility=operator_decision_required`
- `made_for_kids=operator_decision_required`
- `scheduled_at=null`

## `clip-out06-complete-narrative-short-delivery-candidate-v0-001`

| Field | Value |
|---|---|
| title | OUT-06 Complete Narrative Short Delivery Candidate v0 |
| purpose | Preserve the accepted OUT-05 opening and append authoritative `cut_003` as one directly reviewable introduction-development-close internal vertical short, now accepted after the 2026-07-12 bounded subtitle-wrap and seekability repairs for the same artifact ID. |
| storage class | Tracked builder/CLI/tests/contract plus ignored same-machine delivery package. Source media and generated MP4 remain outside Git. |
| repo_relative_path | `src/integrations/render/complete_narrative_short.py`; `src/cli/build_complete_narrative_short.py`; `docs/output_layer/OUT_06_COMPLETE_NARRATIVE_SHORT_DELIVERY_CANDIDATE.md` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/candidate_readback.json` |
| delivery_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/delivery_manifest.json` |
| source_inputs | Accepted OUT-05 readback/video and accepted OUT-04 source timeline, unchanged retained source video/audio, edit pack, transcript, material ledger, rights manifest, cut decision packet, and operator proxy authority. |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out06_complete_narrative_short_delivery_candidate\open_preview.ps1` |
| preview_url | `http://127.0.0.1:8060/index.html` while the retained byte-range local server is running. |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/assets/frame_qa_contact_sheet.jpg` |
| poster_frame | `episodes/jp_pilot01_hololive_bancho_20260525/review/out06_complete_narrative_short_delivery_candidate/assets/poster_frame.jpg`; extracted from the final video, not a decorated thumbnail. |
| validation_command | `uvx --with Pillow pytest -q tests/test_complete_narrative_short.py tests/test_vertical_short_candidate.py tests/test_review_range_server.py`; parse plan/readback/manifest; ffprobe; full FFmpeg decode; loudness/true-peak and decoded PCM boundary analysis; 16-point frame inspection; Range 206 check; browser seek QA; protected tree digests; `git diff --check`; `git ls-files episodes`. |
| review_status | Accepted after bounded repair on this machine: tempo and audio/video continuity accepted; six reported subtitle wraps repaired and accepted; `cut_001 -> cut_002 -> cut_003`, semantic `38.638s`, media `38.633333s`, hard cuts at `6.840s` and `11.678s`, 29 measured/wrapped ASS cues, H.264/AAC 1080x1920 30fps yuv420p faststart, Range seek route and browser seek QA passed. |
| cut003_authority | `keep + needs_review`; `proxy_decision=proceed_with_limitations`; `context_risk_handling=keep_retained_risk_visible`; authority unchanged. |
| reframe | Reused accepted OUT-05 `full_16_9_fit_source_derived_blurred_canvas`; no new comparison or micro-tuning loop. |
| audio | Input `-19.21 LUFS / -2.11 dBTP`; normalized output `-14.39 LUFS / -1.49 dBTP`; both boundary PCM analyses passed without click/dropout risk. |
| output_sha256 | `02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0` |
| candidate_readback_sha256 | `0f8ffcd19c3a1b48cca76cf01dd31c4309f405ac3ced3553ba8d6f29e278f9a2` |
| delivery_manifest_sha256 | `e3be1ec84d97fe472df2c9fb9cdf1a334084a0f727173835a9e0428f6bbb95d0` |
| next_action | Use as the immutable accepted video predecessor for OUT-07 internal operator delivery-pack work. Do not infer rights, production/public use, thumbnail upload, metadata publication, visibility, made-for-kids, or publishing approval. |

Boundary flags remain false or pending:

- `internal_review_only=true`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights_status=pending`
- `public_ready=false`
- `publishing_acceptance=false`
- `publish_attempted=false`

## `clip-out05-vertical-short-internal-candidate-v0-001`

| Field | Value |
|---|---|
| title | OUT-05 Vertical Short Internal Candidate v0 |
| purpose | Preserve the accepted OUT-04 timeline while producing one directly reviewable 1080x1920 internal vertical-format candidate with explicit reframe, subtitle, audio, provenance, and closed-gate readback. |
| storage class | Tracked builder/CLI/tests/contract plus ignored same-machine vertical candidate bundle. Source media and generated MP4 remain outside Git. |
| repo_relative_path | `src/integrations/render/vertical_short_candidate.py`; `src/cli/build_vertical_short_candidate.py`; `docs/output_layer/OUT_05_VERTICAL_SHORT_INTERNAL_CANDIDATE.md` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out05_vertical_short_internal_candidate/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out05_vertical_short_internal_candidate/candidate_readback.json` |
| source_inputs | Accepted OUT-04 readback/video and unchanged retained source video/audio, edit pack, transcript, material ledger, rights manifest, and cut decisions. |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out05_vertical_short_internal_candidate\open_preview.ps1` |
| validation_command | `uvx --with Pillow pytest -q tests/test_vertical_short_candidate.py tests/test_editorial_sequence.py`; parse JSON; ffprobe; full FFmpeg decode; loudness/true-peak measure; frame/contact-sheet inspection; browser DOM/media/layout readback; protected tree digests; `git diff --check`; `git ls-files episodes`. |
| review_status | `accepted` |
| reviewed_at | `2026-07-12 JST` |
| acceptance_scope | OUT-05 internal vertical short candidate only. |
| vertical_framing_subject_action_preservation | `pass` |
| subtitle_position_wrap_readability | `pass` |
| audio_boundary_screen_export_integrity | `pass` |
| review_evidence | Unchanged `cut_001 -> cut_002`, hard cut at `6.840s`, total `11.700s` within tolerance, 9 measured/wrapped ASS cues, H.264/AAC 1080x1920 30fps yuv420p faststart, browser readyState `4`, no media error, console warning/error, or horizontal overflow. |
| reframe | `full_16_9_fit_source_derived_blurred_canvas`; still-frame comparison rejected the explicit anchor crop for left/right information loss and held the bounded hybrid because it lost edge context without a clear focal gain. |
| audio | Input `-19.22 LUFS / -2.11 dBTP`; normalized output `-14.06 LUFS / -1.49 dBTP`. |
| output_sha256 | `d2a75ed5f85a0869d4178917c258624ccf083bbefce33ab468549f93a982b827` |
| rights_approval | `pending` (unchanged) |
| production_acceptance | `false` |
| production_subtitle_design_acceptance | `false` |
| public_or_publishing_acceptance | `false` |
| implementation_commit | `e2d0711` |
| next_action | Use accepted OUT-05 as the immutable opening for OUT-06; do not infer rights, production, subtitle-design, publishing, or public acceptance. |

Boundary flags remain false or pending:

- `internal_review_only=true`
- `vertical_format_candidate=true`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights=pending`
- `public_ready=false`
- `publishing=false`
- `publish_attempted=false`

## `clip-out04-editorial-representative-sequence-v0-001`

| Field | Value |
|---|---|
| title | OUT-04 Editorial Representative Sequence v0 |
| purpose | Compose retained real selected cuts into one playable sequence so editorial order, hard-cut continuity, pacing, and subtitle/audio continuity can be reviewed in one playback. |
| storage class | Tracked builder/CLI/tests/contract plus ignored same-machine sequence bundle. Source media and generated MP4 remain outside Git. |
| repo_relative_path | `src/integrations/render/editorial_sequence.py`; `src/cli/build_editorial_sequence.py`; `docs/output_layer/OUT_04_EDITORIAL_REPRESENTATIVE_SEQUENCE.md` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out04_editorial_representative_sequence/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out04_editorial_representative_sequence/sequence_readback.json` |
| source_inputs | Current JP-Pilot edit pack, accepted final cut decisions, transcript/subtitles, material ledger, rights manifest, retained source video/audio, and accepted OUT-03 as the single-cut predecessor. |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out04_editorial_representative_sequence\open_preview.ps1` |
| validation_command | `uvx pytest -q tests/test_editorial_sequence.py tests/test_selected_cut_proof.py tests/test_tiny_render.py tests/test_subtitle_generation.py`; parse readback JSON; ffprobe MP4; browser DOM/media/layout readback; compare repeat-generation hashes; `git diff --check`; `git ls-files episodes`. |
| review_status | `accepted` |
| reviewed_at | `2026-07-11 JST` |
| acceptance_scope | OUT-04 internal editorial representative sequence only. |
| editorial_coherence | `pass` |
| hard_cut_boundary | `pass` |
| hard_cut_abrupt_or_confusing | `false` |
| subtitle_audio_continuity | `pass` |
| audio_dropout | `none_observed` |
| transition_visual_corruption | `none_observed` |
| reviewer_note | 場面転換前後を含めて画面上の乱れは確認されなかった |
| review_evidence | Evidence remains `cut_001 -> cut_002`, hard cut at `6.840s`, total `11.678s`, 9 rebased subtitles, H.264/AAC 1920x1080 30fps, one video/audio stream, browser readyState `4`, no media error or horizontal overflow. |
| rights_approval | `pending` (unchanged) |
| production_acceptance | `false` |
| public_or_publishing_acceptance | `false` |
| implementation_commit | `b9c785f` |
| output_sha256 | `9fa17e8566acd3e4237793840edffa2485350575876c99b04bed065a8ae6e19a` |
| next_action | Use accepted OUT-04 as the immutable editorial baseline for OUT-05 vertical-short candidate work; do not infer rights, production, system-wide subtitle-design, publishing, or public acceptance. |

Boundary flags remain false or pending:

- `diagnostic_only=true`
- `rights_status=pending`
- `production_candidate=false`
- `production_ready=false`
- `production_acceptance=false`
- `publishing_acceptance=false`
- `public_ready=false`
- `publish_attempted=false`

## `clip-out03-real-local-selected-cut-proof-v0-001`

| Field | Value |
|---|---|
| title | OUT-03 Real-Local Selected-Cut Review Proof v0 |
| purpose | Connect one real retained source segment, non-fixture transcript, selected cut, subtitles, playable diagnostic MP4, and compact readback through one human entrypoint. |
| storage class | Tracked builder/tests/contract plus ignored same-machine review bundle. Source media and generated MP4 remain outside Git. |
| repo_relative_path | `src/integrations/render/selected_cut_proof.py`; `src/cli/build_selected_cut_proof.py`; `docs/output_layer/OUT_03_REAL_LOCAL_SELECTED_CUT_PROOF.md` |
| local_artifact_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/out03_real_local_selected_cut_proof/` |
| machine_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/out03_real_local_selected_cut_proof/proof_readback.json` |
| source_inputs | JP-Pilot `edit_pack.json`, `transcript.json`, material ledger, rights manifest, `cut_002` diagnostic proof MP4, and representative visual proof readback. |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out03_real_local_selected_cut_proof\open_preview.ps1` |
| validation_command | `uvx pytest -q tests/test_selected_cut_proof.py`; run the builder twice and compare SHA-256; parse JSON; ffprobe copied MP4; browser DOM/media/layout readback; `git diff --check`; `git ls-files episodes`. |
| review_status | `accepted` |
| reviewed_at | `2026-07-11 JST` |
| review_scope | OUT-03 internal real-local selected-cut milestone only. |
| playback | `pass` |
| cut_boundary | `pass` |
| content_audio_match | `pass` |
| subtitle_timing | `pass` |
| subtitle_readability | `pass` |
| review_evidence | Page clarity passed. Evidence remains `cut_002`, source `12.329`-`17.167`, duration `4.838s`, H.264/AAC 1920x1080, transcript `subtitle_track` / `youtube_subtitles` with `real_transcript=true`, linked to `seg_000008` and `seg_000009`. |
| rights_approval | `pending` (unchanged) |
| production_acceptance | `false` |
| public_or_publishing_acceptance | `false` |
| implementation_commit | `01b42cd` |
| next_action | Use accepted OUT-03 as the canonical baseline for OUT-04 editorial representative sequence work; do not infer rights, production, creative, publishing, system-wide subtitle-design, or public acceptance. |

Boundary flags remain false or pending:

- `diagnostic_only=true`
- `rights_status=pending`
- `production_candidate=false`
- `production_ready=false`
- `publishing_acceptance=false`
- `public_ready=false`

## `clip-out02-local-fixture-output-proof-smoke-v0-001`

| Field | Value |
|---|---|
| title | OUT-02 Local Fixture Output Proof Smoke v0 |
| purpose | Convert OUT-01 `proof_missing` into a tracked synthetic fixture proof package with parseable JSON, SRT subtitle draft, static HTML timeline, and remaining-gate readback. |
| storage class | Tracked local fixture artifact under `docs/output_layer/`; synthetic data only. It does not open source URLs, fetch/download external media, run yt-dlp, use OAuth/API, approve rights, create production render, mark public-ready, upload, or track `episodes/`. |
| repo_relative_path | `docs/output_layer/local_fixture_output_proof/proof_manifest.json; docs/output_layer/local_fixture_output_proof/proof_readback.json; docs/output_layer/local_fixture_output_proof/proof_timeline.html; docs/output_layer/local_fixture_output_proof/fixture_edit_pack.json; docs/output_layer/local_fixture_output_proof/fixture_subtitles.srt; docs/output_layer/local_fixture_output_proof/README.md` |
| machine_output | `docs/output_layer/video_output_gap_log.json` records `proof_status=local_fixture_output_proof_present` and `recommended_next_slice=OUT-03-selected-cut-proof-link`. |
| source_inputs | Synthetic fixture rows generated by `tools/output_layer/build_output_layer_gap_report.py`; no external media. |
| open_command | `start docs\output_layer\local_fixture_output_proof\proof_timeline.html` |
| generated_from | `python -m src.cli.main build-output-layer-gap-report --format json` |
| validation_command | JSON parse checks for gap log, proof manifest, proof readback, and fixture edit pack; targeted pytest for output layer and asset-fetch boundary; `git diff --check`; `git ls-files episodes`. |
| review_status | Ready as a local fixture output proof. It proves the package/readback shape only; real source material, real transcript, production render, rights approval, and public/upload readiness remain absent or gated. |
| next_action | Use `OUT-03-selected-cut-proof-link` to connect selected cut ids to proof artifacts, or open a separately approved local-material/private-fetch smoke before any real-media output proof. |

Boundary flags remain false:

- `source_kind=synthetic_fixture`
- `external_media_used=false`
- `network_used=false`
- `fetch_authorized=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`
- `public_upload_attempted=false`
- `production_render_attempted=false`

## `clip-int01-parallel-lane-aggregation-v0-001`

| Field | Value |
|---|---|
| title | INT-01 Parallel Lane Aggregation / Thread Registry Sync v0 |
| purpose | Merge TRI-01, HUB-01, OUT-01, and EWS-05 parallel lane outputs onto one reviewable integration branch and record the cross-terminal registry for the next worker. |
| storage class | Tracked local Markdown/JSON integration report plus thread registry. It does not open source URLs, fetch media, call external APIs, approve rights, mark production/public ready, merge main, or create a PR. |
| repo_relative_path | `docs/integration/int01_parallel_lane_aggregation_report.json; docs/integration/int01_parallel_lane_aggregation_report.md; docs/THREAD_REGISTRY.md` |
| machine_output | `docs/integration/int01_parallel_lane_aggregation_report.json` |
| source_inputs | `origin/codex/tri-01-safety-overcapture-triage-v0`; `origin/codex/hub-01-external-source-registry-v0`; `origin/codex/out-01-output-layer-gap-logger-v0`; `origin/codex/ews-05-human-ok-fetch-prep-ready-v0` |
| open_command | `type docs\integration\int01_parallel_lane_aggregation_report.md` |
| validation_command | Targeted lane tests, CLI smokes for external source registry/output gap/docs dashboard, JSON parse checks, `git diff --check`, and `git ls-files episodes`. |
| review_status | Ready for integration review after targeted local validation. The shared CLI dispatcher preserves HUB, OUT, and EWS subcommands. Central docs/dashboard conflicts are recorded in `docs/THREAD_REGISTRY.md` and the INT-01 report. |
| next_action | Review INT-01, then branch OUT-02 from `codex/int-01-parallel-lane-aggregation-v0` if the integration is accepted. Merge into main only after manual review of the combined central docs/dashboard surface. |

Boundary flags remain false:

- `source_urls_opened=false`
- `network_fetch_used=false`
- `media_downloaded=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`
- `main_merged=false`
- `pull_request_created=false`

## `clip-hub01-external-source-registry-v0-001`

| Field | Value |
|---|---|
| title | HUB-01 External Source Hub / RSS Intake Stub v0 |
| purpose | Normalize local RSS XML and manual source seed fixtures into a safe external source candidate registry for later source planning review. |
| storage class | Tracked local JSON/fixture/code artifact; offline-only. It does not fetch live RSS, open source URLs, call metadata APIs, download media, approve rights, or mark anything production/public ready. |
| repo_relative_path | `docs/external_sources/external_source_registry.json` |
| machine_output | `docs/external_sources/external_source_registry.json` |
| source_inputs | `samples/external_sources/rss_fixture.xml`; `samples/external_sources/manual_source_seeds.json` |
| open_command | `type docs\external_sources\external_source_registry.json` |
| generated_from | `uvx python -m src.cli.main build-external-source-registry --format json` |
| validation_command | `uvx pytest -q tests/test_external_source_registry.py` plus JSON parse, `git diff --check`, and `git ls-files episodes`. |
| review_status | Ready as an offline source-intake stub. Registry readback has 4 records: 2 RSS fixture items and 2 manual seeds. All records keep `network_used=false`, `media_downloaded=false`, `rights_approved=false`, and `public_ready=false`. |
| next_action | Review registry rows before any HUB-02 mapping into CPD source planning. Do not auto-advance rows to source identity OK or fetch-ready. |

Boundary flags remain false:

- `network_used=false`
- `source_urls_opened=false`
- `media_downloaded=false`
- `rights_approved=false`
- `public_ready=false`

## `clip-ews05-human-ok-fetch-prep-ready-package-v0-001`

| Field | Value |
|---|---|
| title | EWS-05 Human OK Decision Application / Fetch-Prep Ready Package v0 |
| purpose | Record the human operator's source identity OK report and package the resulting ready-for-future-private-fetch-plan readback for the current CPD-12 source-backed candidate. |
| storage class | Tracked local JSON/Markdown package; consumes the EWS-01 workspace plan, EWS-03 decision intake, EWS-04 fetch-prep planner, and a human operator report. No worker URL opening, fetch/download, media, transcript, render, thumbnail, upload, auth, rights approval, production-ready, or public-ready state is created. |
| repo_relative_path | `docs/content_planning/source_fetch_prep_ready_package.json; docs/content_planning/source_fetch_prep_ready_package.md; docs/content_planning/source_identity_human_ok_decision.json` |
| machine_output | `source_identity.decision.json` and `source_fetch_prep_plan.json` inside an explicit tempdir smoke workspace; tracked portable readback stays under `docs/content_planning/`. |
| source_inputs | `docs/content_planning/episode_workspace_plan.json`; `docs/content_planning/automation_contract.json`; `docs/content_planning/source_identity_human_ok_decision.json`; explicit tempdir workspace |
| open_command | `type docs\content_planning\source_fetch_prep_ready_package.json` |
| validation_command | Tempdir init/record/plan smoke, JSON parse checks, `uvx pytest -q tests/test_episode_workspace.py tests/test_docs_dashboard.py`, `git diff --check`, and `git ls-files episodes`. |
| review_status | Ready as the human OK fetch-prep package. The human report says the URL opens, candidate intent is consistent, and content matches the explanation; the worker did not open the URL. The generated plan reaches `prep_state=ready_for_future_private_fetch_plan` while preserving `fetch_authorized=false`, `media_downloaded=false`, `rights_approved=false`, and `public_ready=false`. |
| next_action | Require explicit private fetch smoke approval before any source fetch/download lane. Do not treat this package as rights/public/production/upload approval. |

Package boundary flags remain false:

- `worker_source_url_opened=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `transcript_generated=false`
- `render_generated=false`
- `thumbnail_generated=false`
- `upload_created=false`
- `rights_approved=false`
- `public_ready=false`

## `clip-ews04-source-fetch-prep-planner-v0-001`

| Field | Value |
|---|---|
| title | EWS-04 Source Fetch-Prep Planner / Decision-Gated Local Plan v0 |
| purpose | Convert an explicit EWS workspace plus `source_identity.decision.json` into a local source fetch-prep plan or a blocked plan with machine-readable reason. |
| storage class | Code-backed local JSON artifact; consumes an inspected workspace, automation contract, and EWS-03 decision record. No source URL opening, fetch/download, media, transcript, render, thumbnail, upload, auth, rights, or public-ready state is created. |
| repo_relative_path | `src/pipeline/episode_workspace.py` |
| machine_output | `source_fetch_prep_plan.json` inside an explicit local/temp workspace, plus parseable stdout JSON. |
| source_inputs | explicit materialized workspace path; `docs/content_planning/episode_workspace_plan.json`; `docs/content_planning/automation_contract.json`; workspace `source_identity.decision.json` |
| open_command | `python -m src.cli.main plan-source-fetch-prep --workspace <workspace> --format json` |
| validation_command | `uvx pytest -q tests/test_episode_workspace.py` plus tempdir init/inspect/prepare/record/plan smoke and JSON parse checks. |
| review_status | Ready as the local fetch-prep planning surface. Missing decisions block as `source_identity_decision_missing`; `pending`, `ng`, and `hold` decisions block with source identity reasons; `ok` plus `allows_fetch_prep=true` returns `prep_state=ready_for_future_private_fetch_plan` while preserving `fetch_authorized=false`, `media_downloaded=false`, `rights_approved=false`, and `public_ready=false`. |
| next_action | Use the plan to decide whether a later private/local fetch smoke slice should be explicitly opened. Do not fetch media or open source/public/rights gates from this plan. |

Fetch-prep planner boundary flags remain false:

- `source_url_opened=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `transcript_created=false`
- `render_created=false`
- `thumbnail_created=false`
- `upload_created=false`
- `rights_approved=false`
- `public_ready=false`

## `clip-ews03-source-identity-decision-intake-v0-001`

| Field | Value |
|---|---|
| title | EWS-03 Source Identity Decision Intake / Local Decision Record v0 |
| purpose | Create a pending local source identity decision template and validate/write a human-provided `pending` / `ok` / `ng` / `hold` decision record into an explicit workspace. |
| storage class | Code-backed local JSON artifact; consumes an inspected workspace and a local decision file. No source URL opening, fetch authorization, media, transcript, render, thumbnail, upload, auth, rights, or public-ready state is created. |
| repo_relative_path | `src/pipeline/episode_workspace.py` |
| machine_output | `source_identity_decision.template.json` and `source_identity.decision.json` inside an explicit local/temp workspace. |
| source_inputs | explicit materialized workspace path; `docs/content_planning/episode_workspace_plan.json`; `docs/content_planning/automation_contract.json`; local decision JSON for recording |
| open_command | `python -m src.cli.main prepare-source-identity-decision --workspace <workspace> --format json` |
| prepare_command | `python -m src.cli.main prepare-source-identity-decision --workspace <workspace> --format json` |
| record_command | `python -m src.cli.main record-source-identity-decision --workspace <workspace> --decision <decision.json> --format json` |
| validation_command | `python -m pytest -q tests/test_episode_workspace.py` plus tempdir init/inspect/prepare/record smoke and JSON parse checks. |
| review_status | Ready as the local source identity decision intake. Generated templates default to `identity_decision=pending`; records reject unknown values; `ok` requires reviewer or notes; `allows_fetch_prep=true` only for `ok`, while `fetch_authorized=false`, `rights_approved=false`, and `public_ready=false` always remain. |
| next_action | Use the decision record as the input to a later fetch-prep planning slice. Do not fetch media or open source/public/rights gates from this record. |

Decision intake boundary flags remain false:

- `source_url_opened=false`
- `fetch_authorized=false`
- `media_files_created=false`
- `transcript_generated=false`
- `render_generated=false`
- `thumbnail_generated=false`
- `rights_approved=false`
- `public_ready=false`

## `clip-ews02-episode-workspace-inspector-v0-001`

| Field | Value |
|---|---|
| title | EWS-02 Episode Workspace Inspector / Manifest Consumer v0 |
| purpose | Read a materialized local/temp EWS-01 workspace skeleton and emit machine-readable readiness/status JSON for downstream local pipeline consumers. |
| storage class | Code-backed local status artifact; consumes an explicit workspace path and writes no media, transcript, render, thumbnail, source receipt, upload, auth, rights, or public-ready state. |
| repo_relative_path | `src/pipeline/episode_workspace.py` |
| machine_output | stdout JSON from `inspect-episode-workspace`; optional `--output` JSON path supplied by the operator. |
| source_inputs | `docs/content_planning/episode_workspace_plan.json`; `docs/content_planning/automation_contract.json`; explicit materialized workspace path |
| open_command | `python -m src.cli.main inspect-episode-workspace --workspace <workspace> --format json` |
| generated_from | `inspect-episode-workspace` reading a local skeleton created by `init-episode-workspace`. |
| validation_command | `python -m pytest -q tests/test_episode_workspace.py` plus tempdir materialize/inspect smoke and JSON parse checks. |
| review_status | Ready as the read-only local workspace consumer. A complete EWS-01 tempdir skeleton reports `manifest_state=initialized`, `source_identity_state=pending`, `readiness_level=source_identity_pending`, `skeleton_ready=true`, `ready_for_source_identity_decision=true`, and `ready_for_fetch=false`. |
| next_action | Use the inspector JSON as the handoff to a later source-decision intake or local fetch-prep slice; do not fetch media or open external gates from this command. |

Inspector boundary flags remain false:

- `source_url_opened=false`
- `media_files_created=false`
- `transcript_generated=false`
- `render_generated=false`
- `thumbnail_generated=false`
- `rights_approved=false`
- `ready_for_fetch=false`
- `blocked_by_true_gate=false`

## `clip-ews01-episode-workspace-spine-v0-001`

| Field | Value |
|---|---|
| title | EWS-01 Episode Workspace Spine / Thin Gate Contract v0 |
| purpose | Convert the CPD-12 current Review item into a local episode workspace plan, with a compact contract that separates allowed local actions from deferred local actions and true external gates. |
| storage class | Tracked local planning artifact; portable JSON contract and workspace plan. No source fetch, media, transcript, render, thumbnail proof, OAuth/API, rights approval, publication, or tracked `episodes/` material is created. |
| repo_relative_path | `docs/content_planning/episode_workspace_plan.json` |
| machine_output | `docs/content_planning/automation_contract.json` |
| source_inputs | `docs/content_planning/operator_cockpit.json` |
| open_command | `python -m src.cli.main build-episode-workspace-plan --format json` |
| skeleton_command | `python -m src.cli.main init-episode-workspace --plan docs/content_planning/episode_workspace_plan.json --target <tempdir> --materialize --format json` |
| generated_from | `build-episode-workspace-plan` reading the CPD-12 current work item from local operator cockpit JSON. |
| validation_command | `python -m pytest -q tests/test_episode_workspace.py` plus JSON parse checks and an explicit tempdir skeleton smoke. |
| review_status | Ready as the downstream local workspace spine. The plan carries `episode_id=ep_seed_cpd01_bancho_marine_misunderstanding`, the CPD-12 planning label, `label_provenance=planning_label_unverified`, `source_url_state=present`, `identity_state=unverified`, and `fetch_authorized=false`. |
| next_action | Inspect or regenerate the plan, then use `init-episode-workspace` only with a tempdir or explicit ignored target if a local skeleton is needed before any source/media lane opens. |

Thin contract categories:

- `allowed_local_actions`: JSON generation, local CLI, explicit tempdir skeletons, explicit ignored local skeletons, local source identity decision records, docs/readme pointers, and targeted tests.
- `deferred_local_actions`: source URL opening, source fetch/download, transcript, render, thumbnail proof, and local media processing.
- `true_external_gates`: public upload/publication, OAuth/API keys/credentials, payment, legal/rights approval claims, destructive git, cross-repo edits, and irreversible source overwrite.

Boundary flags remain false or pending:

- `planning_label_is_verified_video_title=false`
- `source_url_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `transcript_generated=false`
- `render_generated=false`
- `thumbnail_generated=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd12-minimal-review-console-v0-001`

| Field | Value |
|---|---|
| title | ClipPipeGen Review Console / Minimal Review Console v0 |
| purpose | Convert the CPD operator cockpit from a weak view shell into a compact reusable review console with explicit fixed shell regions, dynamic data slots, true Review / Backlog / System modes, and planning-label provenance. |
| storage class | Tracked local planning artifact; portable CPD-01 through CPD-05 consolidation JSON/HTML. Supersedes the CPD-11 view-shell surface in the same output path. |
| repo_relative_path | `docs/content_planning/operator_cockpit.html` |
| machine_output | `docs/content_planning/operator_cockpit.json` |
| source_inputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/episode_seed_drafts.json`; `docs/content_planning/episode_seed_source_resolution.json`; `docs/content_planning/episode_init_plan.json`; `docs/content_planning/source_inspection_packet.json`; `docs/content_planning/source_inspection_decisions.template.json` |
| open_command | `start docs\content_planning\operator_cockpit.html` |
| generated_from | `build-operator-cockpit` reading local CPD planning artifacts only. |
| validation_command | `uvx python -m src.cli.main build-operator-cockpit --format json` plus `uvx pytest -q tests/test_operator_cockpit.py`. |
| latest_validation_result | CPD-12 checkpoint on 2026-07-07 JST: `uvx pytest -q` -> `339 passed, 16 skipped`; targeted cockpit/dashboard tests -> `23 passed`; cockpit/dashboard JSON parsed; `git diff --check` clean; `git ls-files episodes` empty; pushed parity `0 0`. |
| review_status | Ready as the normal human entry point for CPD planning review. The first viewport shows CPD-12 and the artifact id, a fixed shell label, status rail, true mode controls, and a Current Review data slot. The current item is labeled as a planning label with `planning_label`, `source_url_present`, `identity_unverified`, and `not_fetched` provenance badges. Backlog and System details stay behind their modes, and the Candidate Ledger remains readable and collapsed. |
| next_action | Open the cockpit first, use Review mode for OK / NG / HOLD on the one planning-label source item, use Backlog mode for URL-waiting or hold records, and use System mode only for closed-gate/internal readback. |

Boundary flags remain false or pending:

- `source_url_opened_by_worker=false`
- `source_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd11-operator-view-shell-v0-001`

| Field | Value |
|---|---|
| title | ClipPipeGen Review Workbench / Operator View Shell v0 |
| purpose | Convert the CPD operator cockpit from a case-specific briefing page into a reusable view shell with Review, Backlog, and System modes driven by a content model. |
| storage class | Tracked local planning artifact; portable CPD-01 through CPD-05 consolidation JSON/HTML. Supersedes the CPD-10 one-page briefing/ledger surface in the same output path. |
| repo_relative_path | `docs/content_planning/operator_cockpit.html` |
| machine_output | `docs/content_planning/operator_cockpit.json` |
| source_inputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/episode_seed_drafts.json`; `docs/content_planning/episode_seed_source_resolution.json`; `docs/content_planning/episode_init_plan.json`; `docs/content_planning/source_inspection_packet.json`; `docs/content_planning/source_inspection_decisions.template.json` |
| open_command | `start docs\content_planning\operator_cockpit.html` |
| generated_from | `build-operator-cockpit` reading local CPD planning artifacts only. |
| validation_command | `uvx python -m src.cli.main build-operator-cockpit --format json` plus `uvx pytest -q tests/test_operator_cockpit.py`. |
| review_status | Ready as the normal human entry point for CPD planning review. The first viewport is a reusable Review Workbench with state chips, a current source review item, OK / NG / HOLD labels, and a compact locked-gate line. Backlog and System details are separated from the default review mode, and the responsive Candidate Ledger remains available collapsed below. |
| next_action | Open the cockpit first, use Review mode for the one source-ready item, use Backlog mode for URL-waiting or hold records, and use System mode only for closed-gate/internal readback. |

Boundary flags remain false or pending:

- `source_url_opened_by_worker=false`
- `source_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd10-candidate-ledger-readability-v0-001`

| Field | Value |
|---|---|
| title | ClipPipeGen Operator Cockpit / Candidate Ledger Readability v0 |
| purpose | Preserve the accepted CPD-09 Briefing Board while making the lower Candidate Ledger readable for Japanese text-heavy candidate states. |
| storage class | Tracked local planning artifact; portable CPD-01 through CPD-05 consolidation JSON/HTML. Supersedes the CPD-09 ledger table in the same output path. |
| repo_relative_path | `docs/content_planning/operator_cockpit.html` |
| machine_output | `docs/content_planning/operator_cockpit.json` |
| source_inputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/episode_seed_drafts.json`; `docs/content_planning/episode_seed_source_resolution.json`; `docs/content_planning/episode_init_plan.json`; `docs/content_planning/source_inspection_packet.json`; `docs/content_planning/source_inspection_decisions.template.json` |
| open_command | `start docs\content_planning\operator_cockpit.html` |
| generated_from | `build-operator-cockpit` reading local CPD planning artifacts only. |
| validation_command | `uvx python -m src.cli.main build-operator-cockpit --format json` plus `uvx pytest -q tests/test_operator_cockpit.py`. |
| review_status | Ready as the normal human entry point for CPD planning review after the ledger readability repair. The visible Candidate Ledger is stacked/responsive, keeps Japanese titles as full phrase lines, and de-emphasizes machine IDs in a code strip. Source-missing ideas remain not video-backed. |
| next_action | Open the cockpit first, confirm the Candidate Ledger titles read normally, then inspect the single source-backed item through the Primary Review Script or fill source URLs for unresolved ideas before rerunning CPD-03 through CPD-10. |

Boundary flags remain false or pending:

- `source_url_opened_by_worker=false`
- `source_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd09-operator-briefing-board-v0-001`

| Field | Value |
|---|---|
| title | ClipPipeGen Operator Cockpit / Briefing Board Usage-Frequency IA v0 |
| purpose | Give humans one dark-mode content-planning briefing board with an annotated flow, one primary source-identity action, and a compact candidate ledger that does not make source-missing ideas look video-backed. |
| storage class | Tracked local planning artifact; portable CPD-01 through CPD-05 consolidation JSON/HTML. Supersedes the CPD-08 Operator Home / Action Queue layout in the same output path. |
| repo_relative_path | `docs/content_planning/operator_cockpit.html` |
| machine_output | `docs/content_planning/operator_cockpit.json` |
| source_inputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/episode_seed_drafts.json`; `docs/content_planning/episode_seed_source_resolution.json`; `docs/content_planning/episode_init_plan.json`; `docs/content_planning/source_inspection_packet.json`; `docs/content_planning/source_inspection_decisions.template.json` |
| open_command | `start docs\content_planning\operator_cockpit.html` |
| generated_from | `build-operator-cockpit` reading local CPD planning artifacts only. |
| validation_command | `uvx python -m src.cli.main build-operator-cockpit --format json` plus `uvx pytest -q tests/test_operator_cockpit.py`. |
| review_status | Ready as the normal human entry point for CPD planning review. Top screen is a Briefing Board with usage-frequency IA, not a card grid, wide status table, or folded archive. Only `cpd01_bancho_marine_misunderstanding` has a known source URL; JP/EN phrase gap and other unresolved ideas are not source-backed video candidates. |
| next_action | Open the cockpit first, read the Briefing Board annotated flow, then inspect the single source-backed item through the Primary Review Script or fill source URLs for unresolved ideas before rerunning CPD-03 and CPD-04. |

Boundary flags remain false or pending:

- `source_url_opened_by_worker=false`
- `source_opened_by_worker=false`
- `fetch_authorized=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-cpd01-content-candidate-dashboard-v0-001`

| Field | Value |
|---|---|
| title | CPD-01 Content Candidate / Channel Strategy Dashboard v0 |
| purpose | Make "what should we clip next?" reviewable before source fetch, editing, thumbnail, or publishing lanes. |
| storage class | Tracked local planning artifact; portable fixture-generated JSON/HTML. |
| repo_relative_path | `docs/content_planning/content_dashboard.html` |
| machine_outputs | `docs/content_planning/content_candidates.json`; `docs/content_planning/channel_strategy.json` |
| source_fixture | `samples/content_planning/content_candidates_fixture.json` |
| open_command | `start docs\content_planning\content_dashboard.html` |
| generated_from | `build-content-candidate-dashboard` reading offline fixture/manual seed metadata. |
| validation_command | `uvx python -m src.cli.main build-content-candidate-dashboard --format json` plus `uvx pytest -q tests/test_content_planning.py`. |
| review_status | Ready for operator review as planning readback only. It is not source fetch, production render, creative acceptance, rights approval, publishing acceptance, public use, or monetization approval. |
| next_action | Review the top candidate, then decide whether to create an episode seed or add a public metadata adapter behind an explicit offline-safe flag. |

Boundary flags remain false or pending:

- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `media_downloaded=false`
- `oauth_or_credentials_used=false`

## `clip-cpd02-candidate-to-episode-seed-bridge-v0-001`

| Field | Value |
|---|---|
| title | CPD-02 Candidate-to-Episode Seed Bridge v0 |
| purpose | Convert CPD-01 candidate records into deterministic draft episode seed records before any source fetch, transcript, edit, thumbnail, render, or publishing lane runs. |
| storage class | Tracked local planning artifact; portable candidate-derived JSON/HTML. |
| repo_relative_path | `docs/content_planning/episode_seed_dashboard.html` |
| machine_output | `docs/content_planning/episode_seed_drafts.json` |
| source_candidate_json | `docs/content_planning/content_candidates.json` |
| open_command | `start docs\content_planning\episode_seed_dashboard.html` |
| generated_from | `build-episode-seed-drafts` reading CPD-01 candidate JSON. |
| validation_command | `uvx python -m src.cli.main build-episode-seed-drafts --format json` plus `uvx pytest -q tests/test_episode_seed_bridge.py`. |
| review_status | Ready for operator review as draft planning readback only. No episode folders, media, transcripts, edit packs, renders, thumbnails, uploads, rights approval, production acceptance, or public-use permission are created. |
| next_action | Inspect the top seed and decide whether a later slice should resolve source metadata, initialize a real episode skeleton, or hold/reject the seed. |

Boundary flags remain false or pending:

- `status=draft`
- `source_media_state=not_fetched`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `oauth_or_credentials_used=false`

## `clip-cpd03-source-metadata-resolver-v0-001`

| Field | Value |
|---|---|
| title | CPD-03 Source Metadata Resolver / Manual Source Intake v0 |
| purpose | Resolve CPD-02 draft seed source URL state before any source fetch, transcript, episode initialization, thumbnail, render, or publishing lane runs. |
| storage class | Tracked local planning artifact; portable seed-derived JSON/HTML plus blank manual registry template. |
| repo_relative_path | `docs/content_planning/source_resolution_dashboard.html` |
| machine_output | `docs/content_planning/episode_seed_source_resolution.json` |
| manual_registry_template | `docs/content_planning/source_metadata_registry.template.json` |
| source_seed_json | `docs/content_planning/episode_seed_drafts.json` |
| open_command | `start docs\content_planning\source_resolution_dashboard.html` |
| generated_from | `resolve-episode-seed-sources` reading CPD-02 episode seed draft JSON and an optional local manual registry. |
| validation_command | `uvx python -m src.cli.main resolve-episode-seed-sources --format json` plus `uvx pytest -q tests/test_source_metadata_resolver.py`. |
| review_status | Ready for operator review as source-resolution readback only. No media fetch, public API/OAuth lookup, episode folder, transcript, edit pack, render, thumbnail, rights approval, production acceptance, or public-use permission is created. |
| next_action | Fill real source URLs for unresolved seed records in a local manual registry, rerun CPD-03, then decide whether a later dry-run should initialize an episode skeleton for a resolved seed. |

Boundary flags remain false or pending:

- `source_media_state=not_fetched`
- `network_required=false`
- `external_api_used=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-cpd04-init-episode-dry-run-plan-v0-001`

| Field | Value |
|---|---|
| title | CPD-04 Init Episode Dry-Run Plan v0 |
| purpose | Convert CPD-03 source-resolved records into reviewable episode initialization plans without creating real episode folders or downstream production artifacts. |
| storage class | Tracked local planning artifact; portable source-resolution-derived JSON/HTML. |
| repo_relative_path | `docs/content_planning/episode_init_plan_dashboard.html` |
| machine_output | `docs/content_planning/episode_init_plan.json` |
| source_resolution_json | `docs/content_planning/episode_seed_source_resolution.json` |
| seed_enrichment_json | `docs/content_planning/episode_seed_drafts.json` |
| open_command | `start docs\content_planning\episode_init_plan_dashboard.html` |
| generated_from | `build-episode-init-plan` reading CPD-03 source resolution JSON and optional CPD-02 seed draft enrichment. |
| validation_command | `uvx python -m src.cli.main build-episode-init-plan --format json` plus `uvx pytest -q tests/test_episode_init_plan.py`. |
| review_status | Ready for operator review as dry-run initialization readback only. No episode folder, rights manifest, material ledger, fetch receipt, source media, transcript, edit pack, thumbnail, render, upload, rights approval, production acceptance, or public-use permission is created. |
| next_action | Review the single ready dry-run plan and decide whether a later slice should run real source inspection / `init-episode`, while unresolved records stay behind manual source intake. |

Boundary flags remain false or pending:

- `dry_run=true`
- `source_media_state=not_fetched`
- `transcript_state=not_generated`
- `material_ledger_state=planned_only`
- `edit_pack_state=planned_only`
- `thumbnail_state=planned_only`
- `network_required=false`
- `external_api_used=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_manifest_created=false`
- `material_ledger_created=false`
- `fetch_receipt_created=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_ready=false`
- `publishing_acceptance=false`
- `public_ready=false`

## `clip-cpd05-source-inspection-packet-v0-001`

| Field | Value |
|---|---|
| title | CPD-05 Source Inspection Packet / Decision Registry v0 |
| purpose | Convert ready CPD-04 dry-run episode init plans into operator source inspection packets and a blank decision registry template before any future gated source action. |
| storage class | Tracked local planning artifact; portable episode-init-plan-derived JSON/HTML/template. |
| repo_relative_path | `docs/content_planning/source_inspection_packet_dashboard.html` |
| machine_output | `docs/content_planning/source_inspection_packet.json` |
| decision_template | `docs/content_planning/source_inspection_decisions.template.json` |
| source_episode_init_plan | `docs/content_planning/episode_init_plan.json` |
| open_command | `start docs\content_planning\source_inspection_packet_dashboard.html` |
| generated_from | `build-source-inspection-packet` reading CPD-04 episode init plan JSON. |
| validation_command | `uvx python -m src.cli.main build-source-inspection-packet --format json` plus `uvx pytest -q tests/test_source_inspection_packet.py`. |
| review_status | Ready for operator source identity review as an inspection packet only. The worker did not open the source URL, authorize future private/local fetch, create episode folders, generate episode artifacts, approve rights, or mark anything production/public ready. |
| next_action | Open the dashboard, inspect the single ready source URL manually, then fill `source_inspection_decisions.template.json` only if a later gated slice should proceed. |

Boundary flags remain false or pending:

- `dry_run=true`
- `source_opened_by_worker=false`
- `source_media_state=not_fetched`
- `fetch_authorized=false`
- `network_required=false`
- `external_api_used=false`
- `media_downloaded=false`
- `episode_dirs_created=false`
- `rights_manifest_created=false`
- `material_ledger_created=false`
- `fetch_receipt_created=false`
- `transcript_generated=false`
- `edit_pack_created=false`
- `oauth_or_credentials_used=false`
- `rights_approved=false`
- `production_ready=false`
- `public_ready=false`

## `clip-review-acceptance-gate-001`

| Field | Value |
|---|---|
| title | ED-10f Representative Subtitle Design Review Gate |
| purpose | Track the representative subtitle design review gate that consumed the SH-08 human response as `adjust_boundary` and sent font-family / decoration to ED-10g. |
| storage class | Tracked decision/readback artifact; references local proof evidence but is portable as docs. |
| repo_relative_path | `docs/REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md` |
| related_local_artifact | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/index.html` |
| generated_from | Parser-first readback plus human response consumption recorded in tracked docs. |
| validation_command | `uvx pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` |
| latest_validation_result | `18 passed, 8 skipped` on the 2026-06-16 targeted local validation path before the v1.5 dashboard slice. |
| review_status | Human response consumed as `adjust_boundary`; ED-10f is diagnostic / representative only and has successor work in ED-10g / ED-10h. |
| next_action | Use ED-10g Noto overlay proof for current visual judgement; use ED-10h registry only if the font universe must widen after that judgement. |

## `clip-human-preview-session-001`

| Field | Value |
|---|---|
| title | SH-08 Human Preview Session Bundle |
| purpose | Single local entry point for diagnostic / representative review of the current `cut_002` / `cut_003` subtitle overlay evidence. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/index.html` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session\open_preview.ps1` |
| fallback_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\human_preview_session\serve_preview.ps1 -Port 8000` |
| generated_from | `build-human-preview-session` / `build-episode-review-bundle` reading existing ignored episode and review artifacts. |
| validation_command | `uvx pytest -q tests/test_episode_review_bundle.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_status.py` |
| latest_validation_result | `18 passed, 8 skipped` on the 2026-06-16 targeted local validation path. |
| latest_local_smoke | Same-machine parser readback confirmed `review_ready=true`, `state=diagnostic_only`, `target_cuts=[cut_002, cut_003]`, `missing_artifacts=[]`, `<video controls>`, and `cut_002` / `cut_003` MP4 assets. Localhost preview smoke succeeded in the retained workspace. |
| review_status | Human response consumed as `adjust_boundary`; ED-10g successor response `small_adjustment` is now recorded separately. Diagnostic / representative only. |
| next_action | Follow the ED-10g small-adjustment route; do not regenerate SH-08 unless the active preview session itself must be inspected again. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked builder, docs, and tests. It cannot directly
verify the ignored local MP4/PNG assets themselves, so local artifact existence
must be verified with the open command or manifest readback on the retaining
machine. `git ls-files episodes` should remain empty.

## `clip-typography-decoration-comparison-001`

| Field | Value |
|---|---|
| title | ED-10g Subtitle Typography Decoration Comparison v0 |
| purpose | Compare font-family and decorative treatment candidates while preserving the accepted diagnostic font-size direction for `cut_002` / `cut_003`. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/subtitle_typography_decoration_comparison_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_typography_decoration_comparison/subtitle_typography_decoration_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_typography_decoration_comparison\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text, plus tracked ED-10g response readback for `small_adjustment`. |
| validation_command | `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py` plus normal project validation. |
| latest_validation_result | `7 passed` for the Pillow-enabled style-spike path; normal no-Pillow path can skip PNG generation tests. |
| latest_local_smoke | Same-machine refresh on 2026-06-16 JST produced 4 candidates, 16 PNG samples, JSON/HTML report, contact sheet, and `open_comparison.ps1`; `comparison_response_readback.selected_response=small_adjustment`, `selected_candidate_for_next_proof_base=noto_sans_jp_clean_outline`, `next_diagnostic_overlay_proof_route.route_kind=small_adjustment_diagnostic_overlay_proof`, `small_adjustment_decision_packet.decision_state=selected_for_next_diagnostic_overlay_proof_base`, `font_size_policy.value=124`, `production_subtitle_design_acceptance=false`, `rights_status=pending`. The persisted JSON is ASCII-escaped and parsed successfully with Windows PowerShell `ConvertFrom-Json`; the contact sheet was inspected as a nonblank local visual artifact. Other worktrees may lack this ignored artifact and must treat absence as local evidence absence, not a tracked Git failure. |
| review_status | Human response consumed as `small_adjustment`; diagnostic / representative only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Treat this as historical ED-10g comparison context. Use `clip-ed10i-kirinuki-gothic-balance-001` for the current body/outline balance decision. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, and tests. It cannot
directly verify the ignored PNG/HTML comparison artifacts themselves, so local
artifact existence must be verified with the open command or JSON report
readback on the retaining machine. `git ls-files episodes` should remain empty.

## `clip-ed10i-kirinuki-gothic-balance-001`

| Field | Value |
|---|---|
| title | ED-10i Kirinuki Gothic Weight Balance Comparison v0 |
| purpose | Consume the latest human review that the current Noto clean-outline proof is not accepted as-is, then compare a narrow gothic/sans set by glyph body weight, outline thickness, and fill/outline balance. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_gothic_balance_comparison/subtitle_kirinuki_gothic_balance_comparison_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_gothic_balance_comparison/subtitle_kirinuki_gothic_balance_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10i_kirinuki_gothic_balance` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10i human review readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10i_kirinuki_gothic_balance --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_gothic_balance_comparison --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10i generation returned `artifact_id=clip-ed10i-kirinuki-gothic-balance-001`, `candidate_count=4`, `sample_count=16`, `font_size.value=124`, `recommended_default_candidate_id=ed10i_biz_udgothic_bold_balanced_outline`, `production_candidate=false`, and `rights_status=pending`; JSON parsed successfully and the contact sheet was inspected as nonblank local visual evidence. |
| review_status | Human review consumed: the bottom-most gothic candidate was selected as closest to ideal and resolved from local JSON as `ed10i_meiryo_bold_fill_outline_balance`. This comparison remains the audit trail for that choice. |
| next_action | Use `clip-ed10i-meiryo-overlay-proof-001` for the current visual judgement. Reopen this comparison only if the candidate mapping or a bounded body/outline adjustment needs audit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests. It cannot directly verify the ignored PNG/HTML comparison artifacts
themselves, so local artifact existence must be verified with the open command
or JSON report readback on the retaining machine. `git ls-files episodes`
should remain empty.

## `clip-ed10i-meiryo-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10i Meiryo Selected Diagnostic Overlay Proof |
| purpose | Apply the human-selected bottom ED-10i candidate, `ed10i_meiryo_bold_fill_outline_balance`, to the `cut_002` / `cut_003` diagnostic subtitle overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10i_meiryo_bold_fill_outline_balance` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10i_meiryo_bold_fill_outline_balance --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10i_meiryo_bold_fill_outline_balance`, `typography_decoration_candidate_id=ed10i_meiryo_bold_fill_outline_balance`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=Meiryo`, `font_family_route.font_file_status=candidate_primary_font_file_found`, `font_size=124`, `outline=9`, `bbox_wrapping_applied=true`, and target MP4/PNG artifacts for `cut_002` and `cut_003`. The generated PNG frames were inspected as nonblank 1920x1080 local visual artifacts. |
| human_visual_judgement | Freeform review consumed: the proof looks too thin and is not attractive enough as the normal subtitle baseline; the issue may be baseline font choice, not only outline tuning. |
| review_status | Reviewed and not accepted as the normal subtitle baseline. Meiryo is now an audited reference candidate only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Use `clip-ed10j-kirinuki-font-audit-001` to review stronger normal-dialogue font candidates before generating another narrow overlay proof. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored MP4/PNG/ASS files themselves. Other worktrees should
treat missing `episodes/` proof assets as local evidence absence, not as a
tracked Git failure.

## `clip-ed10j-kirinuki-font-audit-001`

| Field | Value |
|---|---|
| title | ED-10j Kirinuki Subtitle Font Research & Candidate Audit v0 |
| purpose | Consume the reviewed Meiryo overlay proof as not accepted for the normal subtitle baseline, then compare a no-download normal-dialogue gothic/sans shortlist before another overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_font_audit/subtitle_kirinuki_font_audit_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_kirinuki_font_audit/subtitle_kirinuki_font_audit_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10j_kirinuki_font_audit` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10j freeform review readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10j_kirinuki_font_audit --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_kirinuki_font_audit --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10j regeneration returned `artifact_id=clip-ed10j-kirinuki-font-audit-001`, `candidate_count=4`, `sample_count=16`, `font_size.value=124`, `selected_candidate_for_next_proof_base=ed10j_biz_udgothic_bold_telop_candidate`, `blue_badge_candidate_id=ed10j_noto_sans_jp_local_telop_candidate`, `blue_badge_is_meiryo_reference=false`, `production_candidate=false`, and `rights_status=pending`; JSON parsed successfully and the contact sheet was inspected as nonblank local visual evidence. |
| review_status | Freeform review consumed: Meiryo is removed from normal baseline candidates, the remaining non-Meiryo candidates are close enough to avoid prolonging the audit, and BIZ UDGothic is selected as the default next proof base. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Treat this as consumed audit trail. ED-10k already tested BIZ, and ED-10l is the current known-font route correction. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests. It cannot directly verify the ignored PNG/HTML comparison artifacts
themselves, so local artifact existence must be verified with the open command
or JSON report readback on the retaining machine. `git ls-files episodes`
should remain empty.

## `clip-ed10k-biz-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10k BIZ UDGothic Diagnostic Overlay Proof |
| purpose | Apply the ED-10j selected default `ed10j_biz_udgothic_bold_telop_candidate` to the `cut_002` / `cut_003` diagnostic subtitle overlay proof after Meiryo was removed from normal subtitle candidates. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10j_biz_udgothic_bold_telop_candidate --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10j_biz_udgothic_bold_telop_candidate`, `typography_decoration_candidate_id=ed10j_biz_udgothic_bold_telop_candidate`, `subtitle_overlay_available_count=2`, `all_target_cuts_have_overlay=true`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=BIZ UDGothic`, `font_family_route.font_file_status=candidate_primary_font_file_found`, `font_size=124`, `outline=8`, `ed10j_kirinuki_font_audit_candidate=true`, `explicit_line_breaks_passed_to_ass=true`, `one_character_orphan_present=false`, and `suspicious_tail_line_present=false`. The `cut_002` and `cut_003` PNG frames were inspected as nonblank 1920x1080 local visual artifacts. |
| review_status | Freeform review consumed: BIZ UDGothic is not accepted as the normal subtitle baseline because it reads too hard/rigid, the text remains thin, and the black outline pressure is too strong. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Keep this as reviewed rejected reference evidence. Use `clip-ed10l-known-kirinuki-font-pack-001` for the current normal-dialogue font route decision. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked code, docs, dashboard metadata, and tests but
not the ignored MP4/PNG/ASS files themselves. Other worktrees should treat
missing `episodes/` proof assets as local evidence absence, not as a tracked
Git failure.

## `clip-ed10l-known-kirinuki-font-pack-001`

| Field | Value |
|---|---|
| title | ED-10l Known Kirinuki Font Pack Audit v0 |
| purpose | Consume the reviewed ED-10k BIZ proof as not accepted, then audit known Japanese YouTube kirinuki/telop font candidates for the normal-dialogue baseline before another overlay proof is selected. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_known_kirinuki_font_pack_comparison/subtitle_known_kirinuki_font_pack_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_known_kirinuki_font_pack_comparison/subtitle_known_kirinuki_font_pack_contact_sheet.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10l_known_kirinuki_font_pack` reading existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10l route-correction readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10l_known_kirinuki_font_pack --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_known_kirinuki_font_pack_comparison --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10n regeneration returned `artifact_id=clip-ed10l-known-kirinuki-font-pack-001`, `comparison_profile=ed10l_known_kirinuki_font_pack`, `sample_count=16`, `candidate_count=4`, `font_size.value=124`, `selected_candidate_for_next_proof_base=ed10l_keifont_pop_dialogue_candidate`, `comparison_response_readback.selected_response=per_user_font_readback_valid_route_to_keifont_overlay_proof`, `font_visual_comparison_validity=valid_requested_font_visual_evidence`, `all_candidates_valid_real_font=true`, `production_candidate=false`, and `rights_status=pending`; JSON parsed successfully. |
| review_status | Regenerated as valid requested-font comparison/readback evidence after HKCU/per-user font resolver support. It supports ED-10n proof routing but is not itself production subtitle design acceptance. |
| next_action | Use `clip-ed10n-keifont-overlay-proof-001` for current human visual judgement. Return to this comparison only if Keifont is rejected and another ED-10l candidate should be promoted. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests. It cannot directly verify the ignored PNG/HTML comparison artifacts
themselves, so local artifact existence must be verified with the open command
or JSON report readback on the retaining machine. `git ls-files episodes`
should remain empty.

## `clip-ed10n-keifont-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10n Keifont Real-Font Diagnostic Overlay Proof |
| purpose | Apply the per-user resolved `ed10l_keifont_pop_dialogue_candidate` to the `cut_002` / `cut_003` diagnostic subtitle overlay proof after ED-10l real-font readback became valid. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --format json` plus targeted tests. |
| latest_validation_result | Same-machine generation returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `typography_decoration_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`; JSON parsed successfully. |
| latest_local_smoke | Same-machine readback resolved `font_family_route.requested=Keifont`, `font_family_route.resolved=Keifont`, `font_family_route.resolved_font_file=C:\Users\thank\AppData\Local\Microsoft\Windows\Fonts\keifont.ttf`, `font_file_status=candidate_primary_font_file_found`, and target MP4/PNG artifacts for `cut_002` and `cut_003`. |
| review_status | Available and requires human visual review. It is not production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Review the visible Keifont proof and answer whether it should proceed, get one bounded adjustment, or be replaced by another ED-10l candidate. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored MP4/PNG/ASS files themselves. Other worktrees should
treat missing `episodes/` proof assets as local evidence absence, not as a
tracked Git failure. `git ls-files episodes` should remain empty.

## `clip-ed10o-multifont-focused-review-001`

| Field | Value |
|---|---|
| title | ED-10o Multi-font Focused Review Surface |
| purpose | Consume the latest Keifont review as improved and usable enough for serious review, then move the bottleneck to a compact one-shot comparison of Keifont, 851 Chikara Yowaku, and Yasashisa Gothic on the same subtitle lines. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_multifont_focused_review/subtitle_multifont_focused_review_report.html` |
| contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_multifont_focused_review/subtitle_multifont_focused_review_matrix.png` |
| open_command | `powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review\subtitle_multifont_focused_review\open_comparison.ps1` |
| generated_from | `build-subtitle-typography-decoration-comparison --comparison-profile ed10o_multifont_focused_review` reading the existing ignored episode `edit_pack.json` for `cut_002` / `cut_003` review text and tracked ED-10n review readback. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-typography-decoration-comparison --comparison-profile ed10o_multifont_focused_review --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10o generation returned `artifact_id=clip-ed10o-multifont-focused-review-001`, `comparison_profile=ed10o_multifont_focused_review`, `sample_count=12`, `candidate_count=3`, `focused_review_surface.status=focused_review_surface_generated`, `focused_review_surface.primary_visual=subtitle_area_crop_matrix`, `selected_candidate_for_next_proof_base=ed10l_keifont_pop_dialogue_candidate`, `font_visual_comparison_validity=valid_requested_font_visual_evidence`, `all_candidates_valid_real_font=true`, `excluded_candidates[0].candidate_id=ed10l_m_plus_fonts_dialogue_candidate`, `production_candidate=false`, and `rights_status=pending`; JSON and HTML parsed successfully and the focused matrix PNG was inspected as a nonblank local visual artifact. |
| review_status | Human review consumed as focused review surface accepted/easier to see. Keifont remains the lead entering ED-10p, with 851 Chikara Yowaku and Yasashisa Gothic preserved as alternates. This is not final baseline or production subtitle design acceptance. |
| next_action | Use as the accepted review UX direction and historical comparison reference while reviewing `clip-ed10r-keifont-dense-stress-proof-001`. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

M+ is intentionally excluded from this one-shot comparison because current
readback resolves to `M PLUS 1 Thin` via `MPLUS1-VariableFont_wght.ttf`; it
should be reintroduced only after an exact non-thin weight/style route is
pinned. Remote Git can verify the tracked generator, docs, dashboard metadata,
and tests but not the ignored PNG/HTML artifacts themselves. Other worktrees
should treat missing `episodes/` review assets as local evidence absence, not
as a tracked Git failure. `git ls-files episodes` should remain empty.

## `clip-ed10p-keifont-lead-representative-proof-001`

| Field | Value |
|---|---|
| title | ED-10p Keifont Lead Representative Proof |
| purpose | Consume the ED-10o review that the font comparison and review screen are easier to see, keep Keifont as diagnostic representative normal-dialogue provisional baseline evidence, and preserve the `cut_002` / `cut_003` proof history without reopening general acceptance. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/current_proof_focused_review.html` |
| detailed_overlay_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| representative_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html` |
| open_command | `.\open-current-proof.ps1` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10p_keifont_lead_representative_proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_002 --target-cut cut_003` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10p_keifont_lead_representative_proof --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10q regeneration returned `artifact_id=clip-ed10p-keifont-lead-representative-proof-001`, `proof_profile=ed10p_keifont_lead_representative_proof`, `source_review_artifact_id=clip-ed10o-multifont-focused-review-001`, `visual_proof_status=available_requires_human_review`, `style_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `typography_decoration_candidate_id=ed10l_keifont_pop_dialogue_candidate`, `subtitle_overlay_available_count=2`, `focused_review_html=episodes/.../current_proof_focused_review.html`, `focused_proof_review.status=representative_keifont_lead_proof_ready`, `review_debt[0].debt_id=cut_008_dense_stress_proof`, `production_candidate=false`, and `rights_status=pending`; focused HTML readback confirmed Review Focus before subtitle-area evidence and Detailed Reports, ED-10o reference link present, cut_002/cut_003 evidence present, cut_008 debt present, and old debug cut table absent from the focused page. |
| review_status | Consumed as provisional normal-dialogue baseline evidence. ED-10q restored the focused page after the old-layout regression, but ED-10q was not font-quality review. Do not request another general Keifont acceptance pass on `cut_002` / `cut_003`. Final baseline, production render, creative, rights, publishing, and public-use gates remain closed. |
| next_action | Use `clip-ed10r-keifont-dense-stress-proof-001` for the active review. Keep this artifact as history and baseline evidence only. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

`cut_008` Review Debt has moved to ED-10r as the current narrow dense/stress
proof. Remote Git can verify the tracked builder, docs, dashboard metadata,
and tests but not the ignored MP4/PNG/ASS artifacts themselves. Other worktrees
should treat missing `episodes/` proof assets as local evidence absence, not
as a tracked Git failure. `git ls-files episodes` should remain empty.

## `clip-ed10af-render-contract-consumer-dry-read-001`

| Field | Value |
|---|---|
| title | ED-10af Render Contract Consumer Dry-Read |
| purpose | Preserve the L0 static consumer payload evidence that was originally added in commit `7e96a28`, before the active L2 probe existed. |
| storage class | Tracked JSON/Markdown predecessor readback; no local media output. |
| repo_relative_path | `docs/style_intent/subtitle-render-contract-consumer-dry-read.md` |
| metadata_json | `docs/style_intent/subtitle-render-contract-consumer-dry-read.json` |
| open_command | `see docs\style_intent\subtitle-render-contract-consumer-dry-read.md` |
| predecessor_commit | `7e96a28 Add ED-10af render contract consumer dry read` |
| successor_artifact | `clip-ed10af-l2-render-path-selector-probe-001` |
| source_render_path_selector_contract_artifact | `clip-ed10ae-render-path-selector-contract-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` dry-read builder plus restored tracked readback files. |
| generated_from | ED-10af dry-read commit `7e96a28`; restored as predecessor evidence after the L2 probe replaced the active surface. |
| validation_command | Parse dry-read JSON, ED-10ag L2 readback JSON, ED-10af probe JSON, and dashboard JSON; run targeted subtitle/dashboard/review tests; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Restored JSON reports six static consumer payloads, `render_level=L0 No Render`, `consumer_dry_read_only=true`, no render boundary leakage, no production/public boundary leakage, and `all_payloads_consumer_ready=true`. |
| review_status | Superseded by the L2 selector probe, but not invalidated. Keep as predecessor source evidence for the full six-example contract consumer payload. |
| next_action | Use only as static predecessor evidence. The active artifact remains `clip-ed10af-l2-render-path-selector-probe-001`. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10af-l2-render-path-selector-probe-001`

| Field | Value |
|---|---|
| title | ED-10af L2 Render Path Selector Probe |
| purpose | Consume the ED-10ae render-path selector contract into a tiny FFmpeg/libass diagnostic path for normal dialogue, shout, and whisper semantic examples. |
| storage class | Tracked JSON/Markdown readback plus ignored same-machine ASS/MP4/manifest evidence. |
| repo_relative_path | `docs/style_intent/subtitle-render-path-selector-probe.md` |
| metadata_json | `docs/style_intent/subtitle-render-path-selector-probe.json` |
| open_command | `see docs\style_intent\subtitle-render-path-selector-probe.md` |
| local_ignored_ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| local_ignored_video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| local_ignored_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| | predecessor_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_render_path_selector_contract_artifact | `clip-ed10ae-render-path-selector-contract-probe-001` |
| source_style_family_palette_artifact | `clip-ed10ad-style-family-palette-axis-proof-001` |
| source_visual_selector_artifact | `clip-ed10ac-visual-selector-proof-001` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10af L2 selector probe using ED-10ae contract entries and existing ignored local source media. |
| validation_command | Parse ED-10af probe JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Local ignored FFmpeg/libass probe generated ASS/MP4/manifest; metadata readback reports 1920x1080, 4.2s, h264/aac. Tracked JSON reports 3 examples, stable body text, badge/accent/backplate route, safe-area/line-break metadata, and closed production/public boundaries. |
| review_status | No Review Card and no user-side judgement requested. This is diagnostic render-path readback only. |
| next_action | Use this L2 selector probe readback before opening a separate production limitation-lift, final render-path, rights, publishing, or public-use route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10ag-lineage-and-observation-surface-001`

| Field | Value |
|---|---|
| title | ED-10ag Lineage and Observation Surface |
| purpose | Record that the restored ED-10af dry-read remains predecessor evidence while the active ED-10af L2 selector probe supplies bounded render-path proof. |
| storage class | Tracked JSON/Markdown lineage and observation surface; references ignored same-machine ASS/MP4/manifest/contact-sheet evidence only. |
| repo_relative_path | `docs/style_intent/subtitle-render-path-lineage-observation-surface.md` |
| metadata_json | `docs/style_intent/subtitle-render-path-lineage-observation-surface.json` |
| open_command | `see docs\style_intent\subtitle-render-path-lineage-observation-surface.md` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_dry_read_commit | `7e96a28` |
| source_l2_selector_probe_artifact | `clip-ed10af-l2-render-path-selector-probe-001` |
| source_render_path_selector_contract_artifact | `clip-ed10ae-render-path-selector-contract-probe-001` |
| local_ignored_ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| local_ignored_video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| local_ignored_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| local_ignored_contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |
| generated_from | ED-10ag Existing Output First lineage surface using the restored ED-10af dry-read and the existing active ED-10af L2 selector probe; no new render was run. |
| validation_command | Parse ED-10ag lineage JSON, ED-10af probe JSON, restored dry-read JSON, and dashboard JSON; run targeted subtitle/dashboard/review tests; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | ED-10ag JSON reports `existing_output_first_reused=true`, `new_render_run=false`, `source_probe_new_render_run=true`, `dry_read_all_payloads_consumer_ready=true`, `stable_body_text_preserved=true`, `production_public_boundary_closed=true`, and `episodes_tracked=false`. |
| review_status | No Review Card and no required user-side observation. The artifact is bounded lineage/observation technical readback, not new subtitle design or render acceptance. |
| next_action | Use this surface to inspect the predecessor/current artifact relationship and local ignored proof paths before opening any production limitation-lift, final render-path, rights, publishing, or public-use route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10ah-production-limitation-lift-entry-001`

| Field | Value |
|---|---|
| title | ED-10ah Production Limitation-Lift Entry |
| purpose | Separate diagnostic render-path proof from production subtitle design acceptance, production render acceptance, creative acceptance, rights status, publishing acceptance, and public-use permission. |
| storage class | Tracked JSON/Markdown gate-separation artifact; references ignored same-machine proof media only. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-entry.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-entry.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-entry.md` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_dry_read_commit | `7e96a28` |
| local_ignored_ass | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.ass` |
| local_ignored_video | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.mp4` |
| local_ignored_manifest | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe.local.json` |
| local_ignored_contact_sheet | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |
| generated_from | ED-10ah consumes the user observation that the opened surface is acceptable enough and forward progress is preferred; it preserves ED-10af as active diagnostic proof and ED-10ag as lineage support. |
| validation_command | Parse ED-10ah, ED-10ag, ED-10af probe, restored dry-read JSON, and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | ED-10ah JSON reports all seven gate names present, `active_diagnostic_source_preserved=true`, `lineage_support_not_production_proof=true`, `dry_read_predecessor_preserved=true`, `production_public_boundary_closed=true`, `new_render_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card. Display/layout polish is deferred by user observation; the artifact is a gate entry, not production/public approval. |
| next_action | Start `production-limitation-lift-stage-1` or `final-render-path-readiness` from this gate matrix while keeping production subtitle design, production render, creative, rights, publishing, and public-use decisions explicit. |

Boundary flags remain false or pending:

- `diagnostic_render_path_proof=available_diagnostic_only`
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10ah-render-readiness-separation-readback-001`

| Field | Value |
|---|---|
| title | ED-10ah Render Readiness Separation Readback |
| type | Tracked JSON/Markdown bounded readiness readback |
| status | `render_readiness_separation_readback_ready` |
| storage class | Tracked JSON/Markdown only; references ignored same-machine diagnostic render evidence but creates no media. |
| repo_relative_path | `docs/style_intent/subtitle-render-readiness-separation.md` |
| metadata_json | `docs/style_intent/subtitle-render-readiness-separation.json` |
| open_command | `see docs\style_intent\subtitle-render-readiness-separation.md` |
| source_l2_selector_probe | `clip-ed10af-l2-render-path-selector-probe-001` |
| source_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_limitation_lift_entry | `clip-ed10ah-production-limitation-lift-entry-001` |
| render_gate | L1/L2 Existing Output Observation / reused diagnostic readback; new render false. |
| generated_from | ED-10ah render-readiness cleanup using existing ED-10af/ED-10ag/ED-10ah tracked readbacks only. |
| validation_command | Parse ED-10ah readiness separation JSON plus related style proof / dry-read / render probe / dashboard files; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records proven scope, not-proven scope, render gate, later explicit render trigger, closed production boundary, closed rights/public-use boundary, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This is not production subtitle design, production render, creative, rights, publishing, public-use, or final subtitle style acceptance. |
| next_action | Use this readback to start a later explicit `final-render-path-readiness` or `production-limitation-lift-stage-1` milestone without inferring production/public approval. |

## `clip-ed10ai-final-render-path-readiness-packet-001`

| Field | Value |
|---|---|
| title | ED-10ai Final Render-Path Readiness Packet |
| purpose | Classify what is ready for a later final render-path route and what remains missing before production/public use can be considered. |
| storage class | Tracked JSON/Markdown readiness packet; references ignored same-machine diagnostic media only. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-readiness.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-readiness.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-readiness.md` |
| source_gate_entry | `clip-ed10ah-production-limitation-lift-entry-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| source_selector_contract | `clip-ed10ab-subtitle-preset-selector-001` |
| source_render_adapter_input_contract | `clip-ed10ae-render-path-selector-contract-probe-001` |
| generated_from | ED-10ai uses ED-10ah gate separation plus ED-10af/ED-10ag diagnostic evidence to prepare `final-render-path-stage-1` without running a render or approving production/public use. |
| validation_command | Parse ED-10ai readiness JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records all required readiness rows, ED-10af active diagnostic source, ED-10ah gate source, ED-10ag lineage, `7e96a28` dry-read predecessor, selector/render-contract evidence, closed production/public boundaries, `new_render_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This packet is preparation only, not production subtitle design, production render, creative, rights, publishing, or public-use approval. |
| next_action | Start `final-render-path-stage-1` or `production-limitation-lift-stage-1` from this readiness matrix while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`

## `clip-ed10aj-final-render-path-stage-1-001`

| Field | Value |
|---|---|
| title | ED-10aj Final Render-Path Stage 1 |
| purpose | Select the stage-1 final render-path candidate from existing diagnostic evidence without approving production render or public use. |
| storage class | Tracked JSON/Markdown stage-1 packet; references ignored same-machine diagnostic media only. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-stage-1.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-stage-1.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-stage-1.md` |
| source_readiness_packet | `clip-ed10ai-final-render-path-readiness-packet-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_gate_entry | `clip-ed10ah-production-limitation-lift-entry-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| selected_path | FFmpeg/libass diagnostic subtitle overlay path, selected for stage-1 preparation only. |
| generated_from | ED-10aj uses ED-10ai readiness plus ED-10af/ED-10ag diagnostic evidence to define `final-render-path-stage-1` without running a render or approving production/public use. |
| validation_command | Parse ED-10aj stage-1 JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records all required stage-1 checklist rows, ED-10ai readiness source, ED-10af active diagnostic source, FFmpeg/libass candidate path, closed production/public boundaries, `new_render_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This packet is preparation only, not production subtitle design, production render, creative, rights, publishing, or public-use approval. |
| next_action | Start `final-render-path-stage-2` or `production-limitation-lift-stage-1` from this selected path while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `final_render_path_approved=false`

## `clip-ed10ak-final-render-path-stage-2-replayability-001`

| Field | Value |
|---|---|
| title | ED-10ak Final Render-Path Stage 2 Replayability |
| purpose | Record how a later agent/operator can inspect or replay the selected FFmpeg/libass diagnostic subtitle overlay path without approving production render or public use. |
| storage class | Tracked JSON/Markdown operation packet; references ignored same-machine diagnostic media only. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-stage-2.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-stage-2.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-stage-2.md` |
| source_stage_1_packet | `clip-ed10aj-final-render-path-stage-1-001` |
| source_readiness_packet | `clip-ed10ai-final-render-path-readiness-packet-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| selected_path | FFmpeg/libass diagnostic subtitle overlay path. |
| operation_matrix | Tracks selected path, tracked inputs, same-machine source inputs, ignored outputs, expected output types, command family, validation/readback commands, fresh-clone absence behavior, diagnostic-only scope, and missing production render approvals. |
| generated_from | ED-10ak uses ED-10aj stage-1 plus ED-10af/ED-10ag diagnostic evidence to define replayability/operation handoff without running a render/replay or approving production/public use. |
| validation_command | Parse ED-10ak stage-2 JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | JSON records all required operation rows, ED-10aj stage-1 source, ED-10af active diagnostic source, FFmpeg/libass command family, fresh-clone absence behavior, closed production/public boundaries, `new_render_run=false`, `new_replay_run=false`, and `episodes_tracked=false`. |
| review_status | No Review Card and no user-side work. This packet is replayability/readback only, not production subtitle design, production render, creative, rights, publishing, or public-use approval. |
| next_action | Start `final-render-path-stage-3` or `production-limitation-lift-stage-1` from this operation packet while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_replay_run=false`
- `final_render_path_approved=false`

## `clip-ed10al-final-render-path-stage-3-rehearsal-001`

| Field | Value |
|---|---|
| title | ED-10al Final Render-Path Stage 3 Diagnostic Rehearsal |
| purpose | Rehearse the selected FFmpeg/libass diagnostic subtitle overlay path from the ED-10ak replayability packet, record same-machine generated ignored outputs and metadata, and keep production/public gates closed. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-final-render-path-stage-3.md` |
| metadata_json | `docs/style_intent/subtitle-final-render-path-stage-3.json` |
| open_command | `see docs\style_intent\subtitle-final-render-path-stage-3.md` |
| source_stage_2_packet | `clip-ed10ak-final-render-path-stage-2-replayability-001` |
| source_stage_1_packet | `clip-ed10aj-final-render-path-stage-1-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| support_lineage_observation_surface | `clip-ed10ag-lineage-and-observation-surface-001` |
| source_dry_read_artifact | `clip-ed10af-render-contract-consumer-dry-read-001` |
| generated_ignored_outputs | `subtitle_render_path_selector_probe.ass`, `subtitle_render_path_selector_probe.mp4`, `subtitle_render_path_selector_probe.local.json` under `episodes/.../subtitle_render_path_selector_probe/` |
| recorded_not_generated_output | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_render_path_selector_probe/subtitle_render_path_selector_probe_contact_sheet.jpg` |
| generated_from | ED-10al uses the ED-10ak operation packet plus local source video/audio to run one bounded ignored FFmpeg/libass diagnostic rehearsal. |
| validation_command | Parse ED-10al stage-3 JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and generated local outputs are ignored. |
| latest_local_smoke | Same-machine rehearsal returned `status=local_ignored_probe_generated`, generated ignored ASS/MP4/manifest outputs, output metadata `duration_seconds=4.2`, `resolution=1920x1080`, `video_codec=h264`, `audio_codec=aac`, `stream_count=2`, style-token survival true, stable body text true, badge/accent/backplate route true, line-break/safe-area metadata true, `production_render_acceptance=false`, `public_use_permission=false`, and `episodes_tracked=false`. |
| review_status | No new Review Card. This is diagnostic rehearsal readback only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-1` or `final-render-path-stage-4` from this rehearsal packet while keeping all production/public decisions explicit. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_rehearsal_run=true`
- `final_render_path_approved=false`

## `clip-ed10as-internal-review-access-sheet-fullpath-001`

| field | value |
|---|---|
| title | ED-10as Internal Review Access Sheet Fullpath |
| purpose | Provide exact current-host full paths and a launcher for the ED-10ar internal review video candidate without creating render/replay/media or granting production/public/rights approval. |
| storage_class | tracked JSON/Markdown plus launcher script |
| repo_relative_path | docs/style_intent/internal-review-video-candidate-access-sheet.json; docs/style_intent/internal-review-video-candidate-access-sheet.md; scripts/operator/open_internal_review_video_candidate.ps1 |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_internal_review_video_candidate.ps1 |
| generated_from | ED-10as consumes ED-10ar and resolves the current-host full paths for the existing ignored MP4, ASS, and local manifest. |
| validation_command | Parse ED-10as and ED-10ar JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | MP4/ASS/manifest full paths resolved on current host; launcher command recorded; no render/replay/media modification; `episodes_tracked=false`; production/rights/public-use/publishing/monetization approvals remain false or pending. |
| review_status | access sheet only; no user review or decision requested now |
| next_action | Use the launcher only when a later supervisor asks for optional freeform observation. |

## `clip-ed10at-internal-review-observation-readback-001`

| field | value |
|---|---|
| title | ED-10at Internal Review Observation Readback |
| purpose | Consume the user's freeform observation after opening the ED-10as / ED-10ar internal review MP4 without turning it into production, public-use, rights, publishing, monetization, or approval state. |
| storage_class | tracked JSON/Markdown observation readback; no media artifact and no ignored episode output generated by this slice |
| repo_relative_path | docs/style_intent/internal-review-video-observation-readback.json; docs/style_intent/internal-review-video-observation-readback.md |
| open_command | see docs\\style_intent\\internal-review-video-observation-readback.md |
| generated_from | ED-10at consumes ED-10as access sheet plus ED-10ar internal review video candidate package, after repairing the stale local checkout assumption that had hidden those artifacts. |
| validation_command | Parse ED-10at, ED-10as, ED-10ar, and dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | Observation records `openability=pass`, `duration=expected_pass`, `subtitle_cue_coverage=pass_for_diagnostic_cue_probe`, `narrative_video_continuity=warning_not_representative_review`, `memo_like_appearance=warning_observed`, `review_guidance_clarity=partial_or_fail`, `new_render_run=false`, `new_media_created=false`, `stage_7_freeform_normalizer_used=false`, `user_observation_converted_to_approval=false`, and `episodes_tracked=false`. |
| review_status | observation readback only; no Review Card, no user-side work, no representative episode/video review, and no production/public approval |
| next_action | Build a representative micro-scene specimen with actual subtitle/script content only if continuing toward real internal review. Use `final-render-path-stage-4` only for a concrete render diagnostic gap; do not use stage-7 freeform normalization now. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10au-representative-micro-scene-internal-review-specimen-001`

| field | value |
|---|---|
| title | ED-10au Representative Micro-Scene Internal Review Specimen |
| purpose | Replace the ED-10at cue-label memo probe with a bounded internal-review specimen that contains actual Japanese subtitle/script content and enough scene continuity for later freeform review. |
| storage_class | tracked JSON/Markdown readback plus launcher; ignored same-machine MP4/ASS/local manifest under `episodes/` |
| repo_relative_path | docs/style_intent/representative-micro-scene-internal-review-specimen.json; docs/style_intent/representative-micro-scene-internal-review-specimen.md; scripts/operator/open_representative_micro_scene_internal_review_specimen.ps1 |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_internal_review_specimen.ps1 |
| generated_from | ED-10au consumes ED-10at observation readback, ED-10as access sheet, ED-10ar candidate package, source video/audio from the local JP pilot episode, and real transcript subtitles `sub_004`-`sub_006`. |
| validation_command | Parse ED-10au, ED-10at, ED-10as, ED-10ar, and dashboard JSON; run targeted subtitle/dashboard/review tests; ffprobe the ignored MP4; git diff --check; git diff --cached --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | MP4 exists on current host at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`, size `3538973` bytes, duration `9.18s`, resolution `1920x1080`, codecs `h264/aac`, access_state `verified_present`, and manifest_size_bytes `10743`. |
| review_status | access verified; no user review requested now; later observation must stay freeform with at most three look-for points |
| next_action | If a later supervisor asks for review, open the launcher and classify the next fix as script, timing/audio, visual layout, or render path; do not infer production/public approval. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10av-micro-scene-observation-frame-readback-001`

| field | value |
|---|---|
| title | ED-10av Micro-Scene Observation Frame Readback |
| purpose | Preserve the user's freeform observation after opening the ED-10au specimen and classify the next practical axis without treating the observation as approval. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, or media artifact |
| repo_relative_path | docs/style_intent/micro-scene-observation-frame-readback.json; docs/style_intent/micro-scene-observation-frame-readback.md |
| open_command | see docs\\style_intent\\micro-scene-observation-frame-readback.md |
| generated_from | ED-10av consumes `clip-ed10au-representative-micro-scene-internal-review-specimen-001`, preserving the user's observation that the development target looked different, evaluation was unclear, the artifact looked like a real scene rather than the earlier cue/memo probe, and the lower subtitle area may be affected by player UI. |
| validation_command | Parse ED-10av and source ED-10au JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render or media smoke is run in ED-10av. Source ED-10au remains the access-verified specimen; ED-10av records observation and classification only. |
| review_status | observation consumed as readback; not approval; no additional user review requested now |
| next_action | Clarify the review frame first; capture subtitle/player-UI evidence only if needed; build a v2 specimen only for confirmed source/scene mismatch; use final-render-path-stage-4 only for a concrete render-path gap. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `layout_broken_claimed=false`
- `player_ui_overlap_confirmed=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`
- `user_review_requested_now=false`

## `clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001`

| field | value |
|---|---|
| title | ED-10aw Grill-me Adoption Readback and Review-Frame Clarification Plan |
| purpose | Classify the local Grill-me skill as a bounded helper and prepare the next review-frame clarification direction without turning ED-10av observation into approval. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, media artifact, or skill-file staging |
| repo_relative_path | docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.json; docs/style_intent/grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md |
| open_command | see docs\\style_intent\\grill-me-adoption-readback-and-ed10aw-review-frame-clarification-plan.md |
| generated_from | ED-10aw consumes `clip-ed10av-micro-scene-observation-frame-readback-001`, records `.agents/skills/grill-me/SKILL.md` and `skills-lock.json` as untracked local helper files, and fixes the allowed Grill-me output contract before ED-10aw review-frame clarification work. |
| validation_command | Parse ED-10aw and source ED-10av JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render or media smoke is run in ED-10aw. The repo state was read as main aligned with origin/main, with only the untracked Grill-me helper and lock retained outside staging. |
| review_status | adoption boundary and review-frame direction ready; no additional user review requested now; not approval |
| next_action | Use review-frame-clarification first; capture subtitle/player-UI evidence, build a v2 specimen, or use final-render-path-stage-4 only if that specific condition is verified. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `next_agent_prompt_allowed=false`
- `agent_report_nested_prompt_allowed=false`
- `grill_me_project_resource_authority=false`
- `grill_me_skill_files_staged=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`

| field | value |
|---|---|
| title | ED-10ay Thank ED-10au Local Access Recovery Readback |
| purpose | Record current-host recovery of the ignored ED-10au representative micro-scene MP4/ASS/local manifest on the Thank terminal after tracked ED-10ax and the launcher were present but the local media were absent. |
| storage_class | tracked JSON/Markdown readback; regenerated MP4/ASS/local manifest remain ignored same-machine evidence under `episodes/` |
| repo_relative_path | docs/style_intent/thank-ed10au-local-access-recovery-readback.json; docs/style_intent/thank-ed10au-local-access-recovery-readback.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_internal_review_specimen.ps1 |
| generated_from | ED-10ay consumes ED-10ax and ED-10au tracked readbacks plus Thank-host source video/audio/transcript/edit_pack availability, then runs the existing bounded ED-10au local artifact writer for the same ignored output path. |
| validation_command | Parse ED-10ay JSON and dashboard JSON; ffprobe the generated MP4; run targeted subtitle/dashboard/review tests if tracked files changed; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | Initial MP4/ASS/manifest state was absent on the Thank host; source video/audio/transcript/edit_pack were present; bounded regeneration succeeded; final MP4 exists at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_internal_review_specimen/representative_micro_scene_internal_review_specimen.mp4`, size `3443682`, duration `9.18s`, H.264/AAC, 1920x1080, 30fps; ASS and local manifest are present. |
| review_status | access recovery only; no user review requested now; not approval |
| next_action | Use the existing ED-10au launcher on this host when a later supervisor asks to open the specimen. Keep ED-10ax as the review-frame surface and use screenshot/v2/final-render routes only under their recorded conditions. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `ignored_local_media_only=true`
- `representative_micro_scene_v2_created=false`
- `screenshot_capture_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10az-observation-readback-and-v2-route-decision-001`

| field | value |
|---|---|
| title | ED-10az Observation Readback and V2 Route Decision |
| purpose | Consume the user's ED-10ax-guided observation after opening the recovered ED-10au MP4 and decide the next route without treating the observation as approval. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, media artifact, v2 specimen, or tracked `episodes/` output |
| repo_relative_path | docs/style_intent/ed10az-observation-readback-and-v2-route-decision.json; docs/style_intent/ed10az-observation-readback-and-v2-route-decision.md |
| open_command | see docs\\style_intent\\ed10az-observation-readback-and-v2-route-decision.md |
| generated_from | ED-10az consumes `clip-ed10ax-review-frame-clarification-surface-001`, `clip-ed10ay-thank-ed10au-local-access-recovery-readback-001`, `clip-ed10au-representative-micro-scene-internal-review-specimen-001`, and the user's freeform observation after opening the recovered MP4. |
| validation_command | Parse ED-10az JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render, screenshot, media, or v2 specimen is created in ED-10az. The source MP4 was opened by the user after ED-10ay recovery; ED-10az records observation and route decision only. |
| review_status | observation consumed as readback; not approval; no additional user review requested now |
| next_action | Design `representative-micro-scene-v2-cut-window-and-review-purpose-alignment`; keep subtitle-layout screenshot capture, final-render-path stage-4, timing/audio, and another pure review-frame packet conditional only. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `subtitle_layout_failure_claimed=false`
- `player_ui_overlap_confirmed=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `representative_micro_scene_v2_created=false`
- `representative_micro_scene_v2_enabled=true`
- `screenshot_capture_created=false`
- `subtitle_layout_screenshot_capture_required_now=false`
- `final_render_path_stage_4_required_now=false`
- `timing_audio_first_route=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10bc-thank-v2-open-command-repair-readback-001`

| field | value |
|---|---|
| title | ED-10bc Thank V2 Open Command Repair Readback |
| purpose | Record and repair the Thank-terminal launcher path where the ED-10ba v2 MP4 was verified present but did not open visibly for the user. |
| storage_class | tracked JSON/Markdown readback plus launcher script repair; MP4/ASS/local manifest remain ignored same-machine evidence |
| repo_relative_path | docs/style_intent/thank-v2-open-command-repair-readback.json; docs/style_intent/thank-v2-open-command-repair-readback.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 |
| generated_from | ED-10bc consumes `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001` and `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`; it classifies the user-visible failure as `file_verified_but_user_visible_open_failed`, not media/render loss, after verifying MP4/ASS/local manifest presence and ffprobe readability. |
| validation_command | Capture pre-repair launcher stdout/stderr/exit code; verify MP4/ASS/local manifest and ffprobe; run repaired launcher `-NoInvoke` and default smoke; parse ED-10bc JSON and dashboard JSON; run targeted subtitle/dashboard tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | Repaired default launcher returned exit `0`, process name `vlc`, `open_attempt_status=start_process_attempted_not_observed`, and `classification=file_verified_but_user_visible_open_not_confirmed`; `-NoInvoke` prints path/size/fallback diagnostics without opening. |
| review_status | opener repaired with fallbacks; no immediate user review requested; no production/public/rights/publishing/monetization or micro-scene approval |
| next_action | If a later supervisor asks to view the v2 specimen, use the repaired opener first; if no player appears, use `-SelectVideo` or `-OpenFolder` before considering any media regeneration. |

Boundary flags remain false or pending:

- `new_v3_created=false`
- `new_render_run=false`
- `new_media_created=false`
- `screenshot_capture_created=false`
- `final_render_path_stage_4=false`
- `timing_audio_first_route=false`
- `stage_7_freeform_normalizer_used=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`

## `clip-ed10bb-thank-ed10ba-v2-local-access-recovery-readback-001`

| field | value |
|---|---|
| title | ED-10bb Thank ED-10ba V2 Local Access Recovery Readback |
| purpose | Record actual Thank-terminal access recovery for ED-10ba without tracking ignored local media or treating access evidence as approval. |
| storage_class | tracked JSON/Markdown readback only; MP4/ASS/local manifest remain ignored same-machine evidence |
| repo_relative_path | docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.json; docs/style_intent/thank-ed10ba-v2-local-access-recovery-readback.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 |
| generated_from | ED-10bb consumes `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001` and records actual Thank-terminal recovery from `C:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`: initial ignored v2 MP4/ASS/local manifest absent, source video/audio/transcript/edit_pack present, bounded writer run, final `access_state=verified_present`. |
| validation_command | Parse ED-10bb JSON and dashboard JSON; verify ED-10ba tracked files are present; verify builder symbol exists; ffprobe the regenerated MP4; run targeted subtitle/dashboard tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | Thank-host regeneration completed on 2026-07-01 JST. Final MP4 exists with size `4627079`, duration `11.9s`, H.264/AAC, 1920x1080, 30fps; ASS size `1529`; local manifest size `13824`; `git ls-files episodes` remains empty. |
| review_status | access recovery complete with `verified_present`; no immediate user review requested; no production/public/rights/publishing/monetization or micro-scene approval |
| next_action | Use the opener only if a later supervisor asks for freeform v2 cut-window/review-purpose observation. Regenerate again only if the ignored outputs disappear and source inputs are still present. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `wrong_host_regeneration=false`
- `screenshot_capture_created=false`
- `final_render_path_stage_4=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ba-representative-micro-scene-v2-cut-window-and-review-purpose-alignment-001`

| field | value |
|---|---|
| title | ED-10ba Representative Micro-Scene V2 Cut Window / Review Purpose Alignment |
| purpose | Produce a bounded v2 internal-review specimen that answers ED-10az: the recovered ED-10au MP4 opened, but the user could not tell what to judge, both cut edges felt too tight for cut-quality review, and the subtitle strategy did not clarify clipping/cutout usefulness. |
| storage_class | tracked JSON/Markdown readback plus launcher; generated MP4/ASS/local manifest remain ignored same-machine evidence under `episodes/` |
| repo_relative_path | docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.json; docs/style_intent/representative-micro-scene-v2-cut-window-and-review-purpose-alignment.md |
| open_command | powershell -ExecutionPolicy Bypass -File scripts\\operator\\open_representative_micro_scene_v2_cut_window_review_purpose_alignment.ps1 |
| generated_from | ED-10ba consumes `clip-ed10az-observation-readback-and-v2-route-decision-001`, verifies the source video/audio/transcript/edit_pack on the current host, generates the ignored local v2 specimen with `write_representative_micro_scene_v2_cut_window_review_purpose_alignment_local_artifacts`, then records tracked access and review-purpose readback. |
| validation_command | Parse ED-10ba JSON and dashboard JSON; ffprobe the generated MP4; run targeted subtitle/dashboard tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | Bounded regeneration succeeded. Final MP4 exists at `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_micro_scene_v2_cut_window_review_purpose_alignment/representative_micro_scene_v2_cut_window_review_purpose_alignment.mp4`, size `4723658`, duration `11.9s`, H.264/AAC, 1920x1080, 30fps. The ASS and local manifest are present in the same ignored folder. |
| review_status | v2 specimen ready for later freeform cut-window/review-purpose judgement; no immediate user review requested; not approval |
| next_action | Use the ED-10ba launcher only when a later supervisor asks to open the v2 specimen. Judge whether the wider `38.50s`-`50.40s` window and visible internal-review purpose label reduce review friction before considering subtitle strategy, screenshot capture, timing/audio, or render-path stage-4. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `subtitle_layout_failure_claimed=false`
- `player_ui_overlap_confirmed=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=true`
- `new_media_created=true`
- `representative_micro_scene_v2_created=true`
- `diagnostic_internal_review_subtitles_only=true`
- `screenshot_capture_created=false`
- `subtitle_layout_screenshot_capture_required_now=false`
- `final_render_path_stage_4_required_now=false`
- `timing_audio_first_route=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ax-review-frame-clarification-surface-001`

| field | value |
|---|---|
| title | ED-10ax Review-Frame Clarification Surface |
| purpose | Turn the ED-10aw plan into a concrete review-frame surface for the ED-10au specimen so a later reviewer knows what to judge, what not to judge, how to interpret ED-10av, and which next route to use. |
| storage_class | tracked JSON/Markdown readback; no render, replay, screenshot, media artifact, v2 specimen, stage-7 normalizer, or skill-file staging |
| repo_relative_path | docs/style_intent/review-frame-clarification-surface.json; docs/style_intent/review-frame-clarification-surface.md |
| open_command | see docs\\style_intent\\review-frame-clarification-surface.md |
| generated_from | ED-10ax consumes `clip-ed10aw-grill-me-adoption-readback-and-review-frame-clarification-plan-001` and `clip-ed10av-micro-scene-observation-frame-readback-001`, preserving the ED-10av observation as classification evidence rather than approval. |
| validation_command | Parse ED-10ax, ED-10aw, ED-10av, and dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; git diff --cached --check if staged; verify git ls-files episodes remains empty. |
| latest_local_smoke | No local render, screenshot, media, or v2 specimen is created in ED-10ax. The artifact records a later freeform review frame with exactly three look-for points and keeps Grill-me a local helper, not repo policy. |
| review_status | review-frame clarification surface ready for later use; no user review requested now; not approval |
| next_action | Use the ED-10ax surface for later freeform review. Use subtitle-layout-screenshot-capture only for lower subtitle/player-UI classification, representative-micro-scene-v2 only for confirmed source/scene mismatch, and final-render-path-stage-4 only for a concrete render-path gap. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `monetization_acceptance=false`
- `micro_scene_accepted=false`
- `user_observation_converted_to_approval=false`
- `layout_broken_claimed=false`
- `player_ui_overlap_confirmed=false`
- `fixed_form_required=false`
- `yes_no_required=false`
- `next_agent_prompt_allowed=false`
- `agent_report_nested_prompt_allowed=false`
- `grill_me_project_resource_authority=false`
- `grill_me_skill_files_staged=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_media_created=false`
- `stage_7_freeform_normalizer_used=false`

## `clip-ed10ar-internal-review-video-candidate-package-001`

| field | value |
|---|---|
| title | ED-10ar Internal Review Video Candidate Package |
| purpose | Assemble a tracked readback for an internal-review video candidate package from existing ignored diagnostic MP4/ASS/manifest output without running a new render or granting production/public/rights/render approval. |
| storage_class | tracked JSON/Markdown |
| repo_relative_path | docs/style_intent/internal-review-video-candidate-package.json; docs/style_intent/internal-review-video-candidate-package.md |
| open_command | notepad docs\\style_intent\\internal-review-video-candidate-package.md |
| generated_from | ED-10ar consumes ED-10aq stage-5 user-decision-ready and reuses the existing same-machine ignored ED-10af/ED-10al diagnostic MP4, ASS, and local manifest as the internal review video candidate package. |
| validation_command | Parse ED-10ar JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | Existing Output First: video/ASS/manifest are present under ignored `episodes/` paths, `duration_seconds=4.2`, `resolution=1920x1080`, `video_codec=h264`, `audio_codec=aac`, `stream_count=2`, `new_render_run=false`, `tracked_binary_artifact_created=false`, `episodes_tracked=false`, and production/rights/public-use/render approvals closed and separate. |
| review_status | internal-review video candidate package only; no user review or decision requested now |
| next_action | Use `optional-internal-review-video-observation` only for a later freeform observation, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |
## `clip-ed10aq-production-limitation-lift-stage-5-user-decision-ready-001`

| field | value |
|---|---|
| title | ED-10aq Production Limitation Lift Stage 5 User Decision Ready |
| purpose | Verify that ED-10ap remains a freeform user decision surface only without asking for a decision now or granting production/public/rights/render approval. |
| storage_class | tracked JSON/Markdown |
| repo_relative_path | docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.json; docs/style_intent/subtitle-production-limitation-lift-stage-5-user-decision-ready.md |
| open_command | notepad docs\\style_intent\\subtitle-production-limitation-lift-stage-5-user-decision-ready.md |
| generated_from | ED-10aq consumes ED-10ap stage-4 user decision card and records gate checks, separation, and no-relapse guards. |
| validation_command | Parse ED-10aq JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; git diff --check; verify git ls-files episodes remains empty. |
| latest_local_smoke | ED-10aq records answer_style=freeform, fixed_form_required=false, fixed_choice_rows_allowed=false, yes_no_rows_emitted=false, required_labels=[], screenshot_required=false, user_decision_requested_now=false, no render/replay/media, and production/rights/public-use/render approvals closed and separate. |
| review_status | stage-5 user-decision-ready packet only; no user decision requested now |
| next_action | Treat as complete stage-5 user-decision-ready packet; use final-render-path-stage-4 only if a concrete diagnostic gap is found. |

## `clip-ed10ap-production-limitation-lift-stage-4-user-decision-card-001`

| Field | Value |
|---|---|
| title | ED-10ap Production Limitation Lift Stage 4 User Decision Card |
| purpose | Convert the ED-10ao owner-review preparation entries into a future short stage-4 user decision card without approving production/public use or asking for a user decision now. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-4-user-decision-card.json` |
| open_command | notepad docs\\style_intent\\subtitle-production-limitation-lift-stage-4-user-decision-card.md |
| source_owner_review_prep | `clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001` |
| source_decision_packet | `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` |
| source_gate_matrix | `clip-ed10am-production-limitation-lift-stage-1-001` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| decision_topics | subtitle design / visual acceptance; production render readiness; rights / publishing / public-use clearance |
| generated_from | ED-10ap uses ED-10ao owner-review groups and records plain-language future question shape, available and missing evidence, safe freeform answer hints, internal normalization hints, stop boundary, and unsafe overclaiming examples for each topic. |
| validation_command | Parse ED-10ap JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10ap has exactly three future decision topics, preserves ED-10ao and ED-10an source links, keeps future user answers freeform, emits no fixed user form or fixed-choice rows, requires no screenshot path, exposes no hidden schema as user input, and keeps all production/public flags false or pending. |
| review_status | No new Review Card. This is future user decision card only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Use `production-limitation-lift-stage-5-user-decision-ready`, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `user_decision_requested_now=false`
- `fixed_user_form_emitted=false`
- `fixed_choice_rows_emitted=false`
- `screenshot_required=false`
- `hidden_schema_exposed_to_user=false`
- `final_render_path_approved=false`

## `clip-ed10ao-production-limitation-lift-stage-3-owner-review-prep-001`

| Field | Value |
|---|---|
| title | ED-10ao Production Limitation-Lift Stage 3 Owner-Review Prep |
| purpose | Convert the ED-10an three decision groups into owner-review preparation entries without approving production/public use or asking for a user decision now. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-3-owner-review-prep.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-stage-3-owner-review-prep.md` |
| source_decision_packet | `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001` |
| source_gate_matrix | `clip-ed10am-production-limitation-lift-stage-1-001` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| owner_review_groups | subtitle design / visual acceptance; production render readiness; rights / publishing / public-use clearance |
| generated_from | ED-10ao uses ED-10an decision groups and records owner category, available evidence, missing evidence, safe next action, unsafe overclaiming, can-proceed-without-user-judgement, and must-stop-before-approval fields. |
| validation_command | Parse ED-10ao JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10ao groups exactly three owner-review entries, preserves ED-10an as the source decision packet, preserves ED-10am and ED-10al source links, emits no fixed user form, and keeps all production/public flags false or pending. |
| review_status | No new Review Card. This is owner-review preparation only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-4-user-decision-card`, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `user_decision_requested_now=false`
- `fixed_user_form_emitted=false`
- `fixed_choice_rows_emitted=false`
- `final_render_path_approved=false`

## `clip-ed10an-production-limitation-lift-stage-2-decision-packet-001`

| Field | Value |
|---|---|
| title | ED-10an Production Limitation-Lift Stage 2 Decision Packet |
| purpose | Convert the ED-10am nine-gate matrix into three bounded decision-preparation groups without approving production/public use. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-2-decision-packet.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-stage-2-decision-packet.md` |
| source_gate_matrix | `clip-ed10am-production-limitation-lift-stage-1-001` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| decision_groups | subtitle design / visual acceptance; production render readiness; rights / publishing / public-use clearance |
| generated_from | ED-10an uses ED-10am gate ownership, missing-evidence rows, and unsafe-overclaiming examples to prepare user-decision inputs without requesting immediate judgement. |
| validation_command | Parse ED-10an JSON plus dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10an groups exactly three decision groups, preserves ED-10am as the source matrix, preserves ED-10al diagnostic metadata (`4.2s`, `1920x1080`, `h264`, `aac`, two streams), and keeps all production/public flags false or pending. |
| review_status | No new Review Card. This is decision-preparation readback only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-3-owner-review-prep`, or use `final-render-path-stage-4` only if a concrete diagnostic gap is found. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `user_decision_requested_now=false`
- `final_render_path_approved=false`

## `clip-ed10am-production-limitation-lift-stage-1-001`

| Field | Value |
|---|---|
| title | ED-10am Production Limitation-Lift Stage 1 |
| purpose | Convert ED-10al diagnostic final-path rehearsal evidence into a gate-by-gate production limitation-lift preparation packet without approving production/public use. |
| storage class | Tracked docs/data artifact; references ignored same-machine diagnostic outputs but does not track media. |
| repo_relative_path | `docs/style_intent/subtitle-production-limitation-lift-stage-1.md` |
| metadata_json | `docs/style_intent/subtitle-production-limitation-lift-stage-1.json` |
| open_command | `see docs\style_intent\subtitle-production-limitation-lift-stage-1.md` |
| primary_diagnostic_rehearsal_source | `clip-ed10al-final-render-path-stage-3-rehearsal-001` |
| stage_2_source | `clip-ed10ak-final-render-path-stage-2-replayability-001` |
| active_diagnostic_proof_source | `clip-ed10af-l2-render-path-selector-probe-001` |
| gates | diagnostic rehearsal evidence; production subtitle design acceptance; production render acceptance; creative acceptance; rights status; publishing acceptance; public-use permission; tracked media boundary; same-machine ignored evidence boundary |
| generated_from | ED-10am uses the ED-10al diagnostic rehearsal packet and records owners, missing evidence, and unsafe-overclaiming examples for each limitation-lift gate. |
| validation_command | Parse ED-10am JSON plus related style intent JSON and dashboard JSON; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty and referenced local outputs are ignored. |
| latest_local_smoke | ED-10al source evidence remains `4.2s`, `1920x1080`, `h264`, `aac`, generated ignored ASS/MP4/manifest, and style-token/body/badge/safe-area survival true. ED-10am itself runs no render. |
| review_status | No new Review Card. This is decision-preparation readback only, not production subtitle design, production render, creative, rights, publishing, or public-use acceptance. |
| next_action | Start `production-limitation-lift-stage-2-decision-packet`, or use `final-render-path-stage-4` only if more diagnostic evidence is genuinely needed. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
- `tracked_binary_artifact_created=false`
- `episodes_tracked=false`
- `new_render_run=false`
- `new_rehearsal_run=false`
- `final_render_path_approved=false`

## `clip-ed10ae-render-path-selector-contract-probe-001`

| Field | Value |
|---|---|
| title | ED-10ae Render Path Selector Contract Probe |
| purpose | Define the static selector-to-render-path input contract for a later render adapter without running render or creating video/audio/frame artifacts. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-render-path-selector-contract.md` |
| metadata_json | `docs/style_intent/subtitle-render-path-selector-contract.json` |
| open_command | `see docs\style_intent\subtitle-render-path-selector-contract.md` |
| source_style_family_palette_artifact | `clip-ed10ad-style-family-palette-axis-proof-001` |
| source_visual_selector_artifact | `clip-ed10ac-visual-selector-proof-001` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10ae bounded static contract/readback slice using ED-10ad examples and L0 No Render. |
| validation_command | Parse style intent registry, preset selector, ED-10ac proof, ED-10ad proof, ED-10ae contract, dashboard JSON, and font candidates; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | The tracked contract represents all six semantic presets and lists semantic preset id, preset key, speaker/emotion/readability axes, family id, palette route, font family role, font size scale, outline/shadow token, badge/accent/backplate/body text color tokens, motion primitive, and safe-area/line-break behavior. Body text color remains `stable_default_body_text`; no render artifact is created. |
| review_status | No Review Card and no user-side work. The contract is static readback only and records later L2 tiny render path probe triggers as a separate milestone. |
| next_action | Use this selector-to-render-path contract before opening a later L2 tiny render probe. Production limitation-lift, rights, publishing, and public-use clearance remain separate routes. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10ad-style-family-palette-axis-proof-001`

| Field | Value |
|---|---|
| title | ED-10ad Style Family / Palette Axis Proof |
| purpose | Group the ED-10ac semantic preset examples by style family and palette route without changing body text color policy or running a render. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-style-family-palette-proof.html` |
| metadata_json | `docs/style_intent/subtitle-style-family-palette-proof.json` |
| open_command | `see docs\style_intent\subtitle-style-family-palette-proof.html` |
| source_visual_selector_artifact | `clip-ed10ac-visual-selector-proof-001` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10ad bounded static proof/readback slice using ED-10ac examples and L0 No Render / Existing Output First. |
| validation_command | Parse style intent registry, preset selector, ED-10ac visual selector proof, ED-10ad style-family/palette proof, dashboard JSON, and font candidates; run targeted subtitle/dashboard/review tests; `git diff --check`; verify `git ls-files episodes` remains empty. |
| latest_local_smoke | The tracked proof represents all six semantic presets and groups them into dialogue current Keifont, emphasis energy, quiet soft readability, ominous inner voice, narration, and system note families. Palette routes are speaker identity blue, high energy warm, quiet cool, ominous dark, narration neutral green, and system neutral. Body text color remains `stable_default_body_text`; palette variation stays on badge/accent/backplate surfaces. |
| review_status | No Review Card and no user-side work. The proof introduces no new style family, no new palette, no body text color policy change, no production route, and no rights, publishing, or public-use decision. |
| next_action | Use this static axis proof before a later render-path probe. Any actual new style family, new palette, body text color policy change, production limitation-lift, rights, publishing, or public-use clearance remains a separate route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10ac-visual-selector-proof-001`

| Field | Value |
|---|---|
| title | ED-10ac Visual Selector Proof |
| purpose | Make the ED-10ab semantic preset examples visually inspectable as token differences without reopening raw numeric review or running a new render. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-visual-selector-proof.html` |
| metadata_json | `docs/style_intent/subtitle-visual-selector-proof.json` |
| open_command | `see docs\style_intent\subtitle-visual-selector-proof.html` |
| source_selector_artifact | `clip-ed10ab-subtitle-preset-selector-001` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | ED-10ac bounded visual selector proof slice using ED-10ab selector examples and L1 Existing Output First. |
| validation_command | Parse `docs/style_intent/subtitle-style-intent-registry.json`, parse `docs/style_intent/subtitle-preset-selector.json`, parse `docs/style_intent/subtitle-visual-selector-proof.json`, parse dashboard JSON, run targeted subtitle/dashboard/review tests, `git diff --check`, and verify `git ls-files episodes` remains empty. |
| latest_local_smoke | The tracked proof represents neutral dialogue intensity 0, shout intensity 2, whisper intensity 1, ominous intensity 2, narration intensity 0, and system note intensity 0. Each card shows intent axes, preset key, font family role, font size scale, outline/shadow token, badge color token, accent color token, backplate/box token, motion placeholder, safe-area/line-break behavior, stable body text color token, and human review status. |
| review_status | No Review Card. The proof introduces no new style family, palette, body text color policy, production route, rights, publishing, or public-use decision. Optional user-side work is open-only freeform observation, maximum 3 points. |
| next_action | Use this proof as the current tracked selector readback. Future movement should be a separate new axis such as style-family exploration, palette proposal, line-break policy tuning, production limitation-lift, final render-path probe, rights, publishing, or public-use clearance. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10ab-subtitle-preset-selector-001`

| Field | Value |
|---|---|
| title | ED-10ab Subtitle Preset Selector |
| purpose | Connect the ED-10aa semantic intent registry to a deterministic selector that maps subtitle intent axes to style token candidates without asking for repeated raw numeric reviews. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/style_intent/subtitle-preset-selector.json` |
| metadata_json | `docs/style_intent/subtitle-preset-selector.json` |
| open_command | `see docs\style_intent\subtitle-preset-selector.json` |
| source_registry_artifact | `clip-ed10aa-subtitle-style-intent-registry-001` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| implementation | `src/integrations/render/subtitle_preset_selector.py` |
| generated_from | Prompt-authorized ED-10ab selector/readback slice consuming the ED-10aa axes and preserving ED-10z as existing visual evidence. |
| validation_command | Parse `docs/style_intent/subtitle-style-intent-registry.json`, parse `docs/style_intent/subtitle-preset-selector.json`, regenerate docs dashboard, run targeted subtitle/dashboard tests, `git diff --check`, and verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Selector examples cover neutral dialogue intensity 0, shout intensity 2, whisper intensity 1, ominous intensity 2, narration, and system note. Each returns font family role, font size scale, outline/shadow strength, badge color, accent color, backplate/box, motion placeholder, safe-area/line-break behavior, and stable body text color token. |
| review_status | No new Review Card. No new visual proof or style family is introduced, and the same Candidate 0-3 comparison remains closed. |
| next_action | Use this selector as a deterministic preset readback before any future visual selector proof. Open a separate route for new style family, new palette, body text color policy change, production route, rights, publishing, or public-use decisions. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10aa-subtitle-style-intent-registry-001`

| Field | Value |
|---|---|
| title | ED-10aa Subtitle Style Intent Registry |
| purpose | Record semantic subtitle style-control axes so future agents can map speaker, emotion, intensity, utterance role, and readability tags to presets instead of asking for repeated tiny numeric outline/shadow/opacity reviews. |
| storage class | Tracked docs/readback artifact. |
| repo_relative_path | `docs/SUBTITLE_STYLE_INTENT_REGISTRY.md` |
| metadata_json | `docs/style_intent/subtitle-style-intent-registry.json` |
| open_command | `see docs\SUBTITLE_STYLE_INTENT_REGISTRY.md` |
| source_render_path_artifact | `clip-ed10z-tiny-render-path-nearer-probe-001` |
| source_previous_artifact | `clip-ed10y-candidate2-carry-forward-001` |
| source_proof_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| generated_from | Prompt-authorized ED-10aa design/readback slice consuming the latest review that Candidate 0/2 are acceptable, Candidate 1/3 are thin, primary review samples were too small, and future styling should move toward emotion/speaker/readability semantics. |
| validation_command | Parse `docs/style_intent/subtitle-style-intent-registry.json`, regenerate docs dashboard, run targeted subtitle/dashboard tests, `git diff --check`, and verify `git ls-files episodes` remains empty. |
| latest_local_smoke | Registry records axes `speaker_id`, `speaker_role`, `emotion`, `intensity`, `utterance_role`, and `readability_priority`; maps them to font family, font size scale, outline/shadow, badge color, accent color, backplate/box, motion placeholder, and safe-area/line-break tokens; keeps body text color stable by default; and marks human review as required only for new style family, new color palette, body text color policy change, production-route change, rights, publishing, or public-use decisions. |
| review_status | No new Review Card. The same Candidate 0-3 comparison, Keifont acceptance, cut_002/cut_003 review, and cut_008/sub_096 pass remain closed. |
| next_action | Use this registry before future subtitle style work. ED-10z remains the current render-path-nearer probe source and now has refreshed same-machine local proof output; any limitation-lift or final render-path work should be opened as a separate route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

## `clip-ed10z-tiny-render-path-nearer-probe-001`

| Field | Value |
|---|---|
| title | ED-10z Tiny Render-Path-Nearer Probe |
| purpose | Preserve `clip-ed10y-candidate2-carry-forward-001` as source/previous state and pass Candidate 2 through the current FFmpeg/libass diagnostic path as a tiny local readback probe. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.html` |
| metadata_json | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.json` |
| open_command | `.\open-current-proof.ps1` |
| source_previous_artifact | `clip-ed10y-candidate2-carry-forward-001` |
| source_review_artifact | `clip-ed10y-candidate2-carry-forward-001` |
| source_proof_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10z_tiny_render_path_nearer_probe --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10z_tiny_render_path_nearer_probe --format json` plus targeted tests. |
| latest_local_smoke | ED-10z actual rerun with explicit FFmpeg/FFprobe paths returned `artifact_id=clip-ed10z-tiny-render-path-nearer-probe-001`, `proof_profile=ed10z_tiny_render_path_nearer_probe`, `source_review_artifact_id=clip-ed10y-candidate2-carry-forward-001`, `visual_proof_status=available_requires_human_review`, `review_card_status=withheld_tiny_render_path_nearer_probe_completed`, `focused_proof_review.status=tiny_render_path_nearer_probe_completed`, `subtitle_overlay_available_count=1`, Candidate 2 as current lead, Candidate 0 as fallback/reference, Candidate 1 / 3 as held references, and no same-candidate review request. |
| review_status | No new Review Card. The latest Candidate 0-3 review is already consumed; this is diagnostic probe readback only. |
| next_action | Use this as refreshed same-machine local readback only. Any production limitation-lift, final render-path, rights, publishing, or public-use decision remains a separate route. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored HTML/JSON/PNG/MP4/ASS artifacts themselves. Other
worktrees should treat missing `episodes/` review assets as local evidence
absence, not as a tracked Git failure. `git ls-files episodes` should remain
empty.

## `clip-ed10y-candidate2-carry-forward-001`

| Field | Value |
|---|---|
| title | ED-10y Candidate 2 Carry-Forward Pack |
| purpose | Consume the latest ED-10w/ED-10x freeform review, promote Candidate 2 as provisional bounded-decoration lead, retain Candidate 0 as fallback, and hold Candidate 1 / 3 because they read too thin. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.html` |
| metadata_json | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.json` |
| open_command | `.\open-current-proof.ps1` |
| source_review_artifact | `clip-ed10w-subtitle-presentation-review-pack-001` |
| source_proof_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10y_candidate2_carry_forward --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10y_candidate2_carry_forward --format json` plus targeted tests. |
| latest_local_smoke | Same-machine ED-10y regeneration writes the same current `subtitle_presentation_review_pack.html` / `.json` path with `artifact_id=clip-ed10y-candidate2-carry-forward-001`, `review_card.action_type=NO_REVIEW_CARD_REVIEW_CONSUMED`, Candidate 2 as `provisional_bounded_decoration_lead`, Candidate 0 as `fallback_reference`, Candidate 1 / 3 as `held_reference`, and `render_path_readiness.status=candidate2_tiny_render_path_nearer_diagnostic_probe_completed`. Full-frame context is no longer constrained to the old cramped 220px proof width. |
| review_status | Latest freeform review consumed. Do not request another Candidate 0-3 comparison review, general Keifont acceptance, cut_002/cut_003 review, or the same cut_008 dense/multiline pass. |
| next_action | Use Candidate 2 as the provisional bounded-decoration lead. Next movement should be a genuinely new axis such as production limitation-lift or final render-path probe, not another same-candidate comparison. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored HTML/JSON/PNG/MP4/ASS artifacts themselves. Other
worktrees should treat missing `episodes/` review assets as local evidence
absence, not as a tracked Git failure. `git ls-files episodes` should remain
empty.

## `clip-ed10w-subtitle-presentation-review-pack-001`

| Field | Value |
|---|---|
| title | ED-10w Subtitle Presentation Review Pack |
| purpose | Combine the already-passed ED-10v dense/stress evidence with one genuinely new review axis: bounded decoration adjustment plus render-path readiness. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.html` |
| metadata_json | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_presentation_review_pack.json` |
| open_command | `.\open-current-proof.ps1` |
| source_review_artifact | `clip-ed10r-keifont-dense-stress-proof-001` |
| source_comparison_artifact | `clip-ed10o-multifont-focused-review-001` |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10w_subtitle_presentation_review_pack --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10w_subtitle_presentation_review_pack --format json` plus targeted tests. |
| latest_local_smoke | ED-10x regeneration keeps the same artifact/path and adds compact subtitle-body crops, SPK badge crops, and Candidate Delta Readback. Same-machine readback: Candidate 0 baseline `outline=7`, `shadow=2`, badge text opacity `1.0`; Candidate 1 `outline=5`, `shadow=1`; Candidate 2 badge text/background opacity `0.435/0.122`; Candidate 3 combines both axes. All Candidate 1-3 delta statuses are `visible`; full-frame images remain secondary click-through context. |
| review_card | One updated new-axis Review Card: `bounded_decoration_adjustment + render_path_readiness`. It asks whether Candidate 0 remains best, whether Candidate 1/2/3 is preferable, and whether the render-path probe should proceed. It does not ask for another general `cut_002` / `cut_003` Keifont review and does not ask for another pass/fail judgement on the same `cut_008` multiline evidence. |
| bounded_candidates | `ed10w_current_pass_reference`, `ed10w_lighter_outline_shadow_pressure`, `ed10w_badge_label_pressure_adjustment`, `ed10w_balanced_combined_low_risk` |
| render_path_readiness | Diagnostic decision card only. It may authorize a later tiny render-path probe, but it is not production render acceptance. |
| review_status | Ready for one freeform subtitle presentation review after ED-10x candidate-delta visibility fix. |
| next_action | Review the crop-first pack once and choose whether Candidate 0 remains best, Candidate 1/2/3 is preferable, or only the tiny render-path readiness probe should proceed. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked generator, docs, dashboard metadata, and
tests but not the ignored HTML/JSON/PNG/MP4/ASS artifacts themselves. Other
worktrees should treat missing `episodes/` review assets as local evidence
absence, not as a tracked Git failure. `git ls-files episodes` should remain
empty.

## `clip-ed10r-keifont-dense-stress-proof-001`

| Field | Value |
|---|---|
| title | ED-10r / ED-10u / ED-10v Keifont Dense/Stress Proof |
| purpose | Treat Keifont as diagnostic representative normal-dialogue provisional baseline from the ED-10n/ED-10o review history, avoid another general `cut_002` / `cut_003` acceptance review, and record the corrected `cut_008` multiline/dense-stress proof as ED-10v diagnostic pass. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/current_proof_focused_review.html` |
| detailed_overlay_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| representative_report | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/representative_visual_proof_report.html` |
| open_command | Fallback from `.\open-current-proof.ps1`; root launcher now opens the ED-10w review pack first. |
| generated_from | `build-subtitle-overlay-visual-proof --proof-profile ed10r_keifont_dense_stress_proof --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --target-cut cut_008` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_008 --typography-decoration-candidate-id ed10l_keifont_pop_dialogue_candidate --proof-profile ed10r_keifont_dense_stress_proof --format json` plus targeted tests. |
| latest_validation_result | Same-machine ED-10u regeneration returned `artifact_id=clip-ed10r-keifont-dense-stress-proof-001`, `proof_profile=ed10r_keifont_dense_stress_proof`, `target_cuts=[cut_008]`, `visual_proof_status=available_requires_human_review`, `review_card_status=review_card_allowed_after_scope_checks`, `subtitle_overlay_available_count=1`, `focused_proof_review.status=dense_stress_keifont_proof_ready`, `font_visual_evidence.status=valid_requested_keifont_visual_evidence`, `requested_font_family=Keifont`, `resolved_font_family=Keifont`, `resolved_font_file=C:/Users/PLANNER007/AppData/Local/Microsoft/Windows/Fonts/keifont.ttf`, `multiline_wrap_evidence.status=multiline_wrap_evidence_surfaced`, `multiline_wrap_evidence.subtitle_id=sub_096`, `wrapped_line_count=2`, `screenshot_count=1`, `screenshot_role=multiline_wrap_1`, `screenshot_path=episodes/.../subtitle_overlay_reference/subtitle_overlay_visual_proof_cut_008.sample_multiline_wrap_1.png`, `focused_html_multiline_image_max_width=220px`, `production_candidate=false`, and `rights_status=pending`. ED-10v then consumed the user review as `diagnostic_dense_stress_passed` for subtitle display / all-pass, without changing production/public gates. |
| review_memory | `prior_review_count=3+`; accepted scope is diagnostic representative review / provisional normal-dialogue baseline / diagnostic dense-stress pass; not accepted scope is production subtitle design, production render, creative acceptance, rights, publishing, public use; next non-redundant axes are linebreak policy readback, bounded decoration adjustment, future shared subtitle layout policy, production limitation-lift, or render-path probe; repeated general review is false. |
| review_card | Withheld after pass: do not emit another Review Card for the same corrected `cut_008` multiline/dense-stress evidence, and do not re-decide general Keifont acceptance from `cut_002` / `cut_003`. |
| review_status | ED-10v records current dense/stress + multiline/wrap route as diagnostic pass with valid same-machine Keifont evidence. This is still diagnostic review, not production subtitle design, render, creative, rights, publishing, or public-use acceptance. |
| next_action | Move only through a genuinely new axis: line-break policy tuning, bounded outline/shadow/badge adjustment, production limitation-lift, or render-path probe. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked code, docs, and tests but not the ignored
MP4/PNG/ASS files themselves. Other worktrees should treat missing
`episodes/` proof assets as local evidence absence, not as a tracked Git
failure. `git ls-files episodes` should remain empty.

## `clip-ed10g-noto-overlay-proof-001`

| Field | Value |
|---|---|
| title | ED-10g Noto Sans JP Diagnostic Overlay Proof |
| purpose | Apply the selected `noto_sans_jp_clean_outline` typography / decoration base to the `cut_002` / `cut_003` diagnostic subtitle overlay proof. |
| storage class | Local retained artifact; same-machine evidence only. |
| repo_relative_path | `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/subtitle_overlay_visual_proof_report.html` |
| open_command | Historical local proof path only; root `.\open-current-proof.ps1` now opens the ED-10r dense/stress proof. |
| generated_from | `build-subtitle-overlay-visual-proof --typography-decoration-candidate-id noto_sans_jp_clean_outline` reading existing ignored episode source media, `edit_pack.json`, `material_ledger.json`, and R3 review artifacts. |
| validation_command | `uvx --with pillow python -m src.cli.main build-subtitle-overlay-visual-proof --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --review-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review --target-cut cut_002 --target-cut cut_003 --typography-decoration-candidate-id noto_sans_jp_clean_outline --format json` plus targeted tests. |
| latest_validation_result | `git diff --check` clean; `uvx pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` -> `18 passed, 8 skipped`; Pillow-enabled supplement `uvx --with pillow pytest -q tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py` -> `13 passed`. |
| latest_local_smoke | Same-machine generation on 2026-06-16 JST returned `visual_proof_status=available_requires_human_review`, `style_candidate_id=noto_sans_jp_clean_outline`, `typography_decoration_candidate_id=noto_sans_jp_clean_outline`, `subtitle_overlay_available_count=2`, `production_candidate=false`, `rights_status=pending`, and `production_usage_allowed=false`. JSON readback resolved the `Noto Sans JP` route with `font_file_status=candidate_primary_font_file_found`, `font_size=124`, `font_size.readback=round(frame_height * 0.115)`, `outline=11`, `outline.readback=max(2, round(font_size * 0.086))`, `bbox_wrapping_applied=true`, `explicit_ass_line_breaks=true`, `one_character_orphan_present=false`, and `suspicious_tail_line_present=false`. Both target cuts had MP4/PNG/ASS assets, the `cut_002` and `cut_003` PNG frames were inspected as nonblank 1920x1080 local visual artifacts, and a readback-based bbox/safe-area check reported no computed failures. |
| human_visual_judgement | Accepted on 2026-06-16 JST for the ED-10g diagnostic route, then superseded for styling on 2026-06-17 by a new review that says the proof is not accepted as-is. |
| review_status | Historical diagnostic proof / current reference only. No production subtitle design, render, creative, rights, publishing, public-use, or upload acceptance. |
| next_action | Keep as historical reference. The current selected proof is `clip-ed10i-meiryo-overlay-proof-001`. |

`status-episode` can still report global `operator_review.review_ready=false`
because the broader R3 artifact set is missing legacy `visual_proof_cut_001.png`.
That global blocked state is separate from this scoped ED-10g `cut_002` /
`cut_003` proof readback.

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`

Remote Git can verify the tracked code, docs, and tests but not the ignored
MP4/PNG/ASS files themselves. Other worktrees should treat missing
`episodes/` proof assets as local evidence absence, not as a tracked Git
failure.

## `clip-docs-dashboard-001`

| Field | Value |
|---|---|
| title | Docs Wiki Dashboard v1.5 |
| purpose | Make the tracked Markdown corpus readable as a project wiki/dashboard with current focus, feature progress, active artifacts, doc-health findings, and next review items. |
| storage class | Tracked docs artifact; portable Git evidence. |
| repo_relative_path | `docs/dashboard/index.html` |
| metadata_json | `docs/dashboard/project-status.json` |
| features_index | `docs/features/index.md` |
| open_command | `.\open-dashboard.ps1` |
| generated_from | `build-docs-dashboard` reading tracked Markdown registries and docs. |
| validation_command | `uvx python -m src.cli.main build-docs-dashboard --format json` plus `uvx pytest -q tests/test_docs_dashboard.py`. |
| latest_validation_result | 2026-06-16 v1.5 slice: dashboard regenerated; `project-status.json` parsed; Chrome headless screenshot inspected as readable/nonblank; `uvx pytest -q tests/test_docs_dashboard.py tests/test_subtitle_style_spike.py tests/test_subtitle_overlay_visual_proof.py tests/test_episode_review_bundle.py tests/test_episode_status.py` -> `21 passed, 8 skipped`. |
| review_status | Tracked dashboard entry is ready for operator navigation; not an episode media proof and not production/public acceptance. |
| next_action | Use this as the first docs navigation surface, then improve high-friction docs from the generated doc-health findings. |

## `clip-subtitle-font-candidate-sweep-001`

| Field | Value |
|---|---|
| title | ED-10h Subtitle Font Candidate Sweep v0 Registry |
| purpose | Define the next subtitle font candidate universe while preserving the current ED-10g selected diagnostic proof base. |
| storage class | Tracked docs/data artifact; no third-party font binaries vendored. |
| repo_relative_path | `docs/SUBTITLE_FONT_CANDIDATE_SWEEP.md` |
| metadata_json | `docs/font_candidates/subtitle-font-candidates.json` |
| open_command | `.\open-font-candidates.ps1` |
| generated_from | Manual v1.5 registry definition plus same-machine Windows font directory readback for local availability. |
| validation_command | `python -m json.tool docs/font_candidates/subtitle-font-candidates.json` plus dashboard/tests. |
| latest_validation_result | 2026-06-16 v1.5 slice: `python -m json.tool docs/font_candidates/subtitle-font-candidates.json` ok; targeted docs/subtitle/review tests -> `21 passed, 8 skipped`. |
| review_status | Candidate registry defined. Downloads and vendoring are not approved; local font availability is same-machine readback only. |
| next_action | Choose whether ED-10h should run no-download local/system comparison first or request permission for Google Fonts downloads with captured license metadata. |

Boundary flags remain false or pending:

- `production_subtitle_design_acceptance=false`
- `production_render_acceptance=false`
- `creative_acceptance=false`
- `rights_status=pending`
- `production_candidate=false`
- `production_usage_allowed=false`
- `publishing_acceptance=false`
- `public_use_permission=false`
