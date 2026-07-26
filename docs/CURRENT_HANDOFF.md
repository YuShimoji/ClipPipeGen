---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT14_EDITORIAL_V3_READY_FOR_HUMAN_REVIEW
last_touched: 2026-07-27
current_slice: OUT-14
phase: exact_v3_artifact_human_editorial_review_pending
canonical_status: out14_editorial_v3_ready_for_human_review
active_branch: codex/out14-editorial-presentation-v3
exact_branch_base: fab5d5a3369fe4d5defab265fa715201c3f8b0cf
active_artifact: clip-out14-push-microarc-editorial-v3-001
human_entrypoint: episodes/out14_push_microarc_editorial_v3_20260727/artifacts/clip-out14-push-microarc-editorial-v3-001/review/index.html
portable_entrypoint: docs/SUPERVISOR_STATUS_REPORT.md
local_artifact_available: true
local_artifact_role: exact_v3_internal_human_review_target
portable_local_artifact_available: false
cross_machine_resume_class: tracked_v3_code_and_docs_are_portable_ignored_source_v2_reference_and_package_are_not
review_status: ready_for_human_review
acceptance_media_sha256: fddae5a6688671ad301b1c1dcecd978a50865dd1fb5d678a6d55db1f3c18e9be
human_review_pending: true
editorial_acceptance_granted: false
acceptance_receipt: null
rights_approval: not_granted
production_acceptance: false
public_or_publishing_acceptance: false
accepted_feature_revision: null
integrated_main_revision: null
main_integration_approved: false
m4_main_integration_status: not_applicable_out14
m5_integrated_baseline_verification_status: not_applicable_out14
m6_rights_status: closed_deny_exact_artifact
m6_packet_status: M6_CLOSED_DENY_EXACT_ARTIFACT
m6_packet: docs/rights/out13_m6_rights_decision_readiness_packet.json
m6_owner_verdict: deny
public_use_verdict: not_evaluated_for_out14
monetized_youtube_verdict: not_evaluated_for_out14
out14_v3_rights_status: not_evaluated
historical_out13_artifact: clip-out13-editorial-video-candidate-v1-005
final_main_revision_locator: refs/heads/codex/out14-editorial-presentation-v3
m6_decision_binding_revision: 097fcaad8985d4f24077da484819efb5942b9c65
upstream_parity: not_configured_local_only
remote_decision_binding_available: false
local_decision_binding_committed: true
remote_mutation_authorized: false
source_of_truth: true
owner_lane: human_overall_editorial_quality_review
decision_required: exact_v3_overall_editorial_quality_and_remaining_major_issue_verdict
next_review_due: now
next_action: open_exact_v3_review_and_record_accept_bounded_repair_or_reject_for_this_sha_only
---

# Current Handoff - ClipPipeGen

## 監修役が最初に開くもの

対象は
`episodes/out14_push_microarc_editorial_v3_20260727/artifacts/clip-out14-push-microarc-editorial-v3-001/review/index.html`。
レビューserverを再起動する場合は、このworktreeで次を実行する。

```powershell
uv run python -m src.cli.serve_review `
  --root episodes/out14_push_microarc_editorial_v3_20260727/artifacts/clip-out14-push-microarc-editorial-v3-001 `
  --port 8082
```

URLは`http://127.0.0.1:8082/review/index.html`。
final MP4 SHAは
`fddae5a6688671ad301b1c1dcecd978a50865dd1fb5d678a6d55db1f3c18e9be`、
manifest file SHAは
`99bb99349b7896a4667358fd14f9c08557d356971823f07a254f2fd35bbace72`、
manifest self-integrityは
`5f1ee7c2da681dbb4bd73c88ac58f1b85b42cfe2776e788add6fe0bca2ec70d7`。

review pageはworking title、selected 320×180 / 160×90、runner-up、
full video、changed-locus probesの順。監修役へ全cue・全cutの採点表入力は要求しない。
全体的な編集品質と残存する重大問題だけを判断対象にする。

## v2 human decisionから何を変えたか

v2 final SHA
`8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414`
はtechnical evidenceとして保存した。v2 verdictがacceptedにしたのはsubtitleの
perceptual timing improvementだけであり、production、thumbnail、未指摘箇所を
accepted扱いしていない。

| v2でBLOCKされた原因 | v3の処理 | 読戻し |
|---|---|---|
| raw source screenshot＋single hook thumbnail | notification revealを主素材にsetup＋consequenceを二階層化 | 1280 / 320 / 160、badge overlap 0 |
| mechanical cue split | full 142 cueを監査しphrase-internal boundary 42件を99 cueへ統合 | 語中・孤立・助詞等・禁則・3行・過密すべて0 |
| quoteを通常speechと同型表示 | narrating Subaru / verified quote / paraphrase / explanationを分離 | verified quote 5件、distinct coverage 100% |
| laughterを空白化 | actual-audio eventをmild 2 / strong 3へ分類 | unhandled 0、strong 3件だけbounded motion |
| 2:48 / 6:27のnaked cut | 8 boundaryを原因分類しmaterial bridgeを追加 | unmarked material cut 0 |
| 6:27後の黒地白文字 | source footageを錨にcompact explanation panelへ統合 | full-black signature消失 |

ACTIVE quarantineは次の3件で、v2 exact identityへ束縛したまま。

1. `out14-v2-source-screenshot-single-hook-thumbnail-v1`
2. `out14-v2-flat-caption-pass-through-v1`
3. `out14-v2-naked-cut-black-card-v1`

v1/v2 artifact、source、manifest、review package、decision recordは上書きしていない。
v2は30 files、final / manifest / rejected thumbnail / sourceのexact SHAを再照合した。

## 生成前design basis

最初のdirection-generating mutationとして
`docs/research/OUT14_EDITORIAL_V3_DESIGN_BASIS.md`を作成し、
`CPG-OUT14-V3-DIRSIG-20260727-A`を固定した。

fresh temporary Incognito、signed-out、extensions/sync/cache disabledで、
4チャンネル・9本を320×180 thumbnailとactual decoded timestampで観測した。
同一題材、複数人物／引用、笑い、section transitionを含む。
Default profile、cookie、Google/YouTube login、Home、おすすめ、競合asset保存、
download、like、comment、subscribeは使用していない。

採用したのは、役割を同型にしない、material jumpを知覚可能にする、
thumbnailをsetup＋consequenceにする、という構造だけ。
公開例のcopy、色、portrait、layout、motion、speech balloonは複製していない。

## 実装とbounded repair

新しいrendererはexact v2/source/design signatureをpreflightし、
role-aware ASS、quote/laughter ledger、8-boundary transition map、
thumbnail compositor、review packageを一回のstaging buildへ接続する。
build直後は`FULL_VIEW_SELF_REVIEW_PENDING`でfail-closedにし、
viewer-facing full playback完走後だけREADYへ昇格する。

probe r1で6:27 explanationのliteral escapeと弱い2:48 bridgeを発見し、r2で修復した。
初回full playback後の全ledger監査で、既知の`なん／か`以外にも
`レッドカ／ード`、`メンバ／ー`、`す／いません`等の同型境界が残ることを検出した。
この時点でREADY claimを固定せず、31 phrase group、42 internal boundary、
1 incomplete fragment suppressionへ原因層を修正し、r3/r4 probe、
full rerender、full decode、2回目の406.55秒full playbackまで実施した。

0:15 locusはv2 boundary 12.64秒からcanonical word end 12.72秒へ移動。
changed timing median / p95は80ms、systematic late biasなし。
これはdeterministic mapping errorであり、人間のperceptual accuracyを自動証明しない。

## exact artifact

| 項目 | 確定値 |
|---|---|
| artifact | `clip-out14-push-microarc-editorial-v3-001` |
| video | H.264 Main / AAC、1920×1080、60fps、406.55秒 |
| bytes / SHA | 404,376,920 / `fddae5a6…e9be` |
| caption | canonical 142 → viewer-facing 99、merged boundary 42 |
| quote | 5 verified、coverage 1.0、portrait 0 |
| laughter | 5 events、mild 2 / strong 3、provider leak 0 |
| transitions | 8 classified、material bridge 2、unmarked 0 |
| thumbnail | selected 1280 / 320 / 160、runner-up 320、external/generated 0 |
| package | 47 payload＋manifest、closed-set pass |
| full playback | 406.55秒、8 checkpoints、ended true、speed 1、volume 1、mute false |

full decode、faststart、A/V start 0、video/audio duration差5ms、-14.9 LUFS、
true peak -1.7 dBFS、silence 0、全cut black 0、9 probe decodeを確認した。
repository-required Pillowを注入したfull suiteは706 passed。
6:23.967–6:24.467の0.5秒freezeはsource内holdで、6:26.44のcut boundary前。
修復前後AAC stream SHAは一致し、audio join最大sample jump 0.07254
（threshold 0.08）の検査結果をexact audioへ継承できる。

## 人間が閉じる判断

監修役はexact v3を全編確認し、次のどれか一つをこのSHAへ束縛する。

- `accept`: internal editorial / language / title / thumbnail scopeだけを受理する。
- `bounded_repair`: 重大問題のdimensionとtimestampを限定して修復する。
- `reject`: v3を内部candidateとして閉じる。

どの結果でもrights、YPP、production、upload、publication、visibilityは開かない。
rights以降へ進むには、exact accepted media、利用範囲、platform、territoryを束縛した
別owner receiptが必要。push / PR / mergeも今回のauthority外で未実施。

詳細な監修報告と条件付き長期目標は`docs/SUPERVISOR_STATUS_REPORT.md`。
