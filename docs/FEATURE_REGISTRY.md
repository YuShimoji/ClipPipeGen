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
| ED-01 | edit_pack schema v1 | done | `docs/SCHEMAS/v1/edit_pack.md` / `src/pipeline/edit_pack.py` / `init-edit-pack` / `validate-edit-pack`。cut 候補・選択 cut・字幕案・review 状態の器を実装。ED-02 以降の自動検出は未実装 |
| ED-02a | 手動/インポート cut candidate 追加 CLI | done | `add-cut-candidate`。元動画解析・speech-to-text は行わず、人手または別ツールで得た秒数を `edit_pack.cut_candidates[]` に追加し、必要なら `selected_cut_ids[]` に入れる手動/インポート入力スライス |
| ED-02 | カット候補抽出（音声・字幕ベース） | proposed | `transcript.json` の segment / keyword / timing を使って `edit_pack.cut_candidates[]` を生成する。VOD / URL 取得は含めず、必要な音声素材は INT-02 から受け取る |
| ED-03 | 文脈チェック | proposed | `transcript.json` の隣接 segment を参照し、カット境界が話者発話や話題遷移を不自然に切断していないかを review note として返す |
| ED-04 | 字幕案生成 | proposed | `transcript.json` の segment を字幕 draft に変換し、ED-05 の EAW 幅計測を消費して折返し候補を作る。burned-in は外部ツール / future renderer |
| ED-05 | 字幕表示幅計測（EAW、stdlib のみ） | done | `src/pipeline/text_measure.py` に EAW unit 計算と折返し、`measure-subtitle-width` CLI を追加。NLMYTGen の `EastAsianWidthMeasurer` / `WpfTextMeasurer` を bridge する設計だったが NLMYTGen 側に standalone CLI が無いため重複実装を選択。WPF 精度の bridge は `docs/proposals/0002-standalone-measure-text-cli.md` の採否次第で `ED-05b` として再起票 |
| ED-05b | text_measure bridge migration | proposed | NLMYTGen 側で `measure-text` standalone CLI が採用された段階で ClipPipeGen 側の `text_measure.py` を bridge に縮約する。詳細: `docs/proposals/0002` |
| ED-06 | 外部 NLE 用 export（EDL／XML） | proposed | DaVinci Resolve / Premiere 向け export |
| ED-07 | transcript schema v1 + transcribe-audio CLI | done | `docs/SCHEMAS/v1/transcript.md` / `src/pipeline/transcript.py` / `transcribe-audio` / `validate-transcript`。初期 engine は `fake` adapter で、既存のローカル音声ファイル + fixture segments から `transcript.json` を生成する。実 `whisper.cpp` 接続と URL / VOD 取得は含めない |

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
| INT-02 | asset_fetch（source audio / video 取得） | proposed | `fetch-source-audio` / `fetch-source-video` CLI。URL / 出力先 / 推定サイズ / 目的を preflight 表示し、実行 log / receipt / rollback 情報を残す。取得結果は `material_ledger` に自動登録できる。yt-dlp / ffmpeg は `src/integrations/asset_fetch/` に隔離し、CI は fake downloader を使う。rights status は readback に留め、値だけで取得そのものの hard gate にはしない |
| INT-02a | source audio material contract + fake fetch | done | `fetch-source-audio --mode fake` を実装。標準音声は `source.wav`（PCM WAV / mono / 16kHz / 16-bit / 1秒 silent fixture）。`sidecar.json` / `fetch_receipt.json` / `material_ledger.json` を生成し、`kind=source_audio` / `subkind=wav_pcm_16k_mono` / `intended_uses=["editing_audio"]` で ED-07 `transcribe-audio` に接続する。実 yt-dlp / ffmpeg / `fetch-source-video` は親 INT-02 の後続 |
| INT-03 | bg_removal 受領フロー | proposed | 外部処理結果（透過PNG）の受け入れ。API 呼び出しは含めるか別途検討 |
| INT-04 | bg_removal API 呼び出し | proposed | INT-03 の能動版。provider / 入出力 / receipt を integration として実装 |

### Shared infra

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| SH-02L | episode status adapter（GUI MVP 用） | done | full `episode_pack` の前段として、Slice 1 artifact の存在・readback・next_action を返す `status-episode` CLI / `episode_status.py` を実装。GUI MVP が読む薄い背骨 |
| SH-02 | episode_pack 統合 manifest | proposed | rights_manifest / material_ledger / edit_pack / thumbnail_patch / publish_draft を episode 単位で連結 |
| SH-03 | GUI MVP Phase 1（read-only operator console） | done | Electron skeleton（`gui/`）と 5 タブ（Episode / Rights / Materials / Thumbnail / Settings）。`status-episode` JSON を消費して状態表示。外部 API・upload は未実装。`docs/GUI_CONVENTIONS.md` に整合-A 規約 |
| SH-03b | GUI Phase 2（action 導線） | done | Rights / Materials / Thumbnail タブに `set-compliance` / `register-material` / `patch-thumbnail` の form を追加。確認 dialog（command / summary / reason の 3 要素）経由で実行。upload / fetch / bg-removal API は未実装であり、今後通常 integration として追加できる。args builder は `gui/args.cjs` に分離して smoke が Electron なしで検証 |
| SH-03c | GUI Editing tab（ED-01 / ED-02a 範囲のみ） | done | Editing タブを追加し `init-edit-pack` / `add-cut-candidate` / `validate-edit-pack` の form を配置。confirm dialog 経由で実行、結果と `editing.state` badge を表示。ED-02 / ED-03 / ED-04 / ED-06 は未実装のため form を持たず、実装と同時に追加する。CLI 規約「episode_id == dirname」に合わせ prefill は dir basename を使用 |
| SH-04 | NLMYTGen GUI への逆提案運用 | done | `docs/proposals/` に運用パターン (`README.md`) と最初の提案 (`0001-gui-alignment-from-clippipegen-mvp.md` / state=draft) を配置。NLMYTGen 側ファイルは編集せず、提案は doc／issue ベース。採否は NLMYTGen 側判断 |

## 未実装 / 必要時に再起票

| ID | 機能 | 状態 | 理由 |
|---|---|---|---|
| OUT-01 | 動画レンダリング（cut/concat/字幕焼き込み／エンコード） | proposed | 未実装。必要になったら renderer / NLE integration として設計 |
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
