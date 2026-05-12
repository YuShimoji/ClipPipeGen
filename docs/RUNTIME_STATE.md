# Runtime State — ClipPipeGen

ブロックの主成果と次の手を更新する。compact 後の再アンカリングではこのファイルを読む。

## 現在位置

### Slice 1.3 done（TH-01 / SH-01: NLMYTGen bridge + thumbnail patch orchestrator）

- Slice 1 ソフトウェア実装は **6/6 done**（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）
- 累計テスト 31 件 all passing。NLMYTGen subprocess は monkeypatch でモック。
- **実装内容**：
  - `src/pipeline/nlmytgen_bridge.py` — `BridgeConfig.load` / `call_nlmytgen` (silent fallback 禁止) / `audit_thumbnail_template` / `patch_thumbnail_template`
  - `src/pipeline/thumbnail_patch.py` — TH-01 オーケストレータ：(1) rights readback (2) material validation (3) NLMYTGen audit (4) NLMYTGen patch (5) readback
  - `src/cli/{audit_thumbnail,patch_thumbnail}.py`
  - `config/nlmytgen_path.json.example`（本体は `.gitignore` 対象）
  - `tests/test_thumbnail_patch.py` — 8 件（bridge 3 + orchestrator 4 + input validator 1）
- **保留中**：実 YMM4 base template `.ymmp`（`thumb.text.*` / `thumb.image.*` Remark 設定済み）に対する end-to-end walkthrough。これは user-owned acceptance step として `FIRST_SLICE.md` DoR に既に記載されている。テンプレ authoring は人手作業のため、ソフト側の DoD は閉じてよい。

### Slice 1.2 done（MS-01 / MS-02 / MS-03: material_ledger + sidecar + 透過PNG 受け入れ）

- Bootstrap commit `d5efd86`、CR-01 commit `5be5439`、Slice 1.2 commit は本ブロック内
- Slice 1 done 状態: `CR-01 / MS-01 / MS-02 / MS-03` (4/6)。残り `TH-01` / `SH-01` は Slice 1.3 で実装
- **Slice 1.2 実装内容**：
  - `src/pipeline/validation.py` — 共有 `ValidationIssue`（CR-01 の dataclass を抽出）
  - `src/pipeline/material_sidecar.py` — schema validator / source-license-restriction metadata readback
  - `src/pipeline/material_ledger.py` — `build_skeleton` / `register_material` / `audit_ledger` / `is_transparent_png` (MS-03) / material resolution
  - `src/cli/{register_material,audit_material_ledger}.py`
  - `tests/test_material_sidecar.py` — 6 tests（positive 1 + critical negatives 5）
  - `tests/test_material_ledger.py` — 8 tests（PNG 判定 2 + register 3 + audit 2 + CLI smoke 1）
- 累計テスト: 23 件 all passing
- readback 方針：
  - sidecar の `source.kind=unverified` / `license.kind in {unknown,fair_use_claimed}` / `restrictions.thumbnail_use=denied` は metadata として保持し、thumbnail 実行は止めない
  - `register-material` で sidecar hash 不一致 / 透過PNG 宣言 vs 実 RGB の不整合 / sidecar 構造違反は `LedgerError`
  - `audit-material-ledger` は hash mismatch / sidecar schema / file resolution を検出

### project

- name: ClipPipeGen
- repo: https://github.com/YuShimoji/ClipPipeGen
- 並列ローカルパス: `c:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`
- 関連リポ: [NLMYTGen](https://github.com/YuShimoji/NLMYTGen)（CLI subprocess 経由でのみ再利用）

### lane / slice

- **current_lane**: Slice 2 — TH-W01 / SH-04 / SH-03b / SH-03c / SH-05 / SH-05b / SH-05b+ / SH-05c / SH-05d / ED-01 / ED-02 / ED-02a / ED-03 / ED-04 / ED-05 / ED-06 / ED-07 / ED-07b / INT-02a / INT-02b / INT-02c / INT-02d / INT-02e / INT-02f / OUT-01 / OUT-01a done。samples runnable
- **current_slice**: Slice 2 — OUT-01a `render preflight / fallback readback` is implemented。`render-tiny-proof` は source_video material、source_audio material、edit_pack の selected cut から diagnostic `rendered_video.*` を再生成しつつ、FFmpeg/FFprobe preflight、selected render profile、attempted profiles、fallback reason、failure classification を `render_receipt.json` / `render_manifest.json` / `render_report.html` に残す。これは production render / creative / publish acceptance ではなく、subtitle burn-in も行わない
- **next_action（assistant 側）**: OUT-01a が安定したため、次は longer local video render smoke と subtitle burn-in diagnostic を比較する。codec/container failure が多い場合だけ render profile matrix を最小追加し、duration/clamp が問題なら longer local source video smoke を優先する。source video の取得元が問題でも、まず local video smoke を長尺化してから URL video acquisition を検討する

### Slice 2 (xxiv) OUT-01a done（render preflight / fallback readback）
- `src/integrations/render/ffmpeg_tiny.py` — render 前に FFmpeg / FFprobe discovery と `-version` preflight を行い、`environment_missing_ffmpeg` / `environment_missing_ffprobe` を分類する。auto profile は `mp4/libx264/aac` を第一候補とし、同 container の codec fallback と `mkv` fallback 候補を command plan に残す
- Failure classification — render attempt ごとに `status`、`profile`、`failure_reason`、stderr digest を保存。分類は `codec_or_container_unsupported`、`input_stream_invalid`、`ffmpeg_command_failed`、`metadata_probe_failed`、`input_video_missing`、`input_audio_missing`、`duration_or_timeline_mismatch`、`code_bug_or_unexpected_exception` を扱う
- `src/cli/render_tiny_proof.py` — success / failure とも receipt / manifest / report に selected profile、attempted profiles、fallback_used、tool preflight、failure_classification を write back する。失敗時も context 解決後なら `render_receipt.json` / `render_manifest.json` / `render_report.html` を残す
- Smoke readback — ignored `episodes/out01a_hardened_smoke_20260513` で synthetic local media を source video / source audio に登録し、manual selected cut から `renders/out01a_hardened/rendered_video.mp4` を再生成。metadata は duration `2.0`、container `mov,mp4,m4a,3gp,3g2,mj2`、video codec `h264`、audio codec `aac`、resolution `160x90`、fps `15.0`、stream count `2`
- Boundary — OUT-01a は diagnostic render subsystem hardening であり、production render、creative edit acceptance、publishing、subtitle burn-in、font/safe-area polish、GUI render button、URL video fetch、FCPXML / Resolve XML には進んでいない。`production_candidate=false` のまま扱う
- Assistant-side validation — targeted OUT-01a render hardening tests、tiny render tests、source-video acquisition tests、ED-07b transcript tests、ED-06 export tests、`uvx pytest -q`、`npm run smoke`、`npm run smoke:electron`、`git diff --check` を通過

### Slice 2 (xxiii) OUT-01 done（tiny render proof）
- `src/integrations/render/ffmpeg_tiny.py` — render 専用 FFmpeg/FFprobe adapter を追加。source video + source audio の単一 cut range を mp4/mkv に出力し、output duration / container / video codec / audio codec / resolution / fps / stream count を FFprobe で readback する。STT / Editing / GUI / asset_fetch には FFmpeg render を混ぜない
- `src/cli/render_tiny_proof.py` — `render-tiny-proof --source-video-material-id ... --source-audio-material-id ... --edit-pack-path ... --output-id ...` を追加。material_ledger / sidecar / fetch_receipt / transcript sibling を readback し、`renders/<output_id>/rendered_video.<ext>`、`render_receipt.json`、`render_manifest.json`、`render_report.html` を作る
- Timeline policy — 最初の selected cut を source video / source audio timeline に対応させ、source video/audio duration や `--duration-sec` を超える場合は shortest input に clamp する。loop / speed change / complex concat / subtitle burn-in は行わず、clamp / duration mismatch / diagnostic render warning を manifest/receipt/report に残す
- Smoke readback — ignored `episodes/ed07b_real_stt_smoke_20260512` に `src_video_out01_smoke` を追加し、既存 real STT 由来 `edit_pack.json` と `src_audio_real_stt_smoke/source.wav` から `renders/out01_tiny_render_smoke/rendered_video.mp4` を生成。output metadata は duration `1.11`、container `mov,mp4,m4a,3gp,3g2,mj2`、video codec `h264`、audio codec `aac`、resolution `160x90`、fps `15.0`、stream count `2`
- Boundary — OUT-01 は rendered artifact plumbing proof であり、production render、creative edit acceptance、publishing、subtitle burn-in、GUI render button、URL video fetch、FCPXML / Resolve XML には進んでいない。`production_candidate=false` のまま扱う
- Assistant-side validation — targeted OUT-01 render tests、source-video acquisition tests、ED-07b transcript tests、ED-06 export tests、`uvx pytest -q`（140 passed）、`npm run smoke`、`npm run smoke:electron`、`git diff --check` を通過

### Slice 2 (xxii) INT-02f done（local source video acquisition）

- `src/integrations/asset_fetch/source_video.py` — local source video adapter を追加。`source_video.<ext>` へコピーし、FFprobe で duration / container / video codec / audio codec / resolution / fps / stream count を JSON readback する。FFprobe discovery は `--ffprobe-path` → `CLIPPIPE_FFPROBE` → PATH。render / encode / cut / concat は行わない
- `src/cli/fetch_source_video.py` — `fetch-source-video --mode local-media-video` を追加。`--source-path`（`--local-media` alias）を受け、episode 配下に `source_video.<ext>` / `sidecar.json` / `fetch_receipt.json` / `material_ledger.json` entry を作る。`--dry-run` は copy / probe subprocess を呼ばず command plan と output contract を返す
- `material_ledger` — `intended_uses` に `editing_video` を追加。source video entry は `kind="source_video"` / `subkind="source_video_original"` / `intended_uses=["editing_video"]`
- Smoke readback — ignored `episodes/int02f_source_video_smoke_20260512` で local fixture `input_source_video.mkv` を `src_video_local_smoke` として登録。`source_video.mkv`、`fetch_receipt.json`、`sidecar.json`、`material_ledger.json` entry を生成し、`audit-material-ledger --format json` は `ok=true`
- Metadata readback — duration `1.2` 秒、container `matroska,webm`、video codec `mpeg4`、audio codec `null`（音声 stream なし）、resolution `160x90`、fps `15.0`、stream count `1`
- Assistant-side validation — targeted source-video acquisition / material ledger / source-audio / transcript / ED-06 export tests、`uvx pytest -q`（136 passed）、`npm run smoke`、`npm run smoke:electron`、`git diff --check` を通過
- Boundary — URL video fetch、yt-dlp-video、render / encode、cut / concat、subtitle burn-in、GUI fetch button、publishing、creative acceptance は追加していない。rights は `pending` snapshot と warning を保持し hard gate にしない

### Slice 2 (xxi) ED-07b done（real STT transcript path）

- `src/integrations/stt/vosk_adapter.py` — optional Vosk adapter を追加。provider は repo dependency にせず、`uvx --with vosk ...` など実行環境側で解決する。`preflight_vosk` は provider importability、model directory、mono 16-bit PCM WAV を確認し、欠落時は fixture fallback せず明示 failure にする
- `src/cli/transcribe_audio.py` — `--engine fake` に加えて `--engine vosk --model <path>` を実装。`--source-audio-path` alias、`--dry-run`、`--format json`、`--provider` alias、`--force` を追加し、`material_ledger` / `material_id` link と source audio hash / duration / sample rate / channels を readback する
- `src/pipeline/transcript.py` — `stt.provider`、`stt.real_transcript`、`stt.segment_count`、top-level `segment_count` を保存。real STT 由来の transcript は `real_transcript=true`、fake / fixture は false のまま
- `src/pipeline/nle_export.py` / `src/cli/export_nle.py` — explicit または sibling `transcript.json` を読み、CSV / manifest / report に transcript provider、engine、model、real flag、segment count、duration を出す。material ledger fallback では sidecar / sibling receipt も見て source audio provider / mode / hash を補う
- Smoke readback — ignored `episodes/ed07b_real_stt_smoke_20260512` で Windows TTS 生成の `source.wav` を Vosk model `_tmp/stt_models/vosk-model-small-en-us-0.15` に通し、`transcript.json`（1 segment / 9.45 秒 / `real_transcript=true`）を生成。そこから 1 cut、context passed、1 subtitle、ED-06 `nle_cut_list.csv` / `nle_export_manifest.json` / `nle_export_report.html` まで通した
- Assistant-side validation — targeted transcript / STT adapter / edit path / ED-06 export tests、`uvx pytest -q`（131 passed）、`npm run smoke`、`npm run smoke:electron`、`git diff --check` を通過
- Boundary — STT 精度評価、話者分離、transcript correction UI、source-video acquisition、render / encode、subtitle burn-in、GUI STT button、GUI export button、publishing は追加していない。real transcript 由来でも `production_edit_candidate=false` のまま、draft / unreviewed として扱う

### Slice 2 (xx) ED-06 done（minimal NLE export）

- `src/pipeline/nle_export.py` — `edit_pack.json` を validate し、`selected_cut_ids` があれば採用 cut の順に、空なら全候補を review 用として `nle_cut_list.csv` に出力する。cut range、duration、title/reason、source_segment_ids、context status、subtitle draft、source audio refs、warning を行ごとに保持する
- `src/cli/export_nle.py` — `export-nle --edit-pack ...` を追加。既定出力は `episodes/<episode_id>/exports/ed06/`、`--preview-manifest` 省略時は episode sibling の `preview_manifest.json` を参照する。`--format json` で CSV / manifest / report path を machine-readable に返す
- Readback artifacts — `nle_export_manifest.json` は input/output path、cut rows、review status、rights/material ledger refs、source audio provenance、`production_edit_candidate=false`、warnings を保持する。`nle_export_report.html` は operator が CSV path、provider、mode、source URL、hash、rights snapshot、warning を読める小さな report
- Boundary — 現行の external editor handoff は CSV cut list。FCPXML / Resolve XML、real STT、source-video acquisition、render / encode、subtitle burn-in、GUI export button、publishing は追加していない
- Assistant-side validation — `tests/test_nle_export.py` で selected cut の CSV export、未選択時の全候補 review export、CLI JSON readback、source audio provenance、fixture transcript warning、production candidate false を確認。ignored `episodes/ed06_export_smoke_20260512` で preview pack 由来 edit_pack から実 export path / report warning を readback

### Slice 2 (xix) SH-05d done（source-audio preview bridge）

- `src/cli/build_local_preview_pack.py` — `--use-existing-source-audio` を追加。既存 episode の `material_ledger.json` から `source_audio` entry を参照し、`source.wav` / `sidecar.json` / 同ディレクトリの `fetch_receipt.json` を検出する。existing mode では `fetch-source-audio` を呼ばない
- `src/pipeline/preview_pack.py` — manifest に `material.sidecar` / `material.material_ledger` / `material.ledger_entry` / `source_audio_provenance` を追加。report に `Source Audio Provenance` section を追加し、receipt mode/provider/command/source URL/local path/tool versions/rights snapshot/intermediate retention/hash を readback する
- `gui/preview_reader.cjs` — read-only ingest が `existing_source_audio_material` input kind と sidecar / material ledger links を validate / artifact readback できるように更新。GUI fetch button や GUI からの build 実行は追加していない
- Production warning — fake/fixture transcript と生成 edit_pack は production candidate ではないことを Decision Warnings / warnings / next actions に明示
- Assistant-side validation — targeted preview-pack tests で existing source audio mode が `fetch-source-audio` を呼ばず、既存 source audio artifacts を manifest/report に接続することを確認。ignored `episodes/sh05d_existing_source_audio_smoke_20260512` で reproducible smoke episode を作成し、`preview_manifest.json` の `source_audio_provenance` / sidecar / material_ledger / ledger_entry / receipt refs、`preview_report.html` の provider / tool / URL / hash / rights snapshot / production-candidate warning、GUI read-only ingest `state=ready` を readback。real INT-02e artifact smoke は元の ignored episode が無いため pending。ED-06、real STT、render、GUI fetch button、NLMYTGen config、publishing は未着手のまま維持

### Slice 2 (xviii) INT-02e done（yt-dlp-audio source audio URL fetch）

- `src/integrations/asset_fetch/yt_dlp_audio.py` — yt-dlp path discovery（`--yt-dlp-path` → `CLIPPIPE_YTDLP` → PATH）、dry-run-safe plan、yt-dlp version readback、URL download、temporary intermediate selection、existing FFmpeg adapter への normalization handoff、combined stderr digest、failure cleanup を追加
- `src/cli/fetch_source_audio.py` — `--mode yt-dlp-audio` / `--yt-dlp-path` を追加。実行は yt-dlp fetch → FFmpeg normalize → sidecar / receipt / ledger write に限定。dry-run は network / subprocess を呼ばず command plan を返す
- Receipt readback — mode/provider/tools/commands/input/intermediate/output/warnings/stderr digest/rights snapshot/rollback を保存。`intermediate.retained=false`、rights は `hard_gate=false`
- URL scrub — 実行時の URL は yt-dlp に渡すが、preflight / receipt / sidecar / command readback では query / fragment / userinfo / token を scrub する
- Boundary — `fetch-source-video`、GUI fetch button、GUI からの fetch/build/render、`transcribe-audio` URL / VOD fetch、cut / concat、subtitle burn-in、render / encode は追加していない
- Assistant-side validation — fake runner / monkeypatch / dry-run / boundary tests で source audio URL fetch surface を確認
- Real URL operator smoke — `episodes/int02e_operator_smoke_20260512`（ignored）で MDN technical smoke audio URL を `fetch-source-audio --mode yt-dlp-audio` に渡し、yt-dlp `2026.03.17` と実 FFmpeg `ffmpeg version 8.0.1-full_build-www.gyan.dev` による `source.wav`、receipt、sidecar、ledger entry を生成。actual 実行は fresh episode で `--force` なし
- Smoke readback — dry-run は `will_write=false`、`will_call_subprocess=false`、URL query / fragment scrub、conflicts `[]` を確認。actual receipt は provider `yt-dlp`、tools `yt-dlp` / `ffmpeg`、download / normalize command summaries、`intermediate.retained=false`、rights snapshot `pending` / `hard_gate=false`、rollback files を保持。Python `wave` で `source.wav` は mono / 16kHz / 16-bit / 2.07425秒、`audit-material-ledger --format json` は `ok=true`
- Artifact hygiene — smoke artifact は ignored `episodes/` 配下に残し、tracked artifact にはしない

### Slice 2 (xvii) SH-05c done（GUI read-only preview pack ingest）

- GUI surface — `gui/renderer.html` に Preview Pack tab を追加し、既存 episode directory または `preview_manifest.json` を読む read-only panel として Status Summary / Decision Warnings / Artifact Links を表示する
- Preview reader — `gui/preview_reader.cjs` が `preview_manifest.json` の lightweight schema validation を行い、missing / invalid / artifact missing を warning state として返す。GUI から build / fetch / render / upload は実行しない
- Readback fields — `transcript.source`、`transcript.not_for_acceptance`、cut candidate count、context counts、subtitle count、manifest/report/source.wav/fetch_receipt/transcript/edit_pack links を表示する
- Visual evidence — ignored scratch `_tmp/sh05c_gui_visual_evidence/gui_preview_pack_tab.png` と `gui_preview_pack_artifacts.png` で SH-05b smoke episode `episodes/sh05b_visual_evidence_medium_ja_ok` を GUI Preview Pack tab から読めることを確認した。DOM readback は `state=ready`、`validation_issues=0`、artifact links 6件 exists、preview 内 form/button 0件
- Boundary — SH-05c は read-only ingest のみ。yt-dlp、network fetch、`fetch-source-video`、GUI fetch button、GUI からの `build-local-preview-pack` 実行、cut / concat、subtitle burn-in、render / encode、creative acceptance、rights hard gate は未実装のまま

### Slice 2 (xvi) SH-05b+ done（visual evidence hardening）

- `src/pipeline/preview_pack.py` — `validate_preview_manifest` を追加し、`preview_manifest.json` の lightweight schema check を明示。`schema_version`、input/material/transcript/cuts/subtitles/report、warnings、next_actions の最低構造を検査する
- report visual polish — Decision Warnings / Warnings section を `warning-panel` として強調し、not-for-acceptance と rights pending readback が上部で視認しやすい状態にした
- medium Japanese fixture smoke — ignored scratch `episodes/sh05b_visual_evidence_medium_ja_ok` で 4 segments の日本語 fixture transcript を使い、fresh episode / `--force` なしで `build-local-preview-pack` を実行。`source.wav`、`transcript.json`、1 cut candidate、context passed、4 subtitles、`preview_manifest.json`、`preview_report.html` を生成
- manifest / wave readback — `validate_preview_manifest` は issues `[]`。Python `wave` で `source.wav` は mono / 16kHz / 16-bit / 8.0秒。manifest は `transcript.source=fixture`、`not_for_acceptance=true`、`segment_count=4`、`candidate_count=1`、`subtitle_count=4`、rights pending warning を保持
- visual evidence — `localhost` 静的配信で `preview_report.html` を開き、`_tmp/sh05b_visual_evidence_medium_ja_ok/preview_report_visible_viewport.png` と `visual_readback.json` を ignored scratch に保存。画面上で Status Summary、Decision Warnings、Artifact Links、source.wav audio controls、日本語 transcript text を確認
- forbidden surface readback — visual/DOM readback で `<button>` / `<form>` / `<video>` はなし。SH-05b+ では GUI ingest、yt-dlp、network fetch、`fetch-source-video`、render、encode、creative acceptance、rights hard gate は未実装のまま

### Slice 2 (xv) SH-05b done（local-preview-pack report QA / polish）

- `src/pipeline/preview_pack.py` — `preview_report.html` 冒頭に Status Summary、Decision Warnings、Artifact Links を追加。`Transcript source`、`Not for acceptance`、`Rights status`、read-only artifact preview であることを一目で読めるようにした
- report links — `source.wav` / `preview_manifest.json` / `fetch_receipt.json` / `transcript.json` / `edit_pack.json` を read-only link として表示。`source.wav` は既存 audio controls で確認できる
- warning visibility — fake / fixture transcript は acceptance material ではないこと、rights pending は readback only で hard gate ではないことを独立 warning として表示
- 日本語 fixture smoke — ignored scratch `episodes/sh05b_fixture_smoke_ja` で Python `wave` 生成の 44.1kHz / stereo / 16-bit / 3.0秒 local WAV と短い日本語 fixture transcript を使い、`build-local-preview-pack` を fresh episode / `--force` なしで実行。`transcript.source=fixture`、`not_for_acceptance=true`、1 cut candidate、2 subtitles、rights pending warning、manifest / receipt links を確認
- independent readback — Python `wave` で `source.wav` が mono / 16kHz / 16-bit / 3.0秒であることを確認。HTML static readback は Status Summary / Decision Warnings / Artifact Links / audio controls / 日本語 transcript text を含み、`<button>` / `<form>` / `<video>` を含まない
- browser evidence — `file://` 直開きではなく `localhost` 静的サーバー経由で `preview_report.html` を開き、DOM readback で日本語 fixture text、not-for-acceptance、rights readback、manifest / receipt link、audio controls を確認
- 境界維持 — SH-05b は HTML report QA / polish のみ。yt-dlp / network fetch / `fetch-source-video` / GUI fetch button / cut / concat / subtitle burn-in / render / encode / creative acceptance は未実装のまま

### Slice 2 (xiv) SH-05 done（local-preview-pack orchestrator）

- `src/cli/build_local_preview_pack.py` — `build-local-preview-pack --episode-id ... --local-media ... --material-id ...` を追加。入力は local media file のみで、URL / VOD / network-like locator は拒否する
- 1 command flow — episode 未作成時は pending `rights_manifest.json` を skeleton 作成し、既存 `fetch-source-audio --mode local-media-audio`、`transcribe-audio --engine fake`、`generate-cuts`、`check-cut-context`、`generate-subtitles` を順に接続する
- fake / fixture transcript — `--transcript-fixture` 指定時は fixture、未指定時は `episodes/<episode_id>/_preview_pack/deterministic_fake_segments.json` を生成する。どちらも `transcript.not_for_acceptance=true` として preview manifest / report に明示する
- `src/pipeline/preview_pack.py` — `preview_manifest.json` と read-only `preview_report.html` を生成。report は素材、source.wav link / audio controls、receipt、transcript、cut candidates、context status、subtitle draft、warnings、next actions を表示する
- artifact layout — `episodes/<episode_id>/{transcript.json,edit_pack.json,preview_manifest.json,preview_report.html}` と `materials/<material_id>/{source.wav,sidecar.json,fetch_receipt.json}`。smoke 用 episode は ignored scratch の `episodes/` 配下で扱う
- 境界維持 — SH-05 は rendered video preview ではなく artifact preview。yt-dlp / network fetch / `fetch-source-video` / GUI fetch button / cut / concat / subtitle burn-in / render / encode / creative acceptance は未実装のまま
- `tests/test_preview_pack.py` / `tests/test_asset_fetch_boundary.py` — CI は fake fetch monkeypatch で実 FFmpeg に依存しない。URL input 拒否、fixture / deterministic fake、conflict / force、manifest/report、help 上の fetch / output 導線不在を検証
- real local operator smoke — `episodes/sh05_operator_smoke_verify`（ignored）で Python `wave` 生成の 44.1kHz / stereo / 16-bit / 2.0秒 synthetic local WAV を入力し、`build-local-preview-pack` を fresh episode / `--force` なしで実行。実 FFmpeg `ffmpeg version 8.0.1-full_build-www.gyan.dev` は既存 `local-media-audio` 経路でのみ使われ、`source.wav`、deterministic fake `transcript.json`、1 cut candidate、context `passed=1`、1 subtitle、`preview_manifest.json`、`preview_report.html` を生成
- smoke readback — Python `wave` で `source.wav` が mono / 16kHz / 16-bit / 32000 frames / 2.0秒であることを確認。manifest は `transcript.source=deterministic_fake`、`not_for_acceptance=true`、`candidate_count=1`、`subtitle_count=1`、rights pending warning を保持。HTML report は `<audio controls>` あり、実行 button なし。`audit-material-ledger --format json` は `ok=true`
- artifact hygiene — `git status --short` で smoke artifact は tracked に出ない。`git status --short --ignored episodes/sh05_operator_smoke episodes/sh05_operator_smoke_verify _tmp/sh05_operator_smoke` は `!! _tmp/` / `!! episodes/`

### Slice 2 (xiii) INT-02d done（yt-dlp-audio boundary spec only）

### Slice 2 (xiii) INT-02d done（yt-dlp-audio boundary spec only）

- `docs/YTDLP_AUDIO_SPEC.md` — `yt-dlp-audio` を spec only として追加。実装、network fetch、yt-dlp 実行、CLI mode 追加、GUI fetch button は行わない
- URL / network — URL は future `fetch-source-audio --mode yt-dlp-audio` の入力だけに限定。actual network access は future `src/integrations/asset_fetch/` adapter のみ。dry-run は network / subprocess を呼ばない
- yt-dlp / FFmpeg — yt-dlp は元 media の一時取得と provider / extractor / format / warnings readback だけ。FFmpeg は取得 media を `source.wav`（PCM WAV / mono / 16kHz / 16-bit）へ正規化するだけ
- receipt / rollback — future receipt は URL、provider、yt-dlp / FFmpeg versions、commands、outputs、warnings、stderr digest、rollback を持つ。downloaded intermediate は success / failure とも削除し、retained intermediate として ledger 登録しない
- rights / human — rights status は snapshot のみで hard gate にしない。URL 選定、権利・規約 review、公開可否、creative acceptance は人間責務
- GUI / STT — INT-02d では GUI fetch button を追加しない。`transcribe-audio` は生成済みローカル `source.wav` だけを読む。Editing / STT / render / encode / cut / concat へ yt-dlp / FFmpeg を浸透させない

### Slice 2 (xii) INT-02c done（local-media-audio normalize）

- `src/integrations/asset_fetch/ffmpeg_audio.py` — FFmpeg adapter を `asset_fetch` 内に限定して追加。path discovery は `--ffmpeg-path` → `CLIPPIPE_FFMPEG` → PATH、version readback は `ffmpeg -version`、normalize は `-vn -ac 1 -ar 16000 -sample_fmt s16 -acodec pcm_s16le`
- `src/cli/fetch_source_audio.py` — `--mode local-media-audio` / `--local-media` / `--ffmpeg-path` を追加。`--source-url` との併用は拒否し、dry-run は subprocess を呼ばず command plan / paths / conflicts を返す
- receipt readback — provider、tools[].version、commands[].summary / exit_code、input.local_path、outputs、warnings、stderr_digest、rollback を保存。stderr 全文は保存せず secret scrub 後の digest / tail のみにする
- failure policy — version 取得失敗や normalize 失敗時は sidecar / receipt / ledger を書かない。partial `source.wav` は削除する
- 境界維持 — `src/pipeline/*`、`transcribe-audio`、`generate-cuts`、`check-cut-context`、`generate-subtitles`、GUI から FFmpeg / yt-dlp を直接呼ばない。asset_fetch は cut / concat / subtitle burn-in / render / encode / preview / creative acceptance を扱わない
- `tests/test_ffmpeg_audio_adapter.py` / `tests/test_source_audio_fetch.py` / `tests/test_asset_fetch_boundary.py` — fake runner / monkeypatch で CI が実 FFmpeg に依存しないこと、dry-run no subprocess、receipt / rollback、core 侵入防止を検証
- real FFmpeg operator smoke — `episodes/int02c_operator_smoke`（ignored）で 44.1kHz / stereo / 16-bit / 2.0秒の synthetic local WAV を `local-media-audio` に入力し、実 FFmpeg `ffmpeg version 8.0.1-full_build-www.gyan.dev` で `source.wav` を生成。actual 実行は fresh episode で `--force` なし
- independent readback — Python `wave` で実 `source.wav` が mono / 16kHz / 16-bit / 32000 frames / 2.0秒であることを確認。receipt は `provider=local-media`、`commands[0].exit_code=0`、`stderr_digest.algorithm=sha256`、rollback files を保持。ledger audit は `ok=true`、rights snapshot は `pending`
- artifact hygiene — smoke artifact は `episodes/` と `_tmp/` 配下で git ignored。`git status --short` は clean、`git status --short --ignored episodes/int02c_operator_smoke _tmp/int02c_operator_smoke` は `!! _tmp/` / `!! episodes/`
- 実 yt-dlp / network fetch、`fetch-source-video`、GUI fetch button は未実装のまま

### Slice 2 (xi) INT-02b done（asset_fetch boundary spec only）

- `docs/ASSET_FETCH_BOUNDARY.md` — yt-dlp / FFmpeg の責務境界を固定。yt-dlp は URL から元 media を取得するだけ、FFmpeg は source audio を PCM WAV / mono / 16kHz / 16-bit に正規化するだけ
- `fetch-source-audio` future mode contract — 実 mode 追加前に `--dry-run` preflight、receipt、rollback、ledger refresh、failure readback を満たす必要がある
- receipt readback — command、tool versions、provider/engine、input URL/local path、output paths、duration、hashes、warnings、stderr digest、rollback files を必須 readback として仕様化
- core 侵入防止 — `transcribe-audio`、`generate-cuts`、`check-cut-context`、`generate-subtitles`、`src/pipeline/*` は yt-dlp / FFmpeg を直接参照しない。asset_fetch は cut / concat / subtitle burn-in / render / encode / preview / creative acceptance を扱わない
- `tests/test_asset_fetch_boundary.py` — boundary spec の必須文言、fetch CLI が source audio mode のみに閉じていること、pipeline / Editing / STT CLI に yt-dlp / FFmpeg 参照がないことを検証
- 実 yt-dlp 実行、network fetch、`fetch-source-video`、GUI fetch button は未実装のまま

### Slice 2 (x) ED-03 done（transcript context check for cut candidates）

- `src/pipeline/context_check.py` — cut candidate の開始/終了が transcript segment の途中を切っていないか、`source_segment_ids` が transcript と対応しているか、近接する前後 segment があるかを判定。`context_check.status` は `passed` / `needs_review` / `failed`
- `src/cli/check_cut_context.py` — `check-cut-context --transcript ... --edit-pack ...` を追加。`--selected-cuts-only` / `--cut-id` / `--boundary-tolerance-seconds` / `--adjacent-window-seconds` / `--dry-run` / `--format json` を持つ
- `status-episode` / GUI Editing readback — `context_checks.{passed_count,needs_review_count,failed_count,not_checked_count}` を表示。transcript と cut があり未チェックなら `next_action` で ED-03 実行を促す
- `tests/test_context_check.py` — aligned boundary、近接 next segment、発話途中切断、selected scope、unknown cut、CLI roundtrip、dry-run を検証。Python suite は 93 tests pass
- ED-03 は review note の記録であり、動画 preview / NLE export / creative acceptance は行わない。ED-06 / OUT-01 後続

### Slice 2 (ix) ED-02 done（transcript-based cut candidate generation）

- `src/pipeline/cut_generation.py` — transcript segment から contiguous speech island を作り、target duration / gap threshold / max candidates に基づいて `edit_pack.cut_candidates[]` を生成。`source="auto"`、`source_segment_ids`、`context_check.status="not_checked"` を付与
- `src/cli/generate_cuts.py` — `generate-cuts --transcript ... --edit-pack ...` を追加。`--target-duration-seconds` / `--min-duration-seconds` / `--max-duration-seconds` / `--gap-threshold-seconds` / `--max-candidates` / `--select-generated` / `--dry-run` を持つ
- 既存 auto cut は `--replace-auto` 指定時のみ refresh。manual/imported cut は保持する
- `tests/test_cut_generation.py` — window 生成、gap split、replace-auto、select-generated、invalid options、CLI roundtrip、dry-run を検証。Python suite は 86 tests pass
- 文脈妥当性は判定しない。ED-03 で隣接 segment と cut 境界を確認する

### Slice 2 (viii) ED-04 done（subtitle draft generation）

- `src/pipeline/subtitle_generation.py` — `transcript.segments[]` を `edit_pack.subtitles[]` に変換。`source="auto"`、`style_slot`、`source_segment_id` を付与し、既存 auto subtitle は `--replace-auto` 指定時のみ refresh
- `src/cli/generate_subtitles.py` — `generate-subtitles --transcript ... --edit-pack ...` を追加。`--wrap-eaw` で ED-05 の EAW greedy wrap を使い、`--selected-cuts-only` / `--cut-id` で cut 範囲へ絞り込める。`--dry-run` は書き込みなし
- `status-episode` / GUI Editing readback — `subtitles_count` を表示
- `tests/test_subtitle_generation.py` — 全 segment 生成、EAW wrap、selected cut への紐付け、既存 auto subtitle refresh、CLI roundtrip、dry-run、invalid wrap を検証。Python suite は 79 tests pass
- 実 subtitle burn-in、動画レンダリング、GUI action button は未実装。NLE export は ED-06 CSV cut list として実装済みだが、FCPXML / Resolve XML は後続

### Slice 2 (vii) INT-02a done（source audio material contract + fake fetch）

- `src/integrations/asset_fetch/fake_audio.py` — fake downloader として PCM WAV / mono / 16kHz / 16-bit / 1秒 silent fixture を生成。network / yt-dlp / ffmpeg は呼ばない
- `src/cli/fetch_source_audio.py` — `fetch-source-audio --mode fake`。`--dry-run` preflight JSON、既存 artifact / duplicate material ID の衝突検出、`--force` refresh、`rights_manifest` readback、`sidecar.json` / `fetch_receipt.json` / `material_ledger.json` 生成
- `material_ledger` entry — `kind="source_audio"` / `subkind="wav_pcm_16k_mono"` / `intended_uses=["editing_audio"]`。`compliance_link` は `rights_manifest.compliance_check.status` の snapshot
- `sidecar.json` — `source.kind="unverified"` / `source.retrieval_method="asset_fetch_fake"` / `license.kind="unknown"` / `usage_conditions=["source_link_required"]`。restriction は metadata として保持し、local CLI の hard gate にはしない
- `docs/SCHEMAS/v1/fetch_receipt.md` — receipt schema と rollback files contract を追加
- `tests/test_source_audio_fetch.py` — fake fetch roundtrip、dry-run、duplicate refusal、missing rights refusal、force refresh、ED-07 `transcribe-audio` 連携を検証。Python suite は 72 tests pass
- 実 yt-dlp / network fetch、`fetch-source-video`、GUI action button は未実装。親 `INT-02` の後続 slice として扱う

### Slice 2 (vi) ED-07 done（transcript schema + fake transcribe-audio adapter）

- `src/pipeline/transcript.py` — `build_transcript` / `load_transcript` / `save_transcript` / `validate_transcript`。duplicate segment ID、時刻不正、空 text、空 segments の理由なし、approved review 不足を検出
- `src/cli/transcribe_audio.py` — `transcribe-audio --engine fake --fixture-segments ...`。既存ローカル音声ファイルを読み、sha256 と fake STT readback を含む `transcript.json` を生成。URL / VOD は拒否
- `src/cli/validate_transcript.py` — `validate-transcript --transcript ... --format text|json`
- `status-episode` — `artifacts.transcript` と `editing.transcript` readback を追加。transcript missing は manual cut workflow を blocked にしない。invalid transcript は `editing.transcript.state=blocked` として表示
- `tests/test_transcript.py` / `tests/test_episode_status.py` — transcript validator / fake transcribe CLI / status readback。累計 66 tests pass
- 実 `whisper.cpp` binary/model config、INT-02 source fetch、ED-04 subtitle generation は未実装。次 feature として分離したまま

### Slice 2 (iii) ED-05 done（subtitle width measurement, EAW）

- 当初設計は NLMYTGen `text_measure` の CLI bridge だったが、NLMYTGen 側 `text_measure.py` は **class はあるが standalone CLI 無し**（measurement は `build-csv` 内 embed）。bridge 設計が結合できない構造ギャップを発見、**stdlib のみで EAW measurer を ClipPipeGen 側に実装**して閉じた
- `src/pipeline/text_measure.py` — `char_eaw_width` / `text_eaw_width` / `wrap_by_eaw` / `measure_subtitle`。Ambiguous (`A`) は default 1、override 可能。空白あり= word break、CJK = char break
- `src/cli/measure_subtitle_width.py` — `--text` / `--text-file` / `--wrap-eaw` / `--ambiguous-width` / `--format`。`needs_wrap` で exit code 1
- `tests/test_text_measure.py` — 10 件（ASCII / Japanese / mixed / Ambiguous override / wrap below/above / whitespace word break / invalid input / CLI 2 件）
- `docs/proposals/0002-standalone-measure-text-cli.md` — NLMYTGen 側に `measure-text` CLI を追加する逆提案（state=draft）。採用された場合は `ED-05b: text_measure bridge migration` で ClipPipeGen 側を bridge に縮約する
- 既存 Python は 56 件（46 + 新規 10）pass、JS smoke 全通過、`status-episode` 出力は変化なし
- **next_action（user 側）**: SLICE1_WALKTHROUGH.md の Quickstart で `samples/episode_example` を `npm start` 経由で開いてレーン状態を見られる。本走作業として YMM4 thumbnail base template の authoring → `patch-thumbnail` 実走

### Slice 2 (v) sample runnable + (i) Editing GUI tab done

- `samples/episode_example/materials/mat_001/x.png` — 64×64 半透明マゼンタ placeholder（assistant 自作、第三者素材ではない）。`is_transparent_png` pass、SHA256 = `55a8010c754b...`
- `samples/episode_example/{rights_manifest,material_ledger,sidecar,thumbnail_patch_input}.json` の `episode_id` を dir 名 `episode_example` に harmonize（CLI 規約：`--episode-id` == dirname）
- `samples/episode_example/edit_pack.json` を `init-edit-pack` で生成、`cut_001` を `add-cut-candidate --select` で追加
- `.gitignore`: `materials/` を `/materials/`（root 限定）に変更し `!samples/episode_example/materials/` で sample 配下は同梱。これまで `sidecar.json` も silently dropped されていた構造的破綻を修正
- `gui/`: Editing タブ追加。`init-edit-pack` / `add-cut-candidate` / `validate-edit-pack` の action panel + confirm dialog 連動。args builder は `args.cjs` に追加して Electron なし smoke で検証
- `gui/renderer.js`: `renderEditing` 追加、`prefillActionForms` で `epDir` から basename と parent root を分離し ED 系 form に prefill。type=number / checkbox 入力に対応する `optionalFieldsByAction` を導入
- 端まで: `python -m src.cli.main status-episode --episode-dir samples/episode_example --format text` が rights/materials/editing/thumbnail 全 ready、`next[assistant]: Run patch-thumbnail after YMM4 base template is ready` を返す（実コマンド検証）。Python 46 件 pass、JS syntax / smoke 全通過

### Slice 2 (c) Phase 2 done（SH-03b: GUI action 導線）

- `gui/main.cjs` — IPC `action:setCompliance` / `action:registerMaterial` / `action:patchThumbnail` を追加。`safeRunCli` で argv 構築失敗を payload に丸めて renderer に返す
- `gui/args.cjs` — argv builder を Electron 非依存モジュールとして分離。smoke から直接 import 可能
- `gui/preload.cjs` — `setCompliance` / `registerMaterial` / `patchThumbnail` を contextBridge に追加
- `gui/renderer.{html,js}` — Rights / Materials / Thumbnail に action panel を追加。`prefillActionForms` が現在 episode から rights_manifest / episode_id / thumbnail_patch_input / output_result を自動 prefill
- 確認 dialog は単一の `#confirm-modal`。command 文字列 / summary / reason の 3 要素を表示。Esc=Cancel、Enter=Confirm。実行後は `action-result` 領域に exit / stdout tail / stderr tail を表示し、`status-episode` を自動 refresh
- `gui/styles.css` — action panel / form / modal スタイルを追加
- `gui/smoke.cjs` — Phase 2 マーカー（`data-action-form="..."` / `id="confirm-modal"`）の存在チェックと `args.cjs` の builder 検証を追加。Electron なしで完全 pass
- upload / fetch / bg-removal API button は未実装（GUI_CONVENTIONS §5）
- 既存 Python 46 件 pass、JS syntax / smoke 全通過

### Slice 2 (a) Phase 1 done（ED-01 / ED-02a: edit_pack schema + manual cut input）

- `docs/SCHEMAS/v1/edit_pack.md` — cut 候補、選択 cut、字幕案、review 状態の schema を追加。
- `src/pipeline/edit_pack.py` — skeleton / load / save / validator / `add_cut_candidate`。時間範囲、cut/subtitle ID 一意性、選択 cut 参照、subtitle text、review approved 条件を検証。
- `src/cli/{init_edit_pack,validate_edit_pack,add_cut_candidate}.py` — `init-edit-pack` / `validate-edit-pack` / `add-cut-candidate` を追加。
- `src/pipeline/episode_status.py` / `src/cli/status_episode.py` — `edit_pack.json` の存在と schema 状態を status JSON / text に反映。
- `gui/renderer.js` — Episode dashboard に Editing status card を追加。Editing タブは SH-03c で追加。
- 累計テスト 46 件 pass。外部 API・元動画ダウンロード・STT 実行・動画レンダリングは未実装/未実行。STT の artifact 境界は ED-07 `transcript.json` として後続で扱う。

### Slice 2 (c) Phase 1 done（SH-03: GUI MVP read-only console）

- `gui/` Electron skeleton — root `package.json`（Electron `42.0.0`）/ `gui/main.cjs`（IPC `episode:status`）/ `gui/preload.cjs`（contextBridge）/ `gui/{renderer.html,styles.css,renderer.js}`
- 5 タブ MVP — Episode（dashboard table）/ Rights / Materials / Thumbnail（readback table 含む）/ Settings（bridge readiness）
- `status-episode` JSON を spawn 経由で取得（cwd=リポ root）。Python は PATH または `CLIPPIPE_PYTHON` で指定
- `docs/GUI_CONVENTIONS.md` — 整合-A 規約（配色・状態語彙・タブ命名・readback 表示・実行操作・逆提案運用）
- Phase 2 = action 導線は **SH-03b** として proposed に分離。実行系 button は Phase 1 で意図的に出さない
- Python tests は 43 件 pass。GUI 側は `npm run smoke` / `npm run smoke:electron` で最小確認する。Playwright/jest 系は後続スライスで必要になってから判断。
- セキュリティ: `contextIsolation: true` / `nodeIntegration: false` / `sandbox: true` / 厳格 CSP（`default-src 'self'; script-src 'self'`）

### Slice 2 (d) done（TH-W01: Slice 1 walkthrough 補助）

- `docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md` — YMM4 上で `thumb.text.*` / `thumb.image.*` の Remark 規約を持つ base template を作る手順、トラブルシューティング、命名規約 (`^thumb\.(text|image|color|transform)\.[a-z0-9_]+$`)
- `docs/walkthrough/SLICE1_WALKTHROUGH.md` — `init-episode` から `patch-thumbnail` までの 11 ステップ runbook、各段 fail パターンとリトライ手順
- `samples/episode_example/{rights_manifest.json,material_ledger.json,thumbnail_patch_input.json}` と `samples/episode_example/materials/mat_001/sidecar.json` — illustrative example。実素材は未同梱
- 既存テスト 31 件は変更なし。docs only commit。

### Slice 2 (c) approved → done（履歴）

- `docs/GUI_MVP_SCOPE.md` — Electron 採用、MVP タブ（Episode / Rights / Materials / Thumbnail / Settings）、SH-02-lite episode status adapter、未実装 action は disabled button を置かない方針を固定。
- GUI は NLMYTGen とアプリ共有しない。見た目・操作感・タブ構造・readback 表示パターンだけ揃える。
- MVP は当初 Slice 1 artifact の操作面に絞った。Editing タブは SH-03c で追加済。
- Phase 1 実装は本ブロックで完了（上記 Phase 1 done セクション参照）。Phase 2 は SH-03b に分離。

### Slice 2 (c) done（SH-02L: episode status adapter）

- `src/pipeline/episode_status.py` — `rights_manifest` / `material_ledger` / `thumbnail_patch_input` / `thumbnail_patch_result` の存在、readback 状態、bridge config readiness、next_action を集約。
- `src/cli/status_episode.py` — `status-episode --episode-dir ... --format json|text` を追加。
- `tests/test_episode_status.py` — 3 tests。累計 34 tests passing。
- full `episode_pack` は Editing / Publishing 実装後に再評価。

### Slice 2 (c) done（SH-03: Electron GUI MVP skeleton）

- `package.json` — Electron 42.0.0 を dev dependency として定義。
- `gui/` — `main.cjs` / `preload.cjs` / `renderer.html` / `renderer.js` / `styles.css` / `smoke.cjs` を追加。
- MVP は `status-episode` を IPC 経由で呼び、Episode / Rights / Materials / Thumbnail / Settings の状態を表示する。
- GUI から upload / fetch / bg-removal API はまだ実行しない（未実装）。

## 主成果物

- active_artifact: Slice 1 minimum proof（rights_manifest → 透過PNG＋sidecar → YMM4 サムネ slot patch → readback）
- artifact_surface: CLI（`src/cli/*`）→ JSON manifest → patched `.ymmp` → 人手で YMM4 確認・書き出し
- last_change_relation: リポ初期化（v0）

## カウンター

- blocks_since_user_visible_change: 0
- slices_completed: 0

## 次に変えうる判断

- SH-03b/SH-03c は GUI action 導線（init-edit-pack / add-cut-candidate / validate-edit-pack / set-compliance / register-material / patch-thumbnail）。ED-02 / ED-03 / ED-04 の generate/check 系 GUI form、upload / fetch / bg-removal API button は未実装。
- ED-03 は `check-cut-context` と `status-episode` readback まで実装済み。ED-06 で NLE CSV export も実装済み。creative acceptance と動画 preview / render は未実装。
- INT-02a で source audio の fake fetch、INT-02b で yt-dlp / FFmpeg 境界仕様、INT-02c で local-media-audio FFmpeg 正規化と実 FFmpeg operator smoke、INT-02d で `yt-dlp-audio` spec only、INT-02e で source audio URL fetch 限定の実装と real URL operator smoke、INT-02f で local source video acquisition と FFprobe metadata readback、SH-05d で取得済み source audio の preview bridge、ED-06 で minimal NLE CSV export、ED-07b で real STT transcript path、OUT-01 で tiny rendered video proof は完了。次の推奨は render hardening / source-video URL acquisition / subtitle burn-in の優先度比較。ただし GUI button / publishing は別 slice に分ける。
- NLMYTGen CLI bridge が想定通り動作した場合、shared package 化を検討（ただし CLI bridge で 2-3 個の実例が出てから）
- ホロライブ以外の VTuber 事務所（にじさんじ等）への対象拡大は v1 では検討しない。Slice 1 完了後に rights_manifest 構造の汎用性を見て判断する

## 関連ドキュメント

- 入口: [README.md](../README.md) / [AGENTS.md](../AGENTS.md)
- 方針: [CLAUDE.md](../CLAUDE.md)（ルート）
- 再開用引き継ぎ: [HANDOFF.md](HANDOFF.md)
- GUI MVP: [GUI_MVP_SCOPE.md](GUI_MVP_SCOPE.md)
- 不変条件: [INVARIANTS.md](INVARIANTS.md)
- 自動化境界: [AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md)
- レーン責務: [LANES.md](LANES.md)
- 機能一覧: [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
- 現スライス: [FIRST_SLICE.md](FIRST_SLICE.md)
- schema: [SCHEMAS/v1/](SCHEMAS/v1/)
