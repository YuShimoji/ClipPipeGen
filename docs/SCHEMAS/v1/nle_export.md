# nle_export artifacts (ED-06)

ED-06 は `edit_pack.json` を ClipPipeGen の内側で止めず、外部編集ソフトへ渡せる最小 artifact に変換する slice。現時点の出口は **CSV cut list + JSON/HTML readback** であり、FCPXML / Resolve XML / render / encode は扱わない。

この export は production edit acceptance ではない。fake / fixture transcript 由来の `edit_pack` から生成された場合は、CSV・manifest・HTML report のすべてで preview-only / not production candidate の warning を保持する。

## 生成ファイル

既定の出力先は `episodes/<episode_id>/exports/ed06/`。

| ファイル | 目的 | 外部編集への使い方 |
|---|---|---|
| `nle_cut_list.csv` | cut range / title / subtitle / source refs を human-readable に渡す | NLE 側で手動 import / spreadsheet review / EDL 化の前段として使う |
| `nle_export_manifest.json` | export の readback。入力・出力 path、source audio provenance、warnings を保持する | operator / CI が生成物と production warning を確認する |
| `nle_export_report.html` | export path と provenance を人間が読む小さな report | source URL / provider / hash / rights snapshot / warning を確認する |

## CSV columns

| column | 内容 |
|---|---|
| `episode_id` / `cut_id` / `selected` | episode と採用 cut の readback。`selected_cut_ids` が空なら全候補を review 用に出す |
| `title` / `reason` | NLE 上で見つけやすい説明。優先順は cut reason、`editing_intent.topic`、cut id |
| `start_seconds` / `end_seconds` / `duration_seconds` | 元 source 上の秒数。フレーム精度変換は後続 NLE/XML slice に残す |
| `source` / `confidence` / `context_status` / `source_segment_ids` | ED-02 / ED-03 の判断 readback |
| `subtitle_ids` / `subtitle_text` / `subtitle_ranges` | ED-04 の subtitle draft。burn-in ではない |
| `source_audio_material_id` / `source_audio_path` / `source_audio_provider` / `source_audio_mode` / `source_url` / `source_audio_sha256` | SH-05d preview manifest または material ledger から解決した source audio provenance |
| `production_edit_candidate` / `warnings` | 常に `false`。fake / fixture transcript、未承認 review、未選択 cut などを明示する |

## CLI

```powershell
python -m src.cli.main export-nle `
  --edit-pack episodes/ep_x/edit_pack.json `
  --preview-manifest episodes/ep_x/preview_manifest.json `
  --output-dir episodes/ep_x/exports/ed06
```

`--preview-manifest` を省略した場合は、`edit_pack.json` と同じ episode directory の `preview_manifest.json` を自動参照する。manifest が無い場合でも `material_ledger_path` から可能な範囲で `source_audio` entry を readback する。

JSON readback が必要な場合:

```powershell
python -m src.cli.main export-nle `
  --edit-pack episodes/ep_x/edit_pack.json `
  --format json
```

## 境界

- ED-06 は CSV cut list / manifest / HTML readback だけを生成する。
- ED-06 は real STT、source-video acquisition、render、encode、subtitle burn-in、GUI export button、publishing を実装しない。
- `source_audio_provenance` は readback であり、rights hard gate ではない。
- fake / fixture transcript 由来の export は preview-only。外部編集ソフトへ渡せるが、production edit candidate とは呼ばない。
