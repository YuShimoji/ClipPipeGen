# Automation Boundary

## 2026-05-26 clarification: diagnostic processing vs production gates

Local diagnostic processing is allowed while `rights_manifest.compliance_check.status` is `pending`: source fetch, provenance-bound `build-edit-ready-source-packet`, transcript generation/import/review, cut generation, context checks, subtitle drafts, NLE CSV export, `render-tiny-proof`, bounded `build-editorial-sequence`, accepted-timeline `build-vertical-short-candidate`, bounded `build-complete-narrative-short`, bounded `build-real-unused-range-short-minibatch`, hash-bound endpoint preflight/evidence, bounded `build-source-adaptive-short-candidate`, combined evidence-only portfolio review, one-command internal long-form `build-real-video`, cut review packets, and evidence summaries. These operations must preserve rights status as readback and must not claim production, creative, publishing, or public-use approval.

Production/public operations are hard-gated beyond this boundary: upload, OAuth-backed publishing, visibility changes, public thumbnail setting, production render acceptance, production subtitle burn-in/design acceptance, and any public-ready claim require an explicit rights / publishing acceptance slice. Pending rights cannot be described as production-usable.

`src/integrations/render/` is the only place where Python may call FFmpeg for rendered video output, and only for diagnostic artifacts with `production_candidate=false` plus receipt / manifest / report. Editing core may prepare transcript, cuts, subtitles, review packets, and NLE handoff data, but it must not become the production renderer.

何を自動化し、何を外部 integration / 外部ツールとして扱うかの境界。禁止リストではなく、実装面の分離を定義する。

## Integration マップ

| 種別 | 操作 | 場所 | 現在の扱い |
|---|---|---|---|
| Local | manifest／schema validate | `src/pipeline/*` | 実装済み |
| Local | local preview pack（artifact preview / read-only report） | `src/cli/build_local_preview_pack.py` / `src/pipeline/preview_pack.py` | SH-05 実装済み。local media 1本から source audio / transcript / cut / context / subtitle / manifest / HTML report を接続。SH-05d で既存 source_audio material の `source.wav` / receipt / sidecar / ledger も再取得なしで review surface に接続。動画生成ではない |
| Local | human preview session bundle（diagnostic / representative review entry） | `src/cli/build_episode_review_bundle.py` / `src/pipeline/episode_review_bundle.py` | SH-08 実装済み。既存 episode / review artifacts を `human_preview_session/index.html`、`review_manifest.json`、`decision_request.json`、`decision_template.json`、`open_preview.ps1`、`serve_preview.ps1`、`assets/` に束ね、playable MP4 または contact sheet を HTML report より先に提示する。active session は人間判断が消費されるまで local retained artifact として cleanup 保護する。render / fetch / upload / rights approval / production acceptance は行わない |
| Local | NLE export（CSV cut list / readback report） | `src/cli/export_nle.py` / `src/pipeline/nle_export.py` | ED-06 実装済み。`edit_pack.json` から `nle_cut_list.csv` / `nle_export_manifest.json` / `nle_export_report.html` を生成する。ED-07b 以降は `transcript.json` の provider / model / real_transcript も readback する。FCPXML / Resolve XML / render / encode ではなく、production candidate 判定はしない |
| Local/External tool | diagnostic render proofs / editorial and vertical candidates / operator delivery pack | `src/cli/render_tiny_proof.py` / `src/cli/build_editorial_sequence.py` / `src/cli/build_vertical_short_candidate.py` / `src/cli/build_complete_narrative_short.py` / `src/cli/build_real_unused_range_short_minibatch.py` / `src/cli/build_second_source_short_repeatability.py` / `src/cli/build_third_source_short_portfolio.py` / `src/cli/build_operator_delivery_pack.py` / `src/cli/reconstitute_out07_review.py` / `src/cli/build_out07_direction_proxy.py` / `src/cli/serve_review.py` / `src/integrations/render/` | OUT-01 は tiny diagnostic proof、OUT-04 は explicit ordered 2-3 cut representative sequence、OUT-05/06 は accepted timeline の internal candidate。OUT-07はaccepted baselineからoperator packを作り、OUT-08は未使用範囲のatomic minibatch、OUT-09は第二source、OUT-10は第三distinct sourceの候補と3-source scorecardを作る。OUT-10は取得済みmedia・official caption・declarative planを厳密照合するだけで、builder内部ではURL取得しない。source probeにより全景保持が必要な場合だけneutral matte canvasを選択でき、そのpolicyではsource-derived blur、crop、native caption suppressionを禁止する。navigation frameは導線専用でthumbnailではなく、review pageの人間判断をacceptanceに代用しない。`serve_review` は固定rootの127.0.0.1 byte-range localhost review serverであり、GUI action / production render / publishing / upload / thumbnail upload / visibility / made-for-kids / production subtitle design acceptance は行わない |
| Local/External tool | OUT-11 endpoint evidence / source-adaptive candidate / five-source review | `src/cli/build_endpoint_preflight.py` / `src/cli/build_endpoint_evidence_manifest.py` / `src/cli/bind_source_adaptive_candidate_plan.py` / `src/cli/build_source_adaptive_short_candidate.py` / `src/cli/build_five_source_short_portfolio.py` / `src/integrations/render/source_adaptive_short_candidate.py` / `src/integrations/render/five_source_short_portfolio.py` | 取得済みsource、caption、endpoint selection、plan、candidate packageをhashとsizeで照合する。sourceごとに観測したneutral matte / official overlay / source-native text保持を選べるが、歌唱・歌詞・speaker意味を知覚証拠なしに主張せず、共通production policyにも一般化しない。combined reviewはOUT-08/09と人間合格済みSOURCE-04をaccepted contextに固定し、修復対象OUT-10/SOURCE-05の二本だけをexact byte copyする。SOURCE-04はreadback/manifest受領証だけで、MP4を再copy・再視聴しない。URL取得、winner選択、human acceptance、rights、production、thumbnail、public/publishingは行わない |
| Local/External tool | OUT-12 one-command real long-form automation | `src/cli/build_real_video.py` / `src/integrations/render/real_video_pipeline.py` / `src/cli/serve_review.py` | 取得済み実sourceまたはepisode material identityから、provenance、content analysis、chronological Timeline IR、caption timing remap、H.264/AAC render、full validation、manifest、localhost reviewまでをatomic packageにする。`--resume`はfingerprint/manifest/hash一致時だけ高コストstageをskipする。source-native textの意味、rights、human content acceptance、production subtitle/design/render acceptance、thumbnail、winner、public/publishing/uploadは推定・実行しない |
| Local GUI | preview pack read-only ingest | `gui/preview_reader.cjs` / GUI Preview Pack tab | SH-05c 実装済み。既存 `preview_manifest.json` / `preview_report.html` を読み、validation / warning / artifact link を表示するだけ。build / fetch / render / upload は実行しない |
| Local/Bridge | サムネ slot patch 適用（書き出し） | `src/cli/patch_thumbnail.py`（NLMYTGen CLI bridge 経由） | 実装済み。出力先は input で指定 |
| Local/External tool | speech-to-text（ローカル音声 → transcript） | `src/cli/transcribe_audio.py` / `src/integrations/stt/` | ED-07 adapter surface 実装済み（fake engine）。ED-07b で optional `vosk` adapter を追加し、明示 model path の local STT で `real_transcript=true` を生成可能。provider / model 不在は preflight failure で、fixture fallback はしない。URL / VOD 取得は含めない |
| External integration | source audio / video 取得 | `src/integrations/asset_fetch/` | INT-02a: `fetch-source-audio --mode fake` で source audio 契約は実装済み。INT-02b: yt-dlp / FFmpeg 境界仕様は固定済み。INT-02c: `local-media-audio` でローカル media の FFmpeg 正規化を実装済み。INT-02d: `yt-dlp-audio` spec only は完了。INT-02e: `yt-dlp-audio` source audio URL fetch は actual smoke まで完了。INT-02f: `fetch-source-video --mode local-media-video` で local source video 登録と FFprobe metadata readback を実装済み。INT-02g/INT-02h: `yt-dlp-video` source video URL fetch は boundary spec + actual smoke まで完了 |
| External integration | 背景切り抜き API 呼び出し | `src/integrations/bg_removal/` | 通常の future integration |
| External integration | YouTube への upload / thumbnail 設定 / visibility 更新 | `src/integrations/youtube/` | 通常の future integration |

## やる（v1 スコープ内）

- 元動画 URL に対する `rights_manifest` 構造化（整形と validate）
- 素材の台帳化（`material_ledger`）と sidecar 強制
- 透過PNG（人物画像）の受け入れと slot 配置
- YMM4 サムネテンプレへの `thumb.image.*` / `thumb.text.*` slot patch（NLMYTGen CLI bridge 経由）
- rights / sidecar status の readback（値は記録し、local CLI の hard gate にはしない）
- 後続スライスで段階的に追加（FEATURE_REGISTRY 参照）：
  - 元動画ダウンロード integration
  - source audio contract（`fetch-source-audio --mode fake`、`--mode local-media-audio`、`--mode yt-dlp-audio` は実装済み。`yt-dlp-audio` は source audio URL fetch のみに限定し、標準形は PCM WAV / mono / 16kHz / 16-bit）
  - ローカル音声ファイルからの transcript 生成（`transcribe-audio --engine fake` と optional `--engine vosk --model <path>` は実装済み。Vosk は local provider / model を明示し、fallback しない）
  - transcript からの字幕案生成（`generate-subtitles` は実装済み。OUT-01c で diagnostic overlay 接続まで実装済み。production subtitle design は後続）
  - transcript からのカット候補抽出（`generate-cuts` は実装済み）
  - transcript 隣接 segment による cut 文脈チェック（`check-cut-context` は実装済み。動画 preview / creative acceptance は後続）
  - ローカル素材 1 本、または取得済み source audio material から operator-visible な artifact preview / read-only HTML report を生成（`build-local-preview-pack` は実装済み。rendered video preview ではない）
  - `edit_pack.json` から外部編集へ渡す CSV cut list / manifest / HTML readback を生成（`export-nle` は実装済み。production edit acceptance ではない）
  - source video / source audio / edit_pack -> tiny diagnostic rendered video / receipt / manifest / report (`render-tiny-proof` is implemented; OUT-01a preflight/fallback/failure readback, OUT-01b longer local smoke, OUT-01c diagnostic subtitle overlay, and OUT-01d subtitle timing/filter diagnostic readback exist; production render acceptance is not claimed)
  - upload / thumbnail 設定 / visibility 更新 integration

## 現時点で未実装

- production render acceptance / production subtitle burn-in-design / public-ready render surface（OUT-12でinternal long-form cut/concat/render/review automationは実装済みだが、production・rights・public acceptanceへは昇格していない）
- FCPXML / Resolve XML など NLE 固有 XML export
- 音声合成 / TTS
- YouTube upload / thumbnail 設定 / visibility 更新
- STT 品質評価、話者分離、外部 API STT、`whisper.cpp` 等の追加 provider
- 背景切り抜き API 呼び出し
- 完全自動サムネ合成 / サムネ画像レンダリング

これらは未実装であり、必要になった時点で FEATURE_REGISTRY に起票し、integration / CLI / GUI として実装する。

## Integration 実行 contract

外部 tool / service を呼ぶ操作、または episode 配下の素材を増やす操作は、実装時に次を surface に出す。これは未実装機能を禁止するためではなく、operator が実行内容を readback できる形にするための contract。

1. **preflight**: URL / 入力ファイル / 出力先 / 推定サイズ / 目的 / 使用 engine または provider を表示する。
2. **confirmation**: GUI 実行時は既存の confirm dialog と同じく command / summary / reason を表示する。CLI 実行時は同等の dry-run または promptless preflight JSON を用意する。
3. **log / receipt**: 実行 command、provider、開始終了時刻、生成 file、hash、warnings を保存する。
4. **rollback 情報**: 生成 file、ledger 追加、receipt の対応関係を残し、operator が削除・再実行できる状態にする。
5. **台帳登録**: INT-02 が音声・動画・画像素材を取得した場合、`material_ledger` へ自動登録できる導線を持つ。

## Review / Readback の所在

これらは operator が見るべき状態だが、値だけで local CLI を止めない：

1. `rights_manifest.compliance_check.status`
2. `rights_manifest.compliance_check.warnings[]`
3. `material_sidecar.source.kind`
4. `material_sidecar.license.kind`
5. `material_sidecar.restrictions.*`
6. `thumbnail_patch_result.patch_result.errors[]`

## Rights Readback の非ブロック機構

旧 Compliance Gate は廃止。以下を現在の正本とする：

- `set-compliance --status passed` は VOD 状態や third_party_ip の値で失敗しない。
- 旧 auto-fail 相当は warnings / review notes として保持する。
- `patch-thumbnail` は rights status を readback に残すが、`pending` / `failed` だけでは停止しない。
- material sidecar の `unverified` / `unknown` / `fair_use_claimed` / `thumbnail_use=denied` は metadata として保持し、thumbnail patch を止めない。

## Integrations 隔離方針

`src/integrations/` の中だけが外部送信・課金・規約従属の処理を持つ。本体ロジック（`src/pipeline/`）は integration 結果を受け取るだけ。

| ディレクトリ | 含むもの | 含まないもの |
|---|---|---|
| `src/integrations/youtube/` | OAuth、videos.insert、thumbnails.set、playlist 操作、visibility 更新 | pipeline 本体ロジック |
| `src/integrations/asset_fetch/` | source audio/video 取得 adapter。INT-02a では fake WAV generator、INT-02c では local-media-audio FFmpeg normalize adapter。後続で yt-dlp 系ラッパー / VOD ダウンロード | 編集処理 |
| `src/integrations/stt/` | STT engine wrapper、engine-specific args / output parse。現在は optional Vosk adapter | URL / VOD 取得、cut 候補抽出、字幕生成、render |
| `src/integrations/render/` | OUT-01 tiny diagnostic render、OUT-04 bounded editorial sequence、OUT-05/06 vertical internal candidate、OUT-07 accepted-baseline operator package、OUT-08 unused-range minibatch、OUT-09 second-source repeatability、OUT-10 third-source candidate、OUT-11 endpoint evidence / source-adaptive candidate / five-source combined review、OUT-12 one-command real long-form automation。取得済みsource/caption/plan authority、Timeline IR、source-specific composition/caption policy、media/audio/frame/manifest/readbackを担当する | URL / VOD取得、STT、rights判断、human acceptance、winner選択、production subtitle/design/render acceptance、GUI action、upload、thumbnail upload、visibility、made-for-kids、publishing |
| `src/integrations/bg_removal/` | 背景切り抜き API クライアント、結果ファイル受領 | 元動画への適用、サムネ合成 |
| `src/pipeline/` | manifest／schema／slot patch／validate／transcript 構造変換 | 外部送信、課金、認証 |
| `src/cli/` | コマンドライン entry points | 業務ロジック（pipeline 呼び出しのみ） |

## SH-05 local-preview-pack 境界

正本: [PREVIEW_PACK.md](PREVIEW_PACK.md)

- `build-local-preview-pack` は local media file、または `--use-existing-source-audio` で既存 `source_audio` material を入力に取る。URL / VOD / network-like locator は拒否する。
- local media mode の source audio 生成は既存 `fetch-source-audio --mode local-media-audio` 経路を使う。existing source audio mode は `fetch-source-audio` を呼ばず、`material_ledger.json` / sidecar / receipt を readback する。SH-05 の orchestrator / preview pipeline / GUI は FFmpeg を直接呼ばない。
- transcript は fixture または deterministic fake。`transcript.not_for_acceptance=true` を manifest/report に出し、creative acceptance には使わない。
- `preview_report.html` は read-only。実行 button、GUI fetch button、編集確定 button は置かない。
- SH-05 は rendered video preview、cut / concat、subtitle burn-in、render / encode を実装しない。
- SH-05c GUI ingest は既存 preview pack を読むだけ。`build-local-preview-pack`、fetch、render、upload を GUI から起動しない。

## SH-10 edit-ready Source Packet 境界

- `build-edit-ready-source-packet` は source locator から既存 `fetch-source-video` と
  `fetch-source-audio --mode local-media-audio` を再利用し、取得 adapter を複製しない。
- transcript authority は provider caption、verified sidecar、verified imported
  subtitle transcript、明示 Vosk real STT の優先順位で選ぶ。fake/fixture は authority
  不可で、provider/STT failure を fixture success に置換しない。
- Caption cue は timing、ordering、ID、text、source duration、language、coverage を
  fail-closed 検証する。normalized segment は元 event/segment ID への mapping を保持し、
  発話、話者、歌唱、歌詞、固有名詞、意味を推定しない。
- Operational state は editorial planning、Timeline IR、subtitle processing、render
  pipeline が入力を読めることだけを表す。human/editorial review、rights、production、
  public/publishing、upload は別 gate のまま。
- `--resume` は input fingerprint、packet canonical hash、artifact manifest hash が
  一致した成功 packet だけを再利用する。異入力または破損 cache は既存成功 packet を
  上書きせず typed blocked result を返す。
- 契約正本は `docs/SCHEMAS/v1/edit_ready_source_packet.md`。

## NLMYTGen GUI との整合方針

- **GUI アプリは共有しない**が、見た目・操作感・タブ構造・readback 表示パターンは NLMYTGen GUI に合わせる
- 技術スタックは NLMYTGen と同じ Electron を第1候補（GUI 着手時に再検討）
- ClipPipeGen で得た GUI 知見は **NLMYTGen 側への逆提案として doc／issue ベースで共有**できる。NLMYTGen 側ファイルの直接編集はしない
- GUI（SH-03 / SH-03b / SH-03c）は実装済み。CLI と同じ artifact を読み書きする操作面として位置付ける

## NLMYTGen CLI bridge 方針

NLMYTGen は別リポ。以下の方針で再利用する：

- 呼び出しは subprocess（Python の `subprocess.run`）
- NLMYTGen の Python module を直接 import しない
- NLMYTGen のソースコードをコピーしない
- NLMYTGen の絶対パスは設定ファイル（`config/nlmytgen_path.json`）で管理。ハードコードしない
- NLMYTGen が見つからない／バージョン不一致の場合はエラーで止める。silent fallback しない
- NLMYTGen 側 CLI の出力（stdout/JSON）を本リポの schema に変換するのは pipeline 層の責務

bridge する CLI 候補：

- `patch-thumbnail-template`（Slice 1 で使用）
- `audit-thumbnail-template`（Slice 1 で使用）
- 字幕表示幅計測（後続スライスで Editing 用）

## INT-02b / INT-02c / INT-02d asset_fetch 境界

正本: [ASSET_FETCH_BOUNDARY.md](ASSET_FETCH_BOUNDARY.md) / [YTDLP_AUDIO_SPEC.md](YTDLP_AUDIO_SPEC.md)

- yt-dlp の責務は URL から元 media を取得することだけ。
- FFmpeg の責務は `src/integrations/asset_fetch/` では source audio を `source.wav`（PCM WAV / mono / 16kHz / 16-bit）に正規化すること、`src/integrations/render/` では承認された bounded diagnostic/internal review route の動画・証跡を作ることだけ。
- `transcribe-audio`、`generate-cuts`、`check-cut-context`、`generate-subtitles` は yt-dlp / FFmpeg を直接呼ばない。
- `asset_fetch` は cut / concat / subtitle burn-in / render / encode / preview / creative acceptance を扱わない。
- INT-02c の `local-media-audio` はローカル file の FFmpeg normalize のみ実装済み。INT-02e の `yt-dlp-audio` source audio URL fetch は actual smoke まで完了。INT-02f の `local-media-video` はローカル video file のコピー登録と FFprobe metadata readback のみ実装済み。INT-02h の `yt-dlp-video` source video URL fetch は actual smoke まで完了。GUI fetch button は未実装。
