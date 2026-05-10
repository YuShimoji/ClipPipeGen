# Preview Pack — SH-05

SH-05 はローカル media file 1本から、制作判断に必要な artifact preview を 1 command で生成する slice。

ここでの preview は **rendered video preview ではない**。`preview_manifest.json` と `preview_report.html` による read-only review surface であり、動画生成、cut / concat、字幕焼き込み、render / encode、creative acceptance は扱わない。

## Command

```powershell
uvx python -m src.cli.main build-local-preview-pack `
  --episode-id <episode_id> `
  --local-media <path-to-local-media> `
  --material-id <material_id>
```

任意:

- `--root episodes`
- `--transcript-fixture <segments.json>`
- `--language ja`
- `--force`

`--local-media` と `--transcript-fixture` は local file のみを受け付ける。`://` を含む URL / VOD / network-like locator は拒否する。

## Boundary

| 層 | やる | やらない |
|---|---|---|
| `build-local-preview-pack` | 既存 CLI contract を順に接続し、manifest/report を生成する | FFmpeg / yt-dlp を直接呼ぶ、network fetch、render / encode、GUI action 追加 |
| `fetch-source-audio --mode local-media-audio` | local media を `source.wav` に正規化する | cut / context / subtitle / report を扱う |
| `transcribe-audio --engine fake` | local `source.wav` と fixture segments から `transcript.json` を作る | URL / VOD 取得、実 STT acceptance |
| Editing CLI | transcript から cut / context / subtitle artifact を作る | media tool 実行、動画出力 |
| HTML report | artifact を read-only 表示する | 実行 button、GUI fetch、編集確定、creative acceptance |

FFmpeg の実行責務は INT-02c と同じく `src/integrations/asset_fetch/` の内側に閉じる。SH-05 は `fetch-source-audio --mode local-media-audio` の既存経路を利用するだけで、orchestrator / pipeline / GUI / STT / Editing から FFmpeg を直接呼ばない。

## Artifact Layout

```text
episodes/<episode_id>/
  rights_manifest.json
  material_ledger.json
  edit_pack.json
  transcript.json
  preview_manifest.json
  preview_report.html
  materials/<material_id>/
    source.wav
    sidecar.json
    fetch_receipt.json
  _preview_pack/
    deterministic_fake_segments.json   # fixture 未指定時のみ
```

既存 episode がなければ、`rights_manifest.json` は skeleton / pending として作成する。rights status は report に readback するだけで hard gate にしない。

## Manifest

`preview_manifest.json` の最小項目:

```json
{
  "schema_version": "v1",
  "episode_id": "episode_001",
  "created_at": "2026-05-11T00:00:00+00:00",
  "input": {
    "kind": "local_media_file",
    "path": "_tmp/input.wav"
  },
  "material": {
    "material_id": "src_audio_001",
    "source_wav": "episodes/episode_001/materials/src_audio_001/source.wav",
    "fetch_receipt": "episodes/episode_001/materials/src_audio_001/fetch_receipt.json"
  },
  "transcript": {
    "source": "deterministic_fake",
    "path": "episodes/episode_001/transcript.json",
    "segment_count": 1,
    "not_for_acceptance": true
  },
  "cuts": {
    "path": "episodes/episode_001/edit_pack.json",
    "candidate_count": 1,
    "context_counts": {
      "passed": 1,
      "needs_review": 0,
      "failed": 0,
      "not_checked": 0
    }
  },
  "subtitles": {
    "path": "episodes/episode_001/edit_pack.json",
    "subtitle_count": 1
  },
  "report": {
    "path": "episodes/episode_001/preview_report.html"
  },
  "warnings": [
    "transcript source is deterministic_fake; transcript.not_for_acceptance is true",
    "rights status is pending; this is readback only"
  ],
  "next_actions": [
    "Review preview_report.html before moving to external acquisition or output work.",
    "Replace fake or fixture transcript with reviewed transcript before acceptance.",
    "Keep source acquisition, output generation, and GUI execution as separate slices."
  ]
}
```

## Report

`preview_report.html` は read-only HTML。表示する内容:

| Section | 内容 |
|---|---|
| Episode | episode id、入力 local media、material id、rights status、provider |
| Material Audio | `source.wav` link と `<audio controls>` |
| Transcript | source 種別、segment 数、先頭 segments |
| Cut Candidates | cut id、start/end、score、context status、reason |
| Subtitle Draft | subtitle id、cut id、start/end、text |
| Warnings | rights pending、fake / fixture transcript、candidate/subtitle 欠落 |
| Next Actions | 次に人間が確認すべき操作 |

HTML report は GUI の代替実装ではない。実行 button、fetch button、編集確定 button は置かない。

### SH-05b Report QA / Polish

SH-05b では、report が「存在する」だけではなく operator が制作判断面として読めることを確認し、表示だけを小さく磨いた。機能追加、GUI ingest、rendered video preview、network fetch は含めない。

追加・確認した表示:

| 表示 | 目的 |
|---|---|
| Status Summary | `Transcript source`、`Not for acceptance`、`Rights status`、`Read-only artifact preview` を冒頭で確認する |
| Decision Warnings | fake / fixture transcript が acceptance material ではないこと、rights pending が readback only であることを warning list から独立して表示する |
| Artifact Links | `source.wav`、`preview_manifest.json`、`fetch_receipt.json`、`transcript.json`、`edit_pack.json` への read-only link をまとめる |
| Audio controls | `source.wav` の read-only 確認用。動画 preview ではない |
| Japanese text wrapping | 日本語 fixture transcript / subtitle draft が table cell 内で読めるように最小調整する |

QA smoke は ignored scratch の `episodes/sh05b_fixture_smoke_ja` と `_tmp/sh05b_fixture_smoke_ja` で実施した。Python `wave` で作成した 44.1kHz / stereo / 16-bit / 3.0秒の local WAV を入力し、短い日本語 fixture transcript を `--transcript-fixture` として渡した。

実測 readback:

- `transcript.source=fixture`
- `transcript.not_for_acceptance=true`
- `candidate_count=1`
- `subtitle_count=2`
- `source.wav` は mono / 16kHz / 16-bit / 3.0秒
- HTML は Status Summary / Decision Warnings / Artifact Links / audio controls / manifest link / receipt link を含む
- HTML は `<button>` / `<form>` / `<video>` を含まない

画面確認は `file://` 直開きがブラウザ安全ポリシーで扱いづらいため、`localhost` の静的サーバー経由で `preview_report.html` を開き、DOM readback を証跡とした。DOM readback では日本語 fixture text、not-for-acceptance 表示、rights pending readback、manifest / receipt link、audio controls が確認できた。

### SH-05b+ Visual Evidence Hardening

SH-05b+ では、DOM readback だけではなく実画面として `preview_report.html` が operator-visible な制作判断面になっていることを確認した。これは GUI ingest ではなく、HTML report の visual evidence hardening である。

追加・確認した項目:

| 項目 | 結果 |
|---|---|
| medium Japanese fixture | 4 segments の日本語 fixture transcript で `build-local-preview-pack` を fresh episode / `--force` なしで実行 |
| visual evidence | `localhost` 静的配信で report を開き、visible screenshot と full-page screenshot を ignored scratch に保存 |
| manifest validation | `validate_preview_manifest` の lightweight schema check を追加し、smoke manifest は issues `[]` |
| report visibility | Status Summary、Decision Warnings、Artifact Links、Material Audio が実画面上で確認可能 |
| warnings | `fixture transcript is not acceptance material`、`transcript.not_for_acceptance is true`、`rights pending is readback only` が上部 warning panel に表示 |
| links / audio | `preview_manifest.json`、`fetch_receipt.json`、`source.wav` link と audio controls を確認 |
| forbidden surface | `<button>` / `<form>` / `<video>` はなし |

実測 readback:

- episode: `episodes/sh05b_visual_evidence_medium_ja_ok`（ignored scratch）
- source fixture: `_tmp/sh05b_visual_evidence_medium_ja_ok/input_44100_stereo.wav`（Python `wave` で生成）
- visual evidence: `_tmp/sh05b_visual_evidence_medium_ja_ok/preview_report_visible_viewport.png`
- `source.wav` は mono / 16kHz / 16-bit / 8.0秒
- `transcript.source=fixture`
- `transcript.not_for_acceptance=true`
- `segment_count=4`
- `candidate_count=1`
- `context_counts.passed=1`
- `subtitle_count=4`
- `preview_manifest` validation issues: `[]`

SH-05b+ でも、yt-dlp / network fetch / `fetch-source-video` / GUI fetch button / GUI からの build-local-preview-pack 実行 / render / encode / creative acceptance は扱わない。

### SH-05c GUI Read-Only Ingest

SH-05c adds a GUI read-only ingest surface for preview packs. It does not generate a preview pack and does not run fetch, build, render, upload, or external acquisition workflows.

GUI behavior:

| Area | Readback |
|---|---|
| Input | Existing episode directory or `preview_manifest.json` path |
| Validation | Lightweight `preview_manifest.json` schema validation; missing / invalid / artifact missing are shown as warning states |
| Status Summary | `episode_id`, input kind/path, material id, transcript source, `not_for_acceptance`, segment count, cut candidate count, context counts, subtitle count, report path |
| Decision Warnings | Manifest warnings plus explicit not-for-acceptance and rights-readback-only messages |
| Artifact Links | `preview_manifest.json`, `preview_report.html`, `source.wav`, `fetch_receipt.json`, `transcript.json`, `edit_pack.json` as local read-only links |

Visual evidence was captured from the GUI Preview Pack tab against the SH-05b smoke episode `episodes/sh05b_visual_evidence_medium_ja_ok`:

- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_tab.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_artifacts.png`
- `_tmp/sh05c_gui_visual_evidence/gui_preview_readback.json`

Readback result:

- `state=ready`
- `validation_issues=0`
- `transcript.source=fixture`
- `transcript.not_for_acceptance=true`
- `cut_candidate_count=1`
- `subtitle_count=4`
- artifact links 6件 all `exists`
- Preview Pack panel has no form/button execution controls

SH-05c keeps the SH-05 boundary: no yt-dlp, network fetch, `fetch-source-video`, GUI fetch button, GUI-triggered `build-local-preview-pack`, rendered video preview, cut / concat, subtitle burn-in, render / encode, creative acceptance, or rights hard gate.

## Fake Transcript

`--transcript-fixture` 未指定時は deterministic fake segments を `episodes/<episode_id>/_preview_pack/deterministic_fake_segments.json` に生成し、既存 `transcribe-audio --engine fake` に渡す。

fixture 指定時も `transcribe-audio --engine fake` を使うため、`preview_manifest.json` では `transcript.not_for_acceptance=true` を維持する。これは接続確認用であり、creative acceptance、字幕品質 acceptance、公開判断の根拠にはしない。

## Remaining Out Of Scope

- `yt-dlp-audio` actual implementation
- network fetch
- `fetch-source-video`
- GUI fetch button
- rendered video preview
- cut / concat
- subtitle burn-in
- render / encode
- creative acceptance
