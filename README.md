# ClipPipeGen

> **Current development state:** use
> [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) as the current-state source.
> OUT-02 is the tracked synthetic output-proof baseline; real local proof,
> production acceptance, rights approval, and public readiness remain separate
> states unless the Runtime capsule records a later reviewed transition.

OUT-08 note: authoritative episode evidence の未使用範囲から、重複しない 2 本の
実尺 vertical Shorts 候補を 1 回の atomic render で生成し、単一列の localhost
review page に束ねた。candidate 02 は reject 済み `cut_009` の source-time
interval を完全除外した。これは同一マシン内の internal review artifact であり、
navigation frame は thumbnail ではない。人間の候補判断、rights、production、
publishing の gate は未承認のまま保持する。

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

**Slice 1 ソフト実装は done**（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）。Slice 2 / Phase 1.5 では、source audio / source video 取得、real STT transcript、cut / context / subtitle draft、NLE CSV export、diagnostic render、real transcript subtitle burn-in、JP-STT-01 / HoloEN-01 / JP-Pilot-01 の実素材 pilot、ED-09 transcript review / correction workflow、ED-10 official subtitle track import、JP-Pilot-01R corrected rerun、JP-Pilot-01R2 review coverage + cut narrowing、JP-Pilot-01R3 official-caption rerun まで実装済み。

現在の中核パイプラインは `source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles -> diagnostic render -> NLE CSV` まで通る。`review-transcript` は補正済み transcript を既存 downstream に戻す入口であり、transcript approval は edit / render / publish / production acceptance ではない。

GUI fetch/render button、production render、production subtitle design、FCPXML / Resolve XML、STT 品質 acceptance、GUI transcript correction surface、Publishing / OAuth はまだ未実装。次の推奨は JP-Pilot R3 の current reviewability/readback を parser-first で確認し、代表字幕デザイン review、final render-path output review、editorial representative-sequence review、rights/material-use clearance のどれか 1 つを narrow slice として選ぶこと。公式字幕が無い素材を優先する場合は STT provider comparison を先に切る。

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
