# ClipPipeGen

> **Current development state:** use
> [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) as the current-state source.
> OUT-02 is the tracked synthetic output-proof baseline; real local proof,
> production acceptance, rights approval, and public readiness remain separate
> states unless the Runtime capsule records a later reviewed transition.

SH-05 benchmark portfolio note: the current finite output benchmark surface is
15 families / 32 family-scoped candidate slots, materialized as 32 tracked
review cards. Open [docs/benchmarks/index.html](docs/benchmarks/index.html).
The current-host ledger reports 25 fully-viewable, 2 playable-proxy, 5
static-reviewable, and 0 contract-only slots. These tiers describe evidence
availability only; existing acceptance, rights, production, publication,
monetization, and upload gates remain exact-artifact decisions.

ED-13 Wiki content-reframe note: human content feedback is `revise`. Turns 1–5 are
preserved byte-for-byte as `SOURCE_SELECTION_AND_RENDER_PROBE`, with non-final product
authority and technical evidence only; MP4 count, decode, coverage, and overlap do not
represent integrated product progress or content acceptance. The tracked pre-render packet
[`wiki_tensaku_content_reframe_v1.html`](docs/content_planning/wiki_tensaku_content_reframe_v1/wiki_tensaku_content_reframe_v1.html)
reconstructs all three known streams as a four-Episode thematic family: 人物像 → 記憶 →
共有言語 → 関係性. Its canonical JSON contains 13 context-expanded ClipUnits with
setup/core/payoff, prior/following context, source timestamps, caption readback, chapter
contribution, and transitions. Twenty of the 60 probe cuts are candidates only inside those
expanded units; 40 are excluded from the current assembly. No new MP4 was created.
The fixed pre-render acceptance score is 74/100; S content review, integrated render,
final media QA, and explicit human content acceptance remain zero/open. Exact source bytes
for `youtube:82iRbxjvbww` and `youtube:Ocqg-RpQURY` remain unavailable and parked without
guessed retrieval, cookies, OAuth, or anonymous retry.

ED-13 Episode 1 production-entry note: S returned `content_continue`, raising the fixed
score to 82/100 without granting human artistic or final delivery acceptance. Mandatory
exact-media preflight resolved CU-01 and CU-03 to retained `youtube:1AcId5Yja10` bytes,
but CU-02 requires `youtube:Ocqg-RpQURY` 390–585s and only its exact automatic caption
bytes are present. The integrated renderer therefore did not run: MP4 count and integrated
product iterations remain 0. The portable blocker and resume map are in
[`preflight_report.md`](docs/content_planning/wiki_tensaku_ep1_integrated_rough_cut_v1/preflight_report.md).
Resume only after exact source bytes plus a receipt binding source identity, byte size, and
SHA-256 are explicitly supplied; this path performs no fetch, credential use, or Drive upload.

SH-10 private artifact transfer note: `build-private-artifact-transfer` creates an
ignored, immutable ZIP plus exact-hash receipt from explicitly listed `episodes/` inputs.
`verify-private-artifact-transfer` rejects unmanifested/path-unsafe members and restores
only missing files, reusing exact existing bytes and failing closed on conflicts. The Wiki
operator wrapper can emit the retained Wiki 001 full-corpus package or a new artifact-only
delta, so Turn 2 and later turns are recoverable without duplicating the already-delivered source package. Large transports are split into
independently hashed 16MiB parts and reassembled only after whole-archive SHA verification; see
[PRIVATE_ARTIFACT_TRANSFER.md](docs/PRIVATE_ARTIFACT_TRANSFER.md). Private transport is
not rights, production, public, monetized, publishing, or upload approval.

ED-12 / S1 note: `build-common-context-probe`は、取得済み実source二本だけをexact
media/caption/transcript/rights hashへbindし、source captionとcreator-authored commentaryを
別provenance trackとして一つのargumentative timelineへ運ぶ。current artifactは
`clip-s1-two-source-common-context-probe-v1-001`、6 cuts / 5 source switches /
98.896s、MP4 SHA`dc621bfe...f95be`。manifest/media validationとfull 689 testsはpassしている。
現在は`S1_S3_COMMON_CONTEXT_PROBE_READY_FOR_S4_HUMAN_REVIEW`で、二sourceが一つの論として
成立するかは人間未判断。rights、production、public/monetized use、uploadは閉じたまま。
詳細は
[S1_TWO_SOURCE_COMMON_CONTEXT_PROBE.md](docs/output_layer/S1_TWO_SOURCE_COMMON_CONTEXT_PROBE.md)。

OUT-13 note: `build-editorial-video-candidate` は、必須 `--artifact-id` ごとに成功済み
outputをローカルpipeline経路から上書きせず、取得済みの実 source、receipt / material ledger、明示 editorial plan、
transcript / source audio、provider JSON3 sidecar、rights snapshot、resolved font bytesを
fail-closedで結ぶ。source hostで生成された最新receiptは
`clip-out13-editorial-video-candidate-v1-005`で、7 cut / 5 sections / 8 omitted ranges /
128.833s（利用率78.2%）のH.264/AAC 1920x1080、MP4 SHA `a76babda...bbb5`、
provider cue 102件、authority / caption-boundary / media / editorial checks、browser review、
renderなしresumeを記録している。provider text/timingを使うが公式著者性は主張しない。
2026-07-25のcurrent root再照合では005のexact inputs / plan / 25-file package / MP4 /
launcherが存在し、全hash、package-tree digest、renderなしresume、page 200 / Range 206が一致した。
2026-07-25、ユーザーはexact SHA `a76babda...bbb5`を従来手順の内部全編
editorial / visual reviewとしてacceptした。受領scopeと重複review防止規則は
[out13_human_acceptance_receipt.json](docs/output_layer/out13_human_acceptance_receipt.json)に固定済み。
M2はclosed。accepted feature revision
`18641fe917b084259869263e8db05d78325aa2db`はmainへfast-forward統合され、
M4 complete / M5 integrated-baseline verification passedとなった。その後M6で
exact Candidate 005のpublic/monetized pathをdenyし、read-only archive evidenceとして閉じた。
ただし`episodes/`はignored same-machine evidenceで、Git同期だけでは別hostへ移らない。
rights、production subtitle/render、thumbnail、public/publishing/upload acceptanceは別gate。詳細は
[docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md](docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md)。

OUT-12 note: `build-real-video` で、取得済みの実 source 1本から解析、scene-boundary
Timeline IR、caption timing remap、H.264/AAC長尺render、full decode/faststart/audio・signal・
mapping検証、manifest、localhost review packageまでを一コマンドで生成できる。実runは
`youtube:gUwJBRUIWow` の source全長を11 cut / 260.694s / 1920x1080へ変換し、MP4 SHA
`5d391ffd...a584`、validation passed、resume時render非実行・同一SHAを確認した。
これはinternal automation acceptanceであり、rights、production subtitle/design、thumbnail、
winner、public/publishing/upload acceptanceではない。詳細は
[docs/output_layer/OUT_12_ONE_COMMAND_REAL_VIDEO_AUTOMATION.md](docs/output_layer/OUT_12_ONE_COMMAND_REAL_VIDEO_AUTOMATION.md)。

OUT-11 note: 人間レビューでSOURCE-04 `465d732c...16524`は問題なしと確定し、MP4を一切
変更せずaccepted receiptへ移した。OUT-10は新しい診察場面を途中で切っていた
`a53d0416...134f2`から、意識確認・患者反応・「ゴッドハンドやね」が閉じるsource `34.785s`、
SHA `62d4b45b...97cdd`へendpointだけを修復した。SOURCE-05は旧`370850c5...b578`の
画面切替直後終了と未確認の歌唱・歌詞説明を退け、同一recordingの`202.586–260.643s`を
source EOFまで収めたSHA `b4a01413...a4969`へ修復した。添付契約の最終人間判断を両exact SHAへ
bindし、5-sourceは`accepted_internal`、winnerなしとして閉じた。OUT-10の軽いsource-specific
endpoint debtとSOURCE-05の歌唱・歌詞・話者未確認は保持するが、追加Short repair/reviewは再開しない。
winner、共通crop/字幕/speaker-color policy、rights、production、thumbnail、public/publishingは
未承認。詳細は
[docs/output_layer/OUT_11_FIVE_SOURCE_SHORT_PORTFOLIO_WAVE.md](docs/output_layer/OUT_11_FIVE_SOURCE_SHORT_PORTFOLIO_WAVE.md)。

OUT-10 note: 30.014s predecessorは導入を維持したが、その直後に始まる意識確認場面を閉じず、
人間レビューで未受理となった。終端だけをsource `34.785s`へ延長し、50 cue、media 34.800s、
exact MP4 `62d4b45b...97cdd`としてOUT-11の修復二本reviewの先頭へ固定した。34.800sから始まる
別キャラクター紹介は含めていない。
詳細は
[docs/output_layer/OUT_10_THIRD_SOURCE_PORTFOLIO_EXPANSION.md](docs/output_layer/OUT_10_THIRD_SOURCE_PORTFOLIO_EXPANSION.md)。

OUT-09 note: OUT-08と異なる実source `D4i4fjs9PWc` / episodeから生成した候補へ、
人間の実見で判明した「中央16:9内のnative captionが小さい」「full-source blurが字幕字形を
下部canvasへ複製する」「下部が霜ガラス状で読めない」という表示欠陥を1回の補正renderで
修復した。source `31.160–64.480s`と33.320秒の意味範囲は変更せず、source下部74pxを
背景・前景の双方からcropし、JSON3 event/token timingに基づく1–6語・1–2行の短い27 cueを
不透明な黒plate上へburn-inした。caption-free cropだけをbackgroundに使い、full-source blur
fallbackとfrosted subtitle surfaceを禁止している。MP4は
`b6b90a4b...73da50`、media/frame/mobile/browser QAはpassed、human reviewはaccepted internal。
旧MP4 `300ee360...e0c9`と失敗repair `3e7ef9d8...2916`はlineageとしてのみ保持する。
rights、production、thumbnail、public/publishing gateは閉じたまま。詳細は
[docs/output_layer/OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md](docs/output_layer/OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md)。

OUT-08 note: authoritative episode evidence の未使用範囲から、重複しない 2 本の
実尺 vertical Shorts 候補を 1 回の atomic render で生成し、単一列の localhost
review page に束ねた。candidate 02 は reject 済み `cut_009` の source-time
interval を完全除外した。これは同一マシン内の internal review artifact であり、
navigation frame は thumbnail ではない。修復後exact二本へのユーザー回答
「両方問題ありません」をcandidate identityへ結び、batch `accepted_all_internal`、
candidate 01 / 02 `accepted_internal`、winner noneとしてOUT-08を閉じた。package欠落や
server停止は受入を失効させない。rights、production、thumbnail、publishing/publicの
gateは未承認のまま。OUT-09はこのclosed baselineを変更せず、別artifactとして
second-source repeatabilityを検証する。

OUT-07 note: Thank の単一 native Shorts cover direction proxy は、人間レビュー
で自然かつこの episode には暫定利用可能と確認されたが、比較が一種類だけの
ため選定・再現性・canonical 化・default template 化は行わない。
`PARK_PROVISIONAL_USABLE` として追加 thumbnail iteration を禁止して閉じ、
ignored proxy package は historical local evidence として保持する。thumbnail
exploration の再開は実 Shorts が 3〜5 本揃った後だけで、reference corpus は
具体例群であり canonical design rules ではない。Planner007 の exact baseline
(`2c1c59bc...2d18`) は historical accepted fact のまま。metadata、upload、
public readiness、rights、production、visibility、made-for-kids、publishing は
閉鎖または pending のままである。See
[docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md).

OUT-06 note: the accepted OUT-05 vertical opening has now been extended with the
authoritative kept `cut_003` through `build-complete-narrative-short`, producing
one ignored same-machine three-cut/29-subtitle internal delivery candidate with
manifest, media/audio/boundary readback, poster, frame QA, and a video-first
review page. The 2026-07-12 review accepted tempo and audio/video continuity,
then accepted the bounded subtitle-wrap and seekability repair as
`accepted_after_bounded_repair` for the same artifact ID. Rights remain pending
and production subtitle/render, public, and publishing acceptance remain
separate gates; see
[docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) for the live artifact and review
state.

ED-10 note: official subtitle track import / transcript alignment is now implemented. Use `import-subtitle-track --base-transcript <path> --subtitle-track <path> --output <path> [--source-format youtube-json3] [--reviewed-by <id>] [--dry-run] [--force] [--format json]` to convert a YouTube JSON3 subtitle track into a `transcript.json`-compatible artifact with `stt.engine="subtitle_track"`. It preserves source-audio readback and alignment notes, and downstream `generate-subtitles` marks drafts as `source_type="imported_subtitle_track"`. This is still diagnostic data, not subtitle design, render, rights, creative, or publishing acceptance.

ED-10a note: `build-cut-review-packet` now turns selected cuts into review packets and evidence summaries. It writes `cut_review_packet.json`, `cut_review_report.html`, `evidence_summary.json`, and `evidence_summary.html` from existing transcript/edit/NLE/render/rights artifacts. The packet keeps decisions as `undecided`, records rights pending as non-production, and exists to hand off final cut/context review.

ED-09 note: transcript review / correction workflow is now implemented. Use `review-transcript --transcript <path> --patch <path> [--reviewed-by <id>] [--dry-run] [--format json]` to apply v1 correction patches to `transcript.json`; it updates only segment text, review status, notes, and top-level review fields. `status-episode` now shows transcript review counts, and `export-nle` reports transcript review state instead of assuming every real STT transcript is unreviewed. Transcript approval is still not edit/render/publish acceptance.

JP-Pilot-01 / 01R / 01R2 / 01R3 note: ED-07c 後の日本語 public VOD diagnostic として、assistant 自律選定 URL <https://www.youtube.com/watch?v=7J5aS_pcBj4>（公式 hololive short anime `【アニメ】押忍！！ば～んちょ だじぇ！`）で URL → source_video / source_audio → Vosk JP transcript → edit_pack → subtitles → diagnostic burn-in render → NLE CSV → ledger audit まで完走。ED-09 後の JP-Pilot-01R2 では公式 Japanese subtitle track の max-overlap alignment で既存 26 transcript segments を accepted 25 / rejected 1 / unreviewed 0 まで補正し、短め selected cuts 5 本、context 5 passed / 0 needs_review、21 subtitle drafts、NLE CSV 5 rows、23.13s diagnostic render を再生成した。ED-10 後の JP-Pilot-01R3 では公式 subtitle track 自体を import し、105 segments、9 selected cuts、context 3 passed / 6 needs_review、105 imported subtitle drafts、NLE CSV 9 rows、6.84s diagnostic render を再生成した。詳細は [docs/JP_PILOT.md](docs/JP_PILOT.md)。

JP-STT-01 / HoloEN-01 note: Vosk JP model (`vosk-model-small-ja-0.22`) で日本語音声を transcript.json にする plumbing proof（adapter 変更 0 行、language-agnostic）と、HoloEN public VOD（assistant 自律選定: Ouro Kronii Kroniicle Animation）で URL → rendered_video.mp4 + NLE CSV まで full pipeline を通した quality scorecard 記入済。runbook は [docs/JP_STT_SMOKE.md](docs/JP_STT_SMOKE.md) / [docs/HOLOEN_PILOT.md](docs/HOLOEN_PILOT.md)。assistant は HoloEN public VOD 候補を自律選定する権限を持ち、除外条件（members-only / paid / concert / song / 第三者IPリスク高）は COVER 公式 derivative works guidelines 由来の compliance として維持。`production_candidate=false` / creative acceptance / publishing acceptance ではない。

Phase 0.5 note: `HoloEN-01 publish-quality diagnostic pilot` は `done`（assistant 自律選定 URL <https://www.youtube.com/watch?v=D4i4fjs9PWc> で actual smoke 完了）。Phase 0 で plumbing が通った縦糸（URL → source_video / source_audio → Vosk EN transcript → edit_pack → diagnostic burn-in render → NLE CSV）を HoloEN 公開済み VOD で 1 本通し、英語発話コンテンツで「動画コンテンツとして成立しそうか」を技術 / 制作 / 権利の 3 軸で早期診断。詳細は [docs/HOLOEN_PILOT.md](docs/HOLOEN_PILOT.md)。

OUT-01e note: real STT `transcript.json` segments can now generate `edit_pack.subtitles[]` drafts with `source_type=real_transcript`, then flow into `render-tiny-proof --burn-in-subtitles diagnostic` with subtitle source / segment id / timing readback. This remains diagnostic proof, not STT quality, production subtitle design, creative acceptance, or GUI render action.

ED-07c note: `transcribe-audio --engine vosk` now validates inferable model language against `--language`. For example, `vosk-model-small-en-us-0.15` with `--language ja` fails before writing `transcript.json`; unknown model names stay warning-only. This protects JP/EN pilot comparisons from misleading transcript metadata.

ホロライブ等の VTuber 切り抜き動画制作を、権利・素材・編集・サムネ・投稿の4レーンで半自動化する制作補助ツール。

## このリポジトリの位置付け

- 元動画 → 素材取得 → rights 記録 → カット候補 → 字幕案 → サムネ slot patch → upload までを接着する Python ツール群。
- 動画レンダリング・字幕焼き込み・音声合成・公開操作は、実装された integration / 外部ツール / GUI 導線で段階的に扱う。
- [NLMYTGen](https://github.com/YuShimoji/NLMYTGen) とは別リポ。共有は CLI / schema / module 単位のみ。GUI は共有しない。

## 4レーン

| レーン | 責務 | 主成果物 |
|---|---|---|
| Compliance / Rights | 権利・出典・状態の記録 | `rights_manifest.json` |
| Material Sourcing | 素材取得・背景切り抜き受領・素材台帳（横断レイヤー） | `material_ledger.json` / 透過PNG＋sidecar |
| Editing | カット候補・字幕案・YMM4/NLE 配置データ | `edit_pack.json` |
| Thumbnail | YMM4 サムネテンプレ slot patch | patched `.ymmp` |
| Publishing | metadata draft・upload | `publish_draft.json` |

詳細: [docs/LANES.md](docs/LANES.md)

## North Star

- rights / material / edit / thumbnail / publishing の情報を episode 単位でつなぎ、制作作業を止めない。
- 外部素材取得・背景切り抜き・upload は通常の integration 候補として扱う。未実装なら「未実装」と表示し、禁止扱いにしない。
- 権利・出典・利用条件は readback と判断材料として残す。`pending` / `unverified` / `unknown` などの値だけで local CLI を止めない。
- YMM4 / 外部 NLE / YouTube など外部ツールとの境界は integration として明示し、必要になった順に実装する。

詳細: [docs/INVARIANTS.md](docs/INVARIANTS.md) / [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)

## 現在のスライス

現在のactive sliceは`SH-05` benchmark portfolio readback。15 family / 32 family-scoped slotを
tracked review surfaceへ有限化し、25 fully-viewable / 2 playable-proxy / 5 static-reviewable /
0 contract-onlyを観測している。ED-13 Wiki 003はretained evidenceだけからnetwork request 0の
candidate-specific 12章static packetへ昇格済み。さらに既存Wiki 001 source bytesをSHA再照合して、
Turn 1からTurn 5まで、既使用rangeを順次除外する300秒artifactを生成し、unique source-timeを
1,775秒まで拡張した。Turn 5はcorrection 8章 / fallback 4章のcorrection-prioritized mixedで、
fallback第1・6・11・12章を章別scarcity evidenceとともにSupervisorへ渡す。
Wiki 002/003のexact source bytesは未供給のままで、そのmedia gateは変更していない。
ED-12/S1 exact probeのhuman reviewは別laneにparkしている。

実装履歴として、**Slice 1 ソフト実装は done**（CR-01 / MS-01 / MS-02 /
MS-03 / TH-01 / SH-01）。Slice 2 / Phase 1.5では、source audio / source video取得、
real STT transcript、cut / context / subtitle draft、NLE CSV export、diagnostic render、
real transcript subtitle burn-in、JP-STT-01 / HoloEN-01 / JP-Pilot-01の実素材pilot、
ED-09 transcript review / correction workflow、ED-10 official subtitle track import、
JP-Pilot-01R corrected rerun、JP-Pilot-01R2 review coverage + cut narrowing、
JP-Pilot-01R3 official-caption rerunまで実装済み。中核パイプラインは
`source media -> material_ledger / receipt -> transcript.json -> edit_pack.json ->
subtitles -> diagnostic render -> NLE CSV`まで通る。`review-transcript`は補正済み
transcriptを既存downstreamへ戻す入口であり、transcript approvalは
edit / render / publish / production acceptanceではない。

直近のproduct actionは、新しいWiki family turnのexact MP4 SHAへ
`accept / bounded repair / reject`をbindする内部editorial review。Wiki 002または003のmedia
upgradeはexact source bytesが明示的に供給された場合だけ進む。S1は別exact MP4への
`accept / bounded repair / reject`をidentityへbindするhuman verdict待ち。rights approval、
production render/subtitle design/image quality、thumbnail、Publishing / OAuth、upload、
public releaseは開始しておらず、独立した未承認gateのままである。

詳細: [docs/FIRST_SLICE.md](docs/FIRST_SLICE.md) / [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md)

## 1 episode 通し手順

[docs/walkthrough/SLICE1_WALKTHROUGH.md](docs/walkthrough/SLICE1_WALKTHROUGH.md) — `init-episode` から `patch-thumbnail` までの 11 ステップ runbook。
[docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md](docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md) — YMM4 上で `thumb.*` Remark 付き base template を authoring する手順。

ローカル素材から制作判断面までの最小確認:

```powershell
uvx python -m src.cli.main build-local-preview-pack `
  --episode-id local_preview_001 `
  --local-media path\to\input.mp4 `
  --material-id src_audio_local_001
```

詳細: [docs/PREVIEW_PACK.md](docs/PREVIEW_PACK.md)

## 入口

- 運用ルール正本: [docs/INVARIANTS.md](docs/INVARIANTS.md) / [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)
- asset_fetch 境界: [docs/ASSET_FETCH_BOUNDARY.md](docs/ASSET_FETCH_BOUNDARY.md)
- local preview pack: [docs/PREVIEW_PACK.md](docs/PREVIEW_PACK.md)
- 引き継ぎ: [docs/HANDOFF.md](docs/HANDOFF.md)
- 機能一覧（全件把握）: [docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md)
- 現在位置: [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md)
- GUI MVP: [docs/GUI_MVP_SCOPE.md](docs/GUI_MVP_SCOPE.md)
- AI エージェント入口: [AGENTS.md](AGENTS.md)
