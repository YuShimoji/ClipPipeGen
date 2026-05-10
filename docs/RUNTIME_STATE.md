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

- **current_lane**: Slice 2 — TH-W01 / SH-04 / SH-03b / SH-03c / SH-05 / SH-05b / ED-01 / ED-02 / ED-02a / ED-03 / ED-04 / ED-05 / ED-07 / INT-02a / INT-02b / INT-02c / INT-02d done。samples runnable
- **current_slice**: Slice 2 — SH-05b local-preview-pack report QA / polish は done。`preview_report.html` 冒頭に status summary、decision warnings、artifact links を追加し、日本語 fixture transcript でも operator-visible な read-only review surface として読めることを localhost / DOM readback で確認した
- **next_action（assistant 側）**: 次の推奨は SH-05c として GUI read-only preview pack ingest を小さく切ること。GUI に fetch button や実行 button は追加せず、既存 episode の `preview_manifest.json` / `preview_report.html` を読むだけに限定する。GUI surface が不要なら、INT-02d の仕様に従い `yt-dlp-audio` 実装 slice を source audio URL fetch のみに限定して進める。`fetch-source-video` / GUI fetch button / render / encode はまだ未実装

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
- 実 subtitle burn-in、動画レンダリング、NLE export、GUI action button は未実装。OUT-01 / ED-06 / SH-03 successor として扱う

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
- ED-03 は `check-cut-context` と `status-episode` readback まで実装済み。creative acceptance、動画 preview、NLE export は未実装。
- INT-02a で source audio の fake fetch、INT-02b で yt-dlp / FFmpeg 境界仕様、INT-02c で local-media-audio FFmpeg 正規化と実 FFmpeg operator smoke、INT-02d で `yt-dlp-audio` spec only は実施済み。次の推奨は仕様に従い `yt-dlp-audio` の実装 slice を source audio URL fetch のみに限定して扱うこと。
- NLMYTGen CLI bridge が想定通り動作した場合、shared package 化を検討（ただし CLI bridge で 2-3 個の実例が出てから）
- ホロライブ以外の VTuber 事務所（にじさんじ等）への対象拡大は v1 では検討しない。Slice 1 完了後に rights_manifest 構造の汎用性を見て判断する

## 関連ドキュメント

- 入口: [README.md](../README.md) / [AGENTS.md](../AGENTS.md)
- 方針: [CLAUDE.md](../CLAUDE.md)（ルート）
- GUI MVP: [GUI_MVP_SCOPE.md](GUI_MVP_SCOPE.md)
- 不変条件: [INVARIANTS.md](INVARIANTS.md)
- 自動化境界: [AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md)
- レーン責務: [LANES.md](LANES.md)
- 機能一覧: [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
- 現スライス: [FIRST_SLICE.md](FIRST_SLICE.md)
- schema: [SCHEMAS/v1/](SCHEMAS/v1/)
