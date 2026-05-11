# ClipPipeGen

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

**Slice 1 ソフト実装は done**（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）。Slice 2 では GUI action 導線、Editing tab、`edit_pack`、手動 cut 入力、字幕幅計測、`transcript.json` / fake `transcribe-audio` adapter、`fetch-source-audio --mode fake` の source audio 契約、`fetch-source-audio --mode local-media-audio` のローカル media 正規化、`generate-cuts` の cut 候補生成、`check-cut-context` の文脈チェック、`generate-subtitles` の字幕案生成、`build-local-preview-pack` による local review pack 生成、GUI Preview Pack tab による既存 preview pack の read-only ingest が実装済み。

次の自動化アンカーは実 downloader 接続（INT-02 successor）だが、先に INT-02b として [asset_fetch 境界仕様](docs/ASSET_FETCH_BOUNDARY.md) を固定済み。INT-02c では URL / VOD / network fetch へ進まず、既存ローカル media file を FFmpeg で `source.wav`（PCM WAV / mono / 16kHz / 16-bit）に正規化する adapter だけを `src/integrations/asset_fetch/` に追加した。INT-02d では [yt-dlp-audio 境界仕様](docs/YTDLP_AUDIO_SPEC.md) を spec only として固定済み。INT-02e では `fetch-source-audio --mode yt-dlp-audio` を source audio URL fetch のみに限定して assistant-side 実装 in_progress（実 URL smoke は user-owned URL 選定と rights / terms review 待ち）。SH-05 では、ローカル media 1本から `source.wav`、fake/fixture transcript、cut candidates、context status、subtitle draft、`preview_manifest.json`、read-only `preview_report.html` までを 1 command で生成する review surface を追加した。SH-05c では GUI から既存 preview pack を read-only 表示できるようにしたが、GUI から生成・fetch・render は実行しない。`transcribe-audio` は既存のローカル音声ファイルを `transcript.json` にする責務に限定し、URL / VOD からの取得は INT-02 として分離する。`fetch-source-video` / GUI fetch button / render / encode はまだ未実装。

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
