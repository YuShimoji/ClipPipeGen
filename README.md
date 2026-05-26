# ClipPipeGen

ED-09 note: transcript review / correction workflow is now implemented. Use `review-transcript --transcript <path> --patch <path> [--reviewed-by <id>] [--dry-run] [--format json]` to apply v1 correction patches to `transcript.json`; it updates only segment text, review status, notes, and top-level review fields. `status-episode` now shows transcript review counts, and `export-nle` reports transcript review state instead of assuming every real STT transcript is unreviewed. Transcript approval is still not edit/render/publish acceptance.

JP-Pilot-01 / 01R note: ED-07c 後の日本語 public VOD diagnostic として、assistant 自律選定 URL <https://www.youtube.com/watch?v=7J5aS_pcBj4>（公式 hololive short anime `【アニメ】押忍！！ば～んちょ だじぇ！`）で URL → source_video / source_audio → Vosk JP transcript → edit_pack → subtitles → diagnostic burn-in render → NLE CSV → ledger audit まで完走。ED-09 後の JP-Pilot-01R では公式 Japanese subtitle track を照合材料に 7 segments を accepted にし、補正済み transcript から 5 cuts、26 subtitle drafts、NLE CSV 5 rows、default/focus diagnostic render を再生成した。詳細は [docs/JP_PILOT.md](docs/JP_PILOT.md)。

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

**Slice 1 ソフト実装は done**（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）。Slice 2 / Phase 1.5 では、source audio / source video 取得、real STT transcript、cut / context / subtitle draft、NLE CSV export、diagnostic render、real transcript subtitle burn-in、JP-STT-01 / HoloEN-01 / JP-Pilot-01 の実素材 pilot、ED-09 transcript review / correction workflow、JP-Pilot-01R corrected rerun まで実装済み。

現在の中核パイプラインは `source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles -> diagnostic render -> NLE CSV` まで通る。`review-transcript` は補正済み transcript を既存 downstream に戻す入口であり、transcript approval は edit / render / publish / production acceptance ではない。

GUI fetch/render button、production render、production subtitle design、FCPXML / Resolve XML、STT 品質 acceptance、GUI transcript correction surface、Publishing / OAuth はまだ未実装。次の推奨は JP-Pilot review coverage + selected cut narrowing、official subtitle track import / transcript alignment、または公式字幕がない素材向けの STT provider comparison。

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
