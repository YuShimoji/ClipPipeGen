# Feature Registry

全機能を ID で管理する。登録されていない機能は追加しない。`proposed` はユーザー承認後に `approved` へ昇格してから実装する。

## ID 規則

| プレフィックス | レーン |
|---|---|
| CR-* | Compliance / Rights |
| MS-* | Material Sourcing |
| ED-* | Editing |
| TH-* | Thumbnail |
| PB-* | Publishing |
| INT-* | Integrations（外部 API・AI サービス境界） |
| SH-* | Shared infra（CLI runner・schema validator・config） |

NLMYTGen 側の FEATURE ID（A-* / B-* 等）とは独立。

## 状態

- `proposed` — 提案中。実装着手不可。
- `approved` — ユーザー承認済み。実装着手可。
- `in_progress` — 実装中。
- `done` — 実装＋acceptance 完了。
- `hold` — 一時停止。再開条件を明記する。
- `rejected` — 廃止。理由を残す。

## Slice 1 スコープ（最初の実証）

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| **CR-01** | rights_manifest schema v1 と validator | done | `docs/SCHEMAS/v1/rights_manifest.md` の構造を実装。`compliance_check.status` は readback として保持し、local CLI の hard gate にはしない。Slice 1.1 完了（commit `5be5439`） |
| **MS-01** | material_ledger schema v1 と CRUD CLI | done | 素材登録・索引・sidecar 紐付け。`register-material` / `audit-material-ledger` 実装。Slice 1.2 完了 |
| **MS-02** | material_sidecar schema v1 と validator | done | 出典・ライセンス・利用条件を metadata として検証・保持。source/license/restriction の値は thumbnail 実行を止めない。Slice 1.2 完了 |
| **MS-03** | 透過PNG 受け入れフロー | done | `is_transparent_png` で PNG color_type が 4/6 かを判定、`character_image` + `subkind=transparent_png` で強制。Slice 1.2 完了 |
| **TH-01** | YMM4 サムネ slot patch（NLMYTGen CLI bridge） | done | `nlmytgen_bridge.py` + `thumbnail_patch.py` orchestrator + `audit-thumbnail` / `patch-thumbnail` CLI。rights readback / material resolution / bridge audit / bridge patch / readback の流れ。Slice 1.3 完了。実 YMM4 base template に対する end-to-end walkthrough は user-owned acceptance step として保留 |
| **SH-01** | CLI runner と config（NLMYTGen path 設定含む） | done | `config/nlmytgen_path.json` schema (例ファイル付き、本体 gitignored)、`BridgeConfig.load`、`call_nlmytgen` subprocess wrapper、`BridgeExecutionError` でのエラー伝搬。silent fallback 禁止。Slice 1.3 完了 |

## Slice 2 以降の候補（着手前、proposed のまま）

### Walkthrough / docs

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| **TH-W01** | Slice 1 walkthrough 補助 | done | YMM4 thumbnail template authoring guide、samples/episode_example、SLICE1_WALKTHROUGH ランブック。Slice 2 (d) 完了 |

### Editing 系

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| ED-01 | edit_pack schema v1 | done | `docs/SCHEMAS/v1/edit_pack.md` / `src/pipeline/edit_pack.py` / `init-edit-pack` / `validate-edit-pack`。cut 候補・選択 cut・字幕案・review 状態の器を実装。ED-02 / ED-04 は後続で実装済み |
| ED-02a | 手動/インポート cut candidate 追加 CLI | done | `add-cut-candidate`。元動画解析・speech-to-text は行わず、人手または別ツールで得た秒数を `edit_pack.cut_candidates[]` に追加し、必要なら `selected_cut_ids[]` に入れる手動/インポート入力スライス |
| ED-02 | カット候補抽出（音声・字幕ベース） | done | `generate-cuts` CLI を実装。`transcript.json` の segment timing / text density / topic hint を使って `edit_pack.cut_candidates[]` を生成する。VOD / URL 取得は含めず、必要な音声素材は INT-02 から受け取る |
| ED-03 | 文脈チェック | done | `check-cut-context` CLI を実装。`transcript.json` の隣接 segment を参照し、cut 境界の発話途中切断、source segment 不整合、近接する前後文脈を `cut_candidates[].context_check` に `passed` / `needs_review` / `failed` と notes で返す |
| ED-04 | 字幕案生成 | done | `transcript.json` の segment を `edit_pack.subtitles[]` に変換する `generate-subtitles` CLI を実装。`--wrap-eaw` で ED-05 の EAW 折返しを消費し、`source_segment_id` で transcript 由来を readback する。burned-in は外部ツール / future renderer |
| ED-05 | 字幕表示幅計測（EAW、stdlib のみ） | done | `src/pipeline/text_measure.py` に EAW unit 計算と折返し、`measure-subtitle-width` CLI を追加。NLMYTGen の `EastAsianWidthMeasurer` / `WpfTextMeasurer` を bridge する設計だったが NLMYTGen 側に standalone CLI が無いため重複実装を選択。WPF 精度の bridge は `docs/proposals/0002-standalone-measure-text-cli.md` の採否次第で `ED-05b` として再起票 |
| ED-05b | text_measure bridge migration | proposed | NLMYTGen 側で `measure-text` standalone CLI が採用された段階で ClipPipeGen 側の `text_measure.py` を bridge に縮約する。詳細: `docs/proposals/0002` |
| ED-06 | 外部 NLE 用 minimal export | done | `export-nle` CLI を追加し、`edit_pack.json` から `nle_cut_list.csv` / `nle_export_manifest.json` / `nle_export_report.html` を生成する。現行出口は CSV cut list + readback で、FCPXML / Resolve XML / render / encode は後続。fake / fixture transcript 由来 export は production candidate ではない warning を保持 |
| ED-07 | transcript schema v1 + transcribe-audio CLI | done | `docs/SCHEMAS/v1/transcript.md` / `src/pipeline/transcript.py` / `transcribe-audio` / `validate-transcript`。初期 engine は `fake` adapter で、既存のローカル音声ファイル + fixture segments から `transcript.json` を生成する。実 `whisper.cpp` 接続と URL / VOD 取得は含めない |
| ED-07b | real STT transcript path | done | optional Vosk adapter を `src/integrations/stt/` に追加し、明示 model path の実 `source.wav` から `real_transcript=true` の `transcript.json` を生成できるようにした。provider / model 不在は preflight failure で fixture fallback しない。生成 transcript は `generate-cuts` / `check-cut-context` / `generate-subtitles` / ED-06 CSV export に接続済み。STT 品質評価、話者分離、render、GUI STT button、source-video acquisition、publishing は含めない |
| ED-08 | real STT subtitle draft linkage | done | `generate-subtitles` が `transcript.stt.real_transcript=true` を読み、`edit_pack.subtitles[]` に `source_type="real_transcript"` / `source_segment_ids[]` / diagnostic draft flags を保持するようにした。fake / fixture transcript は `source_type="transcript_segments"` のまま production candidate にしない。STT 品質評価、transcript correction UI、subtitle design acceptance は含めない |

### Publishing 系

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| PB-01 | publish_draft schema v1 | proposed | metadata（タイトル・説明・タグ・category）の整形 |
| PB-02 | private/unlisted upload integration | proposed | `src/integrations/youtube/` 経由 |
| PB-03 | thumbnail 設定 integration | proposed | `thumbnails.set` |
| PB-04 | upload receipt 記録 | proposed | `upload_receipt.json` |

### Integrations

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| INT-01 | YouTube OAuth flow | proposed | trusted application のセットアップ含む |
| INT-02 | asset_fetch（source audio / video 取得） | proposed | `fetch-source-audio` / `fetch-source-video` CLI。URL / 出力先 / 推定サイズ / 目的を preflight 表示し、実行 log / receipt / rollback 情報を残す。取得結果は `material_ledger` に自動登録できる。yt-dlp / ffmpeg は `src/integrations/asset_fetch/` に隔離し、CI は fake downloader / fake subprocess adapter を使う。rights status は readback に留め、値だけで取得そのものの hard gate にはしない |
| INT-02a | source audio material contract + fake fetch | done | `fetch-source-audio --mode fake` を実装。標準音声は `source.wav`（PCM WAV / mono / 16kHz / 16-bit / 1秒 silent fixture）。`sidecar.json` / `fetch_receipt.json` / `material_ledger.json` を生成し、`kind=source_audio` / `subkind=wav_pcm_16k_mono` / `intended_uses=["editing_audio"]` で ED-07 `transcribe-audio` に接続する。実 yt-dlp / ffmpeg / `fetch-source-video` は親 INT-02 の後続 |
| INT-02b | asset_fetch boundary spec only | done | 実 downloader 実装前に `docs/ASSET_FETCH_BOUNDARY.md` で yt-dlp / ffmpeg の責務を固定。yt-dlp は URL から元 media を取得するだけ、ffmpeg は source audio を PCM WAV / mono / 16kHz / 16-bit に正規化するだけ。Editing core / STT / render / cut / GUI への浸透を禁止し、future mode の preflight / receipt / rollback / ledger readback contract とテスト観点を定義 |
| INT-02c | local-media-audio normalize | done | `fetch-source-audio --mode local-media-audio` を実装。入力はローカル media file のみ。FFmpeg は `src/integrations/asset_fetch/ffmpeg_audio.py` からだけ呼び、`source.wav`（PCM WAV / mono / 16kHz / 16-bit）、sidecar、receipt、ledger entry を生成する。dry-run は subprocess を呼ばず command plan を返す。実 yt-dlp / network fetch / `fetch-source-video` / GUI fetch button は未実装 |
| INT-02d | yt-dlp-audio boundary spec only | done | `docs/YTDLP_AUDIO_SPEC.md` で URL fetch / network access / yt-dlp / FFmpeg 正規化 / receipt / rights readback / human responsibility / GUI 非露出 / STT 非接続を分離。実 `yt-dlp-audio` mode、yt-dlp 実行、network fetch、GUI fetch button は未実装 |
| INT-02e | yt-dlp-audio source audio URL fetch | done | `fetch-source-audio --mode yt-dlp-audio` を source audio URL fetch のみに限定して実装。yt-dlp は `src/integrations/asset_fetch/yt_dlp_audio.py` で一時 media 取得のみ、FFmpeg は `source.wav` 正規化のみ。sidecar / receipt / ledger を生成し、rights は readback snapshot で hard gate にしない。`fetch-source-video` / GUI fetch button / GUI からの fetch/build/render / `transcribe-audio` URL fetch / cut・concat・subtitle burn-in・render・encode は追加しない。fake runner / dry-run / tests に加え、technical smoke URL の actual run で receipt / sidecar / ledger / WAV readback を確認 |
| INT-02f | local source video acquisition | done | `fetch-source-video --mode local-media-video` を追加。既存ローカル video file を `source_video.<ext>` として episode material directory にコピーし、FFprobe metadata（duration / container / video codec / audio codec / resolution / fps / stream count）、sidecar、fetch_receipt、material_ledger entry を生成する。URL video fetch、render / encode、cut / concat、subtitle burn-in、GUI fetch button、publishing は含めない |
| OUT-01 | tiny render proof | done | `render-tiny-proof` を追加。source_video material / source_audio material / edit_pack の最初の selected cut から diagnostic `rendered_video.mp4` または `.mkv`、`render_receipt.json`、`render_manifest.json`、`render_report.html` を生成する。timeline は shortest input に clamp し、output metadata を FFprobe で readback する。production render、creative acceptance、publishing、subtitle burn-in、GUI button、URL video fetch は含めない |
| OUT-01a | render preflight / fallback readback | done | OUT-01 の tiny diagnostic render に、FFmpeg/FFprobe preflight、render profile fallback、attempt status、selected profile、failure classification を追加。receipt / manifest / report が `environment_missing_ffmpeg`、`codec_or_container_unsupported`、`input_video_missing`、`metadata_probe_failed` などを readback し、fresh smoke で `rendered_video.mp4` を再生成する。production render、subtitle burn-in、URL video fetch、GUI render button は含めない |
| OUT-01b | longer local video render smoke | done | OUT-01a の render path を使い、10 秒以上の local source_video + source_audio + edit_pack selected cut から diagnostic `rendered_video.mp4` を再生成する。fresh smoke は duration `12.0` / h264 / aac / `640x360` / `24.0fps` / stream count `2` を readbackし、timeline clamp なし、selected profile `mp4_h264_aac`、fallback なし。subtitle burn-in、URL video fetch、GUI render button、production/creative/publish acceptance は含めない |
| OUT-01c | subtitle burn-in diagnostic | done | `render-tiny-proof --burn-in-subtitles diagnostic` を追加。`edit_pack.subtitles[]`（無い場合は sibling `transcript.json` segments）から UTF-8 SRT を生成し、FFmpeg `subtitles` filter で diagnostic overlay として焼き込む。`render_receipt.json` / `render_manifest.json` / `render_report.html` は subtitle source ref、overlay policy、burn-in status、selected profile、attempts、output metadata を readback する。font / safe-area / line-wrap polish、production render、creative acceptance、URL video fetch、GUI render button、publishing は含めない |
| OUT-01d | subtitle timing / font-filter preflight | done | OUT-01c の diagnostic subtitle overlay を維持し、subtitle item ごとの `included` / `clamped_to_render_window` / `skipped_before_render_window` / `skipped_after_render_window` / `invalid_timing` / `empty_text`、source timeline から render timeline への offset/clamp/skip readback、SRT encoding、FFmpeg subtitles filter / libass / fontconfig / font / path escaping の failure detail を `render_receipt.json` / `render_manifest.json` / `render_report.html` に追加。fresh smoke は edit_pack subtitle draft 由来の included/clamped/skipped items を焼き込み、duration `12.0` / h264 / aac / `640x360` / `24.0fps` / stream count `2` を readback。production subtitle design、typography/safe-area polish、URL video fetch、GUI render button、publishing は含めない |
| OUT-01e | real STT subtitle diagnostic render smoke | done | ED-08 の `source_type="real_transcript"` subtitle drafts を OUT-01d timing diagnostic burn-in に接続し、`render_receipt.json` / `render_manifest.json` / `render_report.html` で subtitle source type、`derived_from_real_transcript=true`、transcript provider/model、`source_segment_ids[]`、timing status を readback できるようにした。fresh smoke は Vosk real transcript 由来 subtitle を `rendered_video.mp4` に焼き込み、duration `8.82` / h264 / aac / `640x360` / `24/1fps` / stream count `2` を FFprobe readback。production render、subtitle quality/design、URL video fetch、GUI render button、publishing は含めない |
| INT-03 | bg_removal 受領フロー | proposed | 外部処理結果（透過PNG）の受け入れ。API 呼び出しは含めるか別途検討 |
| INT-04 | bg_removal API 呼び出し | proposed | INT-03 の能動版。provider / 入出力 / receipt を integration として実装 |

### Shared infra

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| SH-02L | episode status adapter（GUI MVP 用） | done | full `episode_pack` の前段として、Slice 1 artifact の存在・readback・next_action を返す `status-episode` CLI / `episode_status.py` を実装。GUI MVP が読む薄い背骨 |
| SH-02 | episode_pack 統合 manifest | proposed | rights_manifest / material_ledger / edit_pack / thumbnail_patch / publish_draft を episode 単位で連結 |
| SH-03 | GUI MVP Phase 1（read-only operator console） | done | Electron skeleton（`gui/`）と 5 タブ（Episode / Rights / Materials / Thumbnail / Settings）。`status-episode` JSON を消費して状態表示。外部 API・upload は未実装。`docs/GUI_CONVENTIONS.md` に整合-A 規約 |
| SH-03b | GUI Phase 2（action 導線） | done | Rights / Materials / Thumbnail タブに `set-compliance` / `register-material` / `patch-thumbnail` の form を追加。確認 dialog（command / summary / reason の 3 要素）経由で実行。upload / fetch / bg-removal API は未実装であり、今後通常 integration として追加できる。args builder は `gui/args.cjs` に分離して smoke が Electron なしで検証 |
| SH-03c | GUI Editing tab（ED-01 / ED-02a 範囲のみ） | done | Editing タブを追加し `init-edit-pack` / `add-cut-candidate` / `validate-edit-pack` の form を配置。confirm dialog 経由で実行、結果と `editing.state` badge を表示。ED-02 / ED-03 / ED-04 / ED-06 は CLI 実装済みだが GUI action form は未追加。CLI 規約「episode_id == dirname」に合わせ prefill は dir basename を使用 |
| SH-04 | NLMYTGen GUI への逆提案運用 | done | `docs/proposals/` に運用パターン (`README.md`) と最初の提案 (`0001-gui-alignment-from-clippipegen-mvp.md` / state=draft) を配置。NLMYTGen 側ファイルは編集せず、提案は doc／issue ベース。採否は NLMYTGen 側判断 |
| SH-05 | local-preview-pack orchestrator | done | `build-local-preview-pack` CLI を追加。local media 1本から `source.wav`、fake/fixture transcript、cut candidates、context status、subtitle draft、`preview_manifest.json`、read-only `preview_report.html` を生成する。rendered video preview、network fetch、GUI fetch button、render / encode は含めない |
| SH-05b | local-preview-pack report QA / polish | done | `preview_report.html` に Status Summary、Decision Warnings、Artifact Links を追加し、not-for-acceptance、rights pending readback、manifest / receipt / source.wav links を明確化。日本語 fixture smoke を localhost / DOM readback で確認。GUI ingest、network fetch、render / encode は含めない |
| SH-05b+ | local-preview-pack visual evidence hardening | done | medium 日本語 fixture smoke で `preview_report.html` の実画面 screenshot / visual readback を保存。`preview_manifest` lightweight validation を追加し、warnings / not-for-acceptance / rights pending / artifact links / audio controls の視認性を確認。GUI ingest、network fetch、render / encode は含めない |
| SH-05c | GUI read-only preview pack ingest | done | GUI に Preview Pack tab を追加。既存 episode directory または `preview_manifest.json` を読み、manifest validation、Status Summary、Decision Warnings、Artifact Links を read-only 表示する。GUI から build / fetch / render / upload は実行しない |
| SH-05d | source-audio preview bridge | done | `build-local-preview-pack --use-existing-source-audio` を追加し、INT-02e などで取得済みの `source.wav` / `fetch_receipt.json` / `sidecar.json` / `material_ledger.json` を再 download なしで local preview pack の review surface / `preview_manifest.json` / `preview_report.html` に接続する。report は Source Audio Provenance を表示し、fake/fixture transcript と生成 edit_pack は production candidate ではないと明示する。reproducible existing-source-audio smoke は通過、real INT-02e artifact smoke は元 ignored artifact 不在のため pending。新規 downloader、GUI fetch button、GUI からの build-local-preview-pack 実行、render / encode、cut / concat、subtitle burn-in は含めない |

## 未実装 / 必要時に再起票

| ID | 機能 | 状態 | 理由 |
|---|---|---|---|
| OUT-02 | 音声合成（TTS） | proposed | 未実装。必要になったら provider integration として設計 |
| OUT-03 | visibility 更新（public 化含む） | proposed | 未実装。YouTube integration の一部として設計 |
| OUT-04 | 完全自動サムネ合成 | proposed | 未実装。必要になったら thumbnail renderer として設計 |
| OUT-05 | `.ymmp` ゼロ生成 | proposed | 未実装。必要になったら YMM4 schema readback を伴う generator として設計 |
| OUT-06 | NLMYTGen 側ファイル編集 | rejected | cross-project 指示なしには編集しない。再利用は CLI subprocess 経由 |

## 状態遷移ログ

（slice ごとに、状態遷移の根拠を1行で残す）

- bootstrap: 全項目を `proposed` で起票。根拠: docs/FIRST_SLICE.md / docs/LANES.md
- 2026-05-06: Slice 1 の `CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01` を `approved` に昇格。根拠: ユーザー指示（軽量 review 後の着手承認）
- 2026-05-06: `CR-01` を `done` に遷移。根拠: Slice 1.1 実装＋テスト（commit `5be5439`）
- 2026-05-06: `MS-01 / MS-02 / MS-03` を `done` に遷移。根拠: Slice 1.2 実装＋テスト 23 件 pass
- 2026-05-06: `TH-01 / SH-01` を `done` に遷移。根拠: Slice 1.3 実装＋テスト 31 件 pass（NLMYTGen subprocess は monkeypatch でモック）
- 2026-05-07: Slice 2 (d) `TH-W01` を起票・即 done に遷移。根拠: docs/walkthrough/{YMM4_THUMBNAIL_TEMPLATE_AUTHORING,SLICE1_WALKTHROUGH}.md と samples/episode_example/* を配置（user owned acceptance step を docs で支援）
- 2026-05-07: `SH-03` を `approved` に昇格。根拠: ユーザー指示（推奨対応で進行） + docs/GUI_MVP_SCOPE.md
- 2026-05-07: `SH-02L` を起票・即 done に遷移。根拠: `src/pipeline/episode_status.py` / `src/cli/status_episode.py` / `tests/test_episode_status.py`（34 tests pass）
- 2026-05-07: `SH-03` を Phase 1（read-only console）として `done` に遷移。根拠: `gui/` Electron skeleton + 5 タブ UI が `status-episode` JSON を消費して状態表示。Phase 2 は `SH-03b` として分離・proposed
- 2026-05-07: `SH-03b` を起票（proposed）。根拠: GUI Phase 1 の DoD を狭く保ち、action 導線は別スライスで承認・実装する方が手戻りが少ない
- 2026-05-07: `SH-04` を `done` に遷移。根拠: `docs/proposals/{README,0001-gui-alignment-from-clippipegen-mvp}.md` を配置（提案運用 + 初稿 1 本、state=draft）
- 2026-05-07: `SH-03b` を `done` に遷移。根拠: `gui/main.cjs` に IPC `action:setCompliance` / `action:registerMaterial` / `action:patchThumbnail`、`gui/preload.cjs` に bridge methods、`gui/renderer.{html,js,smoke.cjs}` に form＋確認 dialog＋result。args builder は `gui/args.cjs` 分離。Electron 必要なし smoke pass、Python 46 件 pass
- 2026-05-08: `SH-03c` を起票・即 `done` に遷移。根拠: GUI に Editing タブと `init-edit-pack` / `add-cut-candidate` / `validate-edit-pack` action panel を追加（args.cjs / main.cjs IPC / preload bridge / renderer html+js / smoke 全更新）。samples/episode_example の dir 名と episode_id を harmonize し end-to-end status-episode が rights/materials/editing/thumbnail 全 ready で進行確認
- 2026-05-08: `ED-05` を `done`、`ED-05b` を `proposed` で起票。根拠: NLMYTGen に standalone `measure-text` CLI が無いため bridge 不可、stdlib EAW measurer を ClipPipeGen 側に実装（`src/pipeline/text_measure.py` + `measure-subtitle-width` CLI、テスト 10 件 pass）。WPF 精度 bridge は `docs/proposals/0002-standalone-measure-text-cli.md` で逆提案、採用時に ED-05b で実装する
- 2026-05-07: `ED-01` を `approved` 相当として実装し `done` に遷移。根拠: ユーザー指示（推奨対応で進行） + `docs/SCHEMAS/v1/edit_pack.md` / `src/pipeline/edit_pack.py` / `tests/test_edit_pack.py`（43 tests pass）
- 2026-05-07: `ED-02a` を起票・即 done に遷移。根拠: ED-02 本体（音声・字幕ベースの自動抽出）前に、外部 API なしで `edit_pack` へ cut 候補を投入する手動/インポート導線を確保するため
- 2026-05-08: `ED-07` を `proposed` で起票し、`docs/SCHEMAS/v1/transcript.md` を追加。根拠: `transcribe-audio` はローカル音声ファイル → `transcript.json` に限定し、URL / VOD 取得は INT-02 `asset_fetch` として分離するユーザー判断
- 2026-05-09: `ED-07` を `done` に遷移。根拠: `src/pipeline/transcript.py` / `transcribe-audio --engine fake` / `validate-transcript` / `status-episode` transcript readback / `tests/test_transcript.py` を実装。実 STT engine と asset fetch は次 feature のまま分離
- 2026-05-10: `INT-02a` を `done` として追加。根拠: `fetch-source-audio --mode fake` / `src/integrations/asset_fetch/fake_audio.py` / `fetch_receipt.schema` / `tests/test_source_audio_fetch.py` を実装。親 `INT-02` は real fetch / video が残るため `proposed` のまま維持
- 2026-05-10: `ED-04` を `done` に遷移。根拠: `src/pipeline/subtitle_generation.py` / `generate-subtitles` / ED-05 `measure_subtitle` 消費 / `tests/test_subtitle_generation.py` を実装。実 subtitle burn-in / renderer は OUT-01 後続
- 2026-05-10: `ED-02` を `done` に遷移。根拠: `src/pipeline/cut_generation.py` / `generate-cuts` / transcript window heuristic / `tests/test_cut_generation.py` を実装。文脈妥当性の判定は ED-03 で後続実装済み
- 2026-05-10: `ED-03` を `done` に遷移。根拠: `src/pipeline/context_check.py` / `check-cut-context` / `status-episode` context readback / `tests/test_context_check.py` を実装。実動画 preview / NLE export は ED-06 / OUT-01 後続
- 2026-05-10: `INT-02b` を `done` に遷移。根拠: `docs/ASSET_FETCH_BOUNDARY.md` と `tests/test_asset_fetch_boundary.py` で、yt-dlp / ffmpeg の責務、future mode contract、readback、rollback、core 侵入防止テストを仕様化。実 downloader は未実装のまま維持
- 2026-05-10: `INT-02c` を `done` に遷移。根拠: `src/integrations/asset_fetch/ffmpeg_audio.py` / `fetch-source-audio --mode local-media-audio` / `tests/test_ffmpeg_audio_adapter.py` / `tests/test_source_audio_fetch.py`。ローカル media の FFmpeg 正規化だけを実装し、yt-dlp / network fetch / `fetch-source-video` / GUI fetch button は未実装のまま維持
- 2026-05-11: `INT-02c` の real FFmpeg operator smoke を完了。根拠: ignored scratch episode `episodes/int02c_operator_smoke` で synthetic local WAV を `fetch-source-audio --mode local-media-audio` に渡し、実 FFmpeg による `source.wav`、receipt、sidecar、ledger entry、`audit-material-ledger ok=true`、Python `wave` readback（mono / 16kHz / 16-bit / 2.0秒）を確認。yt-dlp / network fetch / `fetch-source-video` / GUI fetch button は未実装のまま維持
- 2026-05-11: `INT-02d` を `done` に遷移。根拠: `docs/YTDLP_AUDIO_SPEC.md` と `docs/ASSET_FETCH_BOUNDARY.md` で `yt-dlp-audio` を spec only として固定。URL fetch / network / yt-dlp / FFmpeg / receipt / rights / human / GUI / STT の責務を分離し、CLI mode と実 network fetch は未実装のまま維持
- 2026-05-11: `SH-05` を `done` に遷移。根拠: `build-local-preview-pack` / `src/pipeline/preview_pack.py` / `docs/PREVIEW_PACK.md` / `tests/test_preview_pack.py` を追加し、local media から `preview_manifest.json` と read-only `preview_report.html` までの 1 command review surface を実装。ignored scratch `episodes/sh05_operator_smoke_verify` で fresh episode / `--force` なしの実 local operator smoke を通し、1 cut candidate / context passed / 1 subtitle / audio controls report を確認。yt-dlp / network fetch / `fetch-source-video` / GUI fetch button / render / encode は未実装のまま維持
- 2026-05-11: `SH-05b` を `done` に遷移。根拠: `preview_report.html` の status summary / decision warnings / artifact links を追加し、日本語 fixture transcript smoke を ignored scratch で実行。localhost / DOM readback で not-for-acceptance、rights pending readback、manifest / receipt links、audio controls、実行 button / rendered video 不在を確認。yt-dlp / network fetch / `fetch-source-video` / GUI fetch button / render / encode は未実装のまま維持
- 2026-05-11: `SH-05b+` を `done` に遷移。根拠: medium 日本語 fixture transcript smoke を ignored scratch で実行し、localhost 実画面 screenshot / visual readback を保存。`validate_preview_manifest` で manifest issues `[]`、`source.wav` mono / 16kHz / 16-bit / 8.0秒、warning visibility、artifact links、audio controls、実行 button / form / video 不在を確認。GUI ingest、yt-dlp / network fetch、`fetch-source-video`、render / encode は未実装のまま維持
- 2026-05-11: `SH-05c` を `done` に遷移。根拠: `gui/preview_reader.cjs` / GUI Preview Pack tab / `npm run smoke` で existing preview pack read-only ingest と manifest validation を実装。ignored scratch の SH-05b smoke episode を GUI で読み、`state=ready`、validation issues `0`、artifact links 6件 exists、Preview Pack panel 内の form/button 0件を screenshot / DOM readback で確認。GUI から build / fetch / render / upload は未実装のまま維持
- 2026-05-11: `INT-02e` を `approved` 相当として実装し `in_progress` に遷移。根拠: ユーザー承認（source audio URL fetch のみに限定、Default executor: assistant、User input required only for smoke URL selection and rights / terms review） + `src/integrations/asset_fetch/yt_dlp_audio.py` / `fetch-source-audio --mode yt-dlp-audio` / fake runner tests / dry-run readback。実 URL operator smoke は user-owned URL 選定と rights / terms review 待ち
- 2026-05-12: `INT-02e` を `done` に遷移。根拠: `uv tool install yt-dlp` で user-local yt-dlp `2026.03.17` を用意し、ignored scratch episode `episodes/int02e_operator_smoke_20260512` で `fetch-source-audio --mode yt-dlp-audio` を fresh episode / `--force` なしで実行。dry-run は no-write / no-subprocess / URL scrub / conflictsなし、actual は `source.wav`、sidecar、receipt、ledger entry を生成。receipt は yt-dlp + FFmpeg tools、download / normalize command summaries、`intermediate.retained=false`、rights `pending` / `hard_gate=false`、rollback files を保持。Python `wave` readback は mono / 16kHz / 16-bit / 2.07425秒、`audit-material-ledger ok=true`。
- 2026-05-12: `SH-05d` を `done` に遷移。根拠: `build-local-preview-pack --use-existing-source-audio` / `src/pipeline/preview_pack.py` の material provenance readback / `gui/preview_reader.cjs` の read-only manifest validation を実装。targeted test で existing source audio mode が `fetch-source-audio` を呼ばず、既存 `source.wav` / `fetch_receipt.json` / `sidecar.json` / `material_ledger.json` を `preview_manifest.json` と `preview_report.html` に接続することを確認。ignored `episodes/sh05d_existing_source_audio_smoke_20260512` の reproducible smoke で manifest / report / GUI reader readback も確認。real INT-02e artifact smoke は元 ignored artifact がローカルに無いため pending。ED-06、real STT、render、GUI fetch button、publishing、NLMYTGen config は未着手のまま維持。
- 2026-05-12: `ED-06` を `done` に遷移。根拠: `src/pipeline/nle_export.py` / `src/cli/export_nle.py` / `docs/SCHEMAS/v1/nle_export.md` を追加し、`edit_pack.json` から CSV cut list、JSON manifest、HTML readback report を生成できるようにした。targeted tests で selected cut の export、未選択時の全候補 review export、CLI JSON readback、source audio provenance、fake / fixture transcript warning、production candidate false を確認。FCPXML / Resolve XML、real STT、render / encode、GUI export button、source-video acquisition、publishing は後続。
- 2026-05-12: `ED-07b` を `done` に遷移。根拠: `src/integrations/stt/vosk_adapter.py` / `src/cli/transcribe_audio.py` / `src/pipeline/transcript.py` / `src/pipeline/nle_export.py` を更新し、optional Vosk real STT で `source.wav` から `transcript.json` を生成、その transcript から cut / context / subtitle / ED-06 `csv_cut_list_v1` export まで接続した。ignored `episodes/ed07b_real_stt_smoke_20260512` で 1 segment / 9.45 秒の real transcript、1 cut、1 subtitle、`nle_cut_list.csv` / manifest / report readback を確認。production candidate は false のまま、STT 品質・creative edit・render・source-video・GUI button・publishing は後続。
- 2026-05-12: `INT-02f` を `done` に遷移。根拠: `src/integrations/asset_fetch/source_video.py` / `src/cli/fetch_source_video.py` を追加し、`fetch-source-video --mode local-media-video` で local source video を `source_video.<ext>` として登録、FFprobe metadata、sidecar、fetch_receipt、material_ledger entry を生成できるようにした。ignored `episodes/int02f_source_video_smoke_20260512` で `source_video.mkv`、receipt、sidecar、ledger audit ok、duration 1.2秒 / mpeg4 / 160x90 / 15fps / matroska,webm を readback。render / encode、URL video fetch、GUI fetch button、publishing は後続。
- 2026-05-12: `OUT-01` を `done` に遷移。根拠: `src/integrations/render/ffmpeg_tiny.py` / `src/cli/render_tiny_proof.py` / `tests/test_tiny_render.py` を追加し、source_video + source_audio + edit_pack selected cut から diagnostic rendered video、receipt、manifest、HTML report を生成できるようにした。ignored `episodes/ed07b_real_stt_smoke_20260512` に `src_video_out01_smoke` を追加し、real STT 由来 `edit_pack.json` と `src_audio_real_stt_smoke/source.wav` から `renders/out01_tiny_render_smoke/rendered_video.mp4` を生成、duration 1.11秒 / h264 / aac / 160x90 / 15fps / stream count 2 を readback。production render、creative acceptance、subtitle burn-in、URL video fetch、GUI button、publishing は後続。
- 2026-05-13: `OUT-01a` を `done` に遷移。根拠: `src/integrations/render/ffmpeg_tiny.py` / `src/cli/render_tiny_proof.py` / `docs/SCHEMAS/v1/tiny_render.md` / `tests/test_tiny_render.py` を更新し、render 前 preflight、profile fallback、attempt/failure readback、failure artifact receipt/manifest/report を追加。fresh ignored episode `episodes/out01a_hardened_smoke_20260513` で `rendered_video.mp4` を再生成し、FFprobe metadata を readback。production render、subtitle burn-in、URL video fetch、GUI render button、publishing は後続。
- 2026-05-13: `OUT-01b` を `done` に遷移。根拠: `src/cli/render_tiny_proof.py` / `tests/test_tiny_render.py` / `docs/SCHEMAS/v1/tiny_render.md` を更新し、10 秒以上 local render smoke の manifest readback、source audio WAV format 補完、clamp / duration target unmet warning tests を追加。fresh ignored episode `episodes/out01b_long_local_render_smoke_20260513` で `src_video_out01b_long_local` / `src_audio_out01b_long_local` / `cut_out01b_long_001` から `renders/out01b_long_local/rendered_video.mp4` を再生成し、duration 12.0秒 / h264 / aac / 640x360 / 24fps / stream count 2 を readback。subtitle burn-in、URL video fetch、GUI render button、publishing は後続。
- 2026-05-13: `OUT-01c` を起票・承認・`done` に遷移。根拠: ユーザー指示（OUT-01c subtitle burn-in diagnostic）+ `src/integrations/render/ffmpeg_tiny.py` / `src/cli/render_tiny_proof.py` / `tests/test_tiny_render.py` / `docs/SCHEMAS/v1/tiny_render.md` を更新し、fresh ignored episode `episodes/out01c_subtitle_burnin_smoke_20260513` で `edit_pack.subtitles[]` 由来の diagnostic overlay を `renders/out01c_subtitle_burnin/rendered_video.mp4` に焼き込み、duration 12.0秒 / h264 / aac / 640x360 / 24fps / stream count 2、subtitle source ref、overlay policy、burn-in status を readback。production render、subtitle design acceptance、URL video fetch、GUI render button、publishing は後続。
- 2026-05-14: `OUT-01d` を起票・承認・`done` に遷移。根拠: ユーザー指示（OUT-01d subtitle timing / font-filter preflight）+ `src/cli/render_tiny_proof.py` / `src/integrations/render/ffmpeg_tiny.py` / `tests/test_tiny_render.py` / `docs/SCHEMAS/v1/tiny_render.md` を更新し、subtitle item ごとの original/render timing、render_start offset、included/clamped/skipped/invalid/empty status、SRT encoding、subtitles/libass/fontconfig/font/path failure detail を receipt / manifest / report へ追加。fresh ignored episode `episodes/out01d_timing_font_preflight_smoke_20260514` で `edit_pack.subtitles[]` 由来の diagnostic overlay を `renders/out01d_timing_font_preflight/rendered_video.mp4` に焼き込み、duration 12.0秒 / h264 / aac / 640x360 / 24fps / stream count 2、status counts、filter preflight status を readback。production subtitle design、URL video fetch、GUI render button、publishing は後続。
- 2026-05-16: `ED-08` / `OUT-01e` を起票・承認・`done` に遷移。根拠: ユーザー指示（real STT transcript -> subtitle draft -> edit_pack.subtitles[] -> OUT-01d diagnostic render）+ `src/pipeline/subtitle_generation.py` / `src/cli/render_tiny_proof.py` / `tests/test_subtitle_generation.py` / `tests/test_real_transcript_pipeline.py` / `tests/test_tiny_render.py` を更新し、real transcript 由来 subtitle source / segment IDs / non-production draft flags を edit_pack と render readback に保持した。fresh ignored episode `episodes/out01e_real_transcript_subtitle_smoke_20260516` で Vosk real transcript 由来 `sub_001` を `renders/out01e_real_transcript_subtitle_render/rendered_video.mp4` に焼き込み、duration 8.82秒 / h264 / aac / 640x360 / 24/1fps / stream count 2、`derived_from_real_transcript=true`、status counts `included=1` を readback。STT 品質評価、transcript correction UI、production subtitle design、URL video fetch、GUI render button、publishing は後続。
