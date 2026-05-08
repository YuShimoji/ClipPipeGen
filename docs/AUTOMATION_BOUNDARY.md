# Automation Boundary

何を自動化し、何を外部 integration / 外部ツールとして扱うかの境界。禁止リストではなく、実装面の分離を定義する。

## Integration マップ

| 種別 | 操作 | 場所 | 現在の扱い |
|---|---|---|---|
| Local | manifest／schema validate | `src/pipeline/*` | 実装済み |
| Local/Bridge | サムネ slot patch 適用（書き出し） | `src/cli/patch_thumbnail.py`（NLMYTGen CLI bridge 経由） | 実装済み。出力先は input で指定 |
| Local/External tool | speech-to-text（ローカル音声 → transcript） | `src/cli/transcribe_audio.py` / future `src/integrations/stt/` | ED-07 adapter surface 実装済み（fake engine）。URL / VOD 取得は含めない |
| External integration | source audio / video 取得 | `src/integrations/asset_fetch/` | INT-02。`fetch-source-audio` / `fetch-source-video` として通常の future integration |
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
  - ローカル音声ファイルからの transcript 生成（`transcribe-audio --engine fake` は実装済み。実 STT engine は後続）
  - カット候補抽出（`edit_pack.cut_candidates`）
  - 字幕案生成（`edit_pack.subtitles`）
  - upload / thumbnail 設定 / visibility 更新 integration

## 現時点で未実装

- 動画レンダリング / cut / concat / 字幕焼き込み / エンコード
- 音声合成 / TTS
- YouTube upload / thumbnail 設定 / visibility 更新
- 元動画ダウンロード
- 実 STT engine 接続（`whisper.cpp` 等）
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
| `src/integrations/asset_fetch/` | yt-dlp 系ラッパー、VOD ダウンロード | 編集処理 |
| future `src/integrations/stt/` | STT engine wrapper、engine-specific args / output parse | URL / VOD 取得、cut 候補抽出 |
| `src/integrations/bg_removal/` | 背景切り抜き API クライアント、結果ファイル受領 | 元動画への適用、サムネ合成 |
| `src/pipeline/` | manifest／schema／slot patch／validate／transcript 構造変換 | 外部送信、課金、認証 |
| `src/cli/` | コマンドライン entry points | 業務ロジック（pipeline 呼び出しのみ） |

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
