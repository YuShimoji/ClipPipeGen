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

- **current_lane**: Slice 2 — TH-W01 / SH-04 / SH-03b / SH-03c / SH-05 / SH-05b / SH-05b+ / SH-05c / SH-05d / ED-01 / ED-02 / ED-02a / ED-03 / ED-04 / ED-05 / ED-06 / ED-07 / ED-07b / ED-08 / INT-02a / INT-02b / INT-02c / INT-02d / INT-02e / INT-02f / INT-02g / INT-02h / OUT-01 / OUT-01a / OUT-01b / OUT-01c / OUT-01d / OUT-01e done。samples runnable
- **current_slice**: Phase 0.5 — `HoloEN-01 publish-quality diagnostic pilot` を `in_progress (blocked_waiting_for_url)` として正本化。`docs/HOLOEN_PILOT.md` に URL 選定条件 / 避けるべき素材（members-only / paid / concert / 楽曲中心 / 第三者 IP リスク高）/ COVER 公式 attribution 要件 / runbook / quality scorecard（技術 / 制作 / 権利の 3 軸）/ acceptance / 次候補判断を固定。assistant は任意 URL を勝手に選定せず、actual smoke は operator-supplied HoloEN public VOD URL を待つ。Phase 0.5 は日本語 STT 対応の代替ではなく、英語発話コンテンツで「動画コンテンツとして成立しそうか」を早期診断する先行路線。`production_candidate=false` / creative acceptance / publishing acceptance ではない
- **next_action（assistant 側）**: HoloEN-01 actual smoke は user-supplied URL を待つ blocked 状態。operator は `docs/HOLOEN_PILOT.md` の URL 選定条件 / 避けるべき素材を確認し、HoloEN 公開済み VOD URL 1 本を選定する。URL 取得後の手順は同 doc の Runbook セクション。並行候補として日本語 STT 接続（`JP-STT-01` 候補）を Phase 1 に置けるが、Phase 0.5 の品質観測結果を見てから decide するのが推奨。chosen_format readback の archive.org extractor 限界、`transcript.language` defaulted 不整合は別 slice 候補として保留

### Phase 0.5 (i) HoloEN-01 in_progress（publish-quality diagnostic pilot — blocked_waiting_for_url）

`Phase 0` で plumbing が通ったあとに、英語発話コンテンツで「動画コンテンツとして成立しそうか」を早期観測する先行路線として `HoloEN-01` を起票・承認。`docs/HOLOEN_PILOT.md` を新規作成して URL 選定条件 / 避けるべき素材 / COVER 公式 attribution / runbook / quality scorecard / acceptance / blocked state 手順 / 次候補判断を固定した。

- 根拠ガイドライン: COVER 公式 derivative works terms（<https://hololivepro.com/en/terms/>）
- 主要 readback:
  - clip / shorts / translation は guideline 準拠なら個別許諾不要、ただし Content ID 登録は禁止
  - **members-only / paid / concert footage は明示的に clip 不可**（pilot 対象から除外）
  - 公開時は **元配信 URL link + 元配信 source title** が attribution として必須
  - 第三者 IP（ゲーム / 楽曲 / フォント等）は operator が個別確認
  - 公序良俗違反 / 政治宗教 / 名誉毀損 / official 偽装は禁止
- URL 選定方針: assistant は任意 URL を勝手に選定しない。operator が HoloEN 公開済み VOD を選定し、避けるべき素材条件を満たさないと判断したものを渡す
- 縦糸再利用: 既存 INT-02h / INT-02e / Vosk EN STT / generate-cuts / check-cut-context / generate-subtitles / OUT-01d diagnostic burn-in / ED-06 CSV export を新規 architecture なしで使う
- placeholder URL dry-run: `https://www.youtube.com/watch?v=__operator_supplied_holoen_vod__` を入力に `fetch-source-video --mode yt-dlp-video --dry-run` を実行し、no-network / URL scrub / format selector default `best[ext=mp4]/best[ext=mkv]/best[ext=webm]/best` / allowed containers `[mp4, mkv, webm]` / `will_write=false` / `will_call_subprocess=false` を readback
- 境界維持: `production_candidate=false` / creative acceptance / publishing acceptance / YouTube upload / OAuth / Content ID 登録 / 日本語 STT 対応 / font polish / GUI render button / FCPXML / Resolve XML には進まない
- 観測結果による次候補:
  - transcript / subtitle / cut が成立 → transcript review / production render acceptance
  - STT が weak → 別 EN STT provider（whisper.cpp 等）または transcript correction
  - URL 未指定で blocked のまま → operator にHoloEN public VOD URL 選定を依頼
  - 日本語展開が主目的 → `JP-STT-01` Japanese STT adapter smoke
  - pipeline 通るが品質弱い → human quality gate / review workflow

### Slice 2 (xxxi) Phase 0 one-pass smoke done（URL → rendered_video.mp4 + NLE CSV）

ClipPipeGen の縦糸を初めて 1 本通した。INT-02h 完了直後、同じ ignored episode `episodes/int02h_operator_smoke_20260518` を共用して `https://archive.org/details/BigBuckBunny_124` を入力に下記の連鎖を実行。

Pipeline trace（すべて exit 0）:

1. `fetch-source-video --mode yt-dlp-video` → `source_video.mp4` (h264 / aac / 640x360 / 24fps / 596.48s / 61.8MB)
2. `fetch-source-audio --mode yt-dlp-audio` → `source.wav` (pcm_s16le / 16kHz / mono / 19.1MB / sha256 `77b7e31e0e68ebf82410a151da858caa1eb5ad0a51d2a1c64da9fee02f4ed747`)
3. `transcribe-audio --engine vosk --model _tmp/stt_models/vosk-model-small-en-us-0.15`（`uvx --with vosk` 経由）→ `transcript.json`（`real_transcript=true`、`segment_count=2`、`duration_seconds=596.48`、語認識は `seg_000001 "the" [272.88-273.66]` と `seg_000002 "bush" [456.90-457.23]` のみ）
4. `init-edit-pack` + `generate-cuts --target-duration-seconds 12 --gap-threshold-seconds 30 --select-generated` → 2 cut candidates、両方 selected
5. `check-cut-context` → 2 cuts `passed`
6. `generate-subtitles --wrap-eaw 40 --selected-cuts-only` → 2 subtitles、`source_type=real_transcript`、`draft=true`、`source_segment_ids` 紐付け
7. `render-tiny-proof --burn-in-subtitles diagnostic`（最初の selected cut のみ render）→ `rendered_video.mp4`（0.78s / h264 / aac / 640x360 / 24fps / 101KB）、`diagnostic_subtitles.srt` に "the" 焼き込み、`subtitle_burn_in.status=enabled` / `subtitle_source_type=edit_pack_subtitles` / `derived_from_real_transcript=true`
8. `export-nle` → `nle_cut_list.csv` (2 rows) + `nle_export_manifest.json` + `nle_export_report.html`。CSV は `source_audio_provider=yt-dlp` / `transcript_provider=vosk` / `transcript_real=true` / `production_edit_candidate=false` を保持

Phase 0 で観測された詰まり所（Phase 1 候補）:

- **STT × コンテンツのミスマッチ**: Big Buck Bunny は主にアニメ + 音楽で英語台詞ほぼ無し。`vosk-model-small-en-us-0.15` は 596.48 秒の入力から計 1.11 秒分（"the" / "bush"）しか認識しなかった。これは "real STT 接続が動く" 証拠であると同時に、**creative acceptable な subtitle のためには日本語 model + 日本語コンテンツが必要** であることの実証
- **環境依存**: yt-dlp / ffmpeg は user-scope winget install で揃えられた。Vosk は `uv tool install vosk` + `uvx --with vosk` 経由で実行できたが、Vosk model は手動 download（`alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip` → `_tmp/stt_models/`）
- **`transcript.language` の不整合**: `--language` 未指定で defaulted `ja` のまま English model を使ったため、`transcript.language=ja` が記録された。English model 使用時に language readback を一致させる軽い修正余地
- **`chosen_format` readback の archive.org extractor 限界**（INT-02h closeout で既記録）

Phase 1 候補（観測根拠つき優先度）:

1. 日本語 STT 接続（vosk-model-ja or whisper.cpp）— **Phase 0 で最も明確な詰まり所**。日本語コンテンツで縦糸の "意味のある transcript" を出すために必須
2. TH-01 実 YMM4 base template walkthrough — `config/nlmytgen_path.json` 設定 + 実 `.ymmp` authoring。サムネレーンの user-owned acceptance
3. SH-02 `episode_pack` 統合 manifest — rights / material / edit / thumbnail / publish_draft を 1 個に結ぶ
4. Publishing（INT-01 + PB-01..04）— 縦糸の出口を閉じる

Boundary 維持: Phase 0 は **plumbing 一本通しの観測** であり、creative acceptance / publishing acceptance / production render / 日本語字幕 typography / safe-area polish / GUI render button のいずれにも昇格しない。すべての receipts / sidecar / report が `production_candidate=false` / `not for acceptance` を保持

Assistant-side validation — `uvx pytest -q`（173 passed）、`npm run smoke` / `npm run smoke:electron`（OK）、各段の CLI exit_code=0、Phase 0 全成果物は ignored `episodes/int02h_operator_smoke_20260518/` 配下に閉じ込め

### Slice 2 (xxx) INT-02h done（yt-dlp-video source video URL fetch）

- `src/integrations/asset_fetch/yt_dlp_video.py` — yt-dlp video adapter を新規。`discover_yt_dlp` は `--yt-dlp-path` → `CLIPPIPE_YTDLP` → PATH。`build_plan` は subprocess / network を呼ばず、scrubbed URL / format selector / 許容 container ホワイトリスト / yt-dlp と FFprobe の path discovery / output template / command summary を返す。`fetch_url_video` は yt-dlp version 取得 → URL download (output template `source_video.%(ext)s`) → produced container の whitelist 判定 → FFprobe metadata readback → sha256 / byte_size を返す。許容外 container や partial download は cleanup して raise する。既存 source_video.* がある状態では yt-dlp を呼ばずに raise する
- format selector / container — default は `best[ext=mp4]/best[ext=mkv]/best[ext=webm]/best`。許容 container は `mp4` / `mkv` / `webm`。`--format-selector` で operator が上書き可
- URL scrub — query / fragment / userinfo / signed URL token を receipt / sidecar / command summary / dry-run JSON から除去（既存 `yt_dlp_audio.scrub_url_for_readback` を再利用）
- `src/cli/fetch_source_video.py` — `--mode` choices に `yt-dlp-video` を追加。`--source-url` / `--format-selector` / `--yt-dlp-path` を新規 argument。`_mode_arg_error` は `yt-dlp-video` mode で `--source-url` 必須、`--source-path` / `--local-media` 拒否。`_paths` は `yt-dlp-video` mode で video path を post-fetch に確定する。`_conflicts` は material_dir 内の `source_video.*` を検出して conflict 扱い。`_execute_yt_dlp_video` が fetch / sidecar / receipt / ledger 書き出しを担い、`_build_yt_dlp_video_sidecar` / `_build_yt_dlp_video_receipt` で chosen_format / container / `source_pipeline.intermediate_retained=false` / `rights_snapshot.hard_gate=false` / `rights_snapshot.production_acceptance=false` を保存
- `tests/test_ytdlp_video_adapter.py` — 9 件の fake runner test。discover 順序、dry-run no subprocess、URL scrub、format selector、success mp4 readback、unsupported container cleanup、yt-dlp failure cleanup、ffprobe failure cleanup、非 http URL 拒否、既存 source_video.* がある場合の refuse
- `tests/test_source_video_fetch.py` — 7 件の INT-02h CLI test を追加。dry-run no-write、artifact 生成 + sidecar / receipt / ledger readback、URL scrub の receipt 透過、conflict without force、`--source-path` 拒否、rights pending でも fetch hard gate にならない、unsupported container failure 時 sidecar / receipt / ledger を残さない、help に `yt-dlp-video` / `--source-url` / `--format-selector` / `--yt-dlp-path` が現れる
- `tests/test_asset_fetch_boundary.py` — 既存 `test_fetch_source_video_exposes_local_video_acquisition_only` を rename / assertion 反転。help に `local-media-video` と `yt-dlp-video` 両方、`--source-url` / `--format-selector` / `--yt-dlp-path` / `--ffprobe-path` の存在、`render` / `encode` の不在を assertion
- 境界維持 — `transcribe-audio` / `generate-cuts` / `check-cut-context` / `generate-subtitles` / `render-tiny-proof` / `build-local-preview-pack` に URL / yt-dlp を浸透させない（既存 forbidden terms test 維持）。GUI fetch / render button、production render、production subtitle design、subtitle 字幕 typography polish、Publishing は INT-02h スコープ外
- Assistant-side validation — `uvx pytest -q tests/test_ytdlp_video_adapter.py`（9 passed）、`uvx pytest -q tests/test_source_video_fetch.py`（11 passed）、`uvx pytest -q tests/test_asset_fetch_boundary.py`（7 passed）、`uvx pytest -q`（173 passed）、`npm run smoke`（OK）、`npm run smoke:electron`（OK）、`git diff --check`（clean）を通過
- Operator smoke done — ignored `episodes/int02h_operator_smoke_20260518` で `fetch-source-video --mode yt-dlp-video` を fresh episode に対して `--dry-run` + actual run。dry-run は `will_write=false` / `will_call_subprocess=false` / URL scrub / format selector default / allowed containers `[mp4, mkv, webm]` を readback。actual run は archive.org `BigBuckBunny_124` URL を入力に `source_video.mp4` / `sidecar.json` / `fetch_receipt.json` / `material_ledger.json` entry を生成
- Tool acquisition readback — yt-dlp と ffmpeg は初期状態で PATH に不在。`choco install` は admin elevation 不在で失敗、`winget install --scope user` で `Gyan.FFmpeg 8.1.1` と `yt-dlp.yt-dlp 2026.03.17` を user scope で成功インストール。binary path は `--yt-dlp-path` / `--ffprobe-path` で明示渡しした
- URL acquisition readback — 当初 GCS public bucket（`https://commondatastorage.googleapis.com/.../ForBiggerBlazes.mp4`）は yt-dlp generic extractor に対して `HTTP 403 Forbidden` を返したため、archive.org の `https://archive.org/details/BigBuckBunny_124`（Blender Foundation, CC-BY 3.0）に切替。yt-dlp は archive.org extractor で 3 format（ogv 533x300 / mp4 640x360 / avi 1280x720）を解決し、format selector の whitelist 優先で mp4 640x360 を選択
- Receipt readback — `mode=yt-dlp-video`、`provider=yt-dlp`、`source_url=https://archive.org/details/BigBuckBunny_124`（scrub 維持）、`container=mp4`、`byte_size=61878609`、`sha256=46f62396c755e1ed0ab856a1521378d54196e125ef1a1643a199af087a15046b`、`tools=[yt-dlp 2026.03.17, ffprobe 8.1.1-full_build-www.gyan.dev]`、`input.format_selector=best[ext=mp4]/best[ext=mkv]/best[ext=webm]/best`、`input.allowed_containers=[mp4, mkv, webm]`、`intermediate.retained=false`、`source_pipeline.intermediate_retained=false`、`rights_snapshot={compliance_status_at_fetch: pending, hard_gate: false, production_acceptance: false}`、`video_metadata={duration_seconds: 596.48, video_codec: h264, audio_codec: aac, resolution: 640x360, fps: 24.0, stream_count: 2}`
- Audit ledger — `audit-material-ledger --format json` -> `{ok: true, issues: [], materials_count: 1}`
- Known limitation — `chosen_format` の format_id / vcodec / acodec / width / height / fps / filesize が全 None で receipt に残った。yt-dlp の `--print after_video:...` template は marker 行は出るが archive.org extractor は format field を `NA` で返すため。FFprobe metadata は完全に readback できているので機能要件は満たす。`chosen_format` readback の fallback は別 slice で扱う

### Slice 2 (xxix) INT-02g done（yt-dlp-video boundary spec only）

- `docs/YTDLP_VIDEO_SPEC.md` — `yt-dlp-video` を spec only として固定。yt-dlp は URL から source video を取得し chosen format / extractor / warnings を readback するだけ、FFprobe は metadata（duration / container / video codec / audio codec / resolution / fps / stream count）を読むだけ、FFmpeg normalize / cut / concat / subtitle burn-in / render / encode は INT-02g では行わない
- URL / network — URL は future `fetch-source-video --mode yt-dlp-video` の入力だけに限定。actual network access は future `src/integrations/asset_fetch/yt_dlp_video.py` adapter のみ。dry-run は network / subprocess を呼ばない
- URL scrub — 実行時の URL は yt-dlp に渡すが、preflight / receipt / sidecar / command readback では query / fragment / userinfo / signed URL token を scrub する（INT-02e と同じ contract）
- intermediate — yt-dlp output 自身が `source_video.<ext>`。別 intermediate を残さず、receipt は `source_pipeline.intermediate_retained=false` を明示
- format selector / container — INT-02h で明示 format expression と許容 container ホワイトリストを固定する。許容外 container は failure として partial download を削除し、sidecar / receipt / ledger を書かない
- receipt / rollback — URL (scrub 済)、provider、chosen format（id / video codec / audio codec / container / resolution / fps / filesize）、yt-dlp / FFprobe versions、commands、metadata、warnings、stderr digest、rollback を保存。rights snapshot は `hard_gate=false` / `production_acceptance=false`
- 境界維持 — `transcribe-audio` / `generate-cuts` / `check-cut-context` / `generate-subtitles` / `render-tiny-proof` に URL / yt-dlp を浸透させない。GUI fetch button は追加しない。`build-local-preview-pack` も network / fetch-source-video を呼ばない既存境界を維持
- INT-02h test 観点 — dry-run no network / no subprocess、actual success の `source_video.<ext>` / sidecar / receipt / ledger entry、receipt の必須 field、rights `pending/failed` でも fetch hard gate にしない、`transcribe-audio` / `render-tiny-proof` が URL を拒否し続けること、`src/pipeline/*` と Editing/STT CLI と `render-tiny-proof` CLI と GUI に yt-dlp の直接呼び出しがないこと、GUI smoke が fetch button なしで通ること、URL scrub、許容外 container failure cleanup を最低限固定
- `tests/test_asset_fetch_boundary.py` — `docs/YTDLP_VIDEO_SPEC.md` の必須文言（URL fetch / network access / yt-dlp / FFprobe / receipt / 権利確認 / 人間責務 / GUI 非露出 / render / STT / URL scrub / intermediate.retained=false / `fetch-source-video --mode yt-dlp-video` / 許容 container / rights `hard_gate=false`）と boundary doc の INT-02g 状態行と `yt-dlp-video` mode の spec only 記載を検証する境界 test を追加

### Slice 2 (xxviii) ED-08 / OUT-01e done（real STT subtitle draft linkage and diagnostic render smoke）
- `src/pipeline/subtitle_generation.py` — `transcript.stt.real_transcript=true` を subtitle draft source として読み、生成 `edit_pack.subtitles[]` に `source_type="real_transcript"`、`source_segment_ids[]`、`draft=true`、`diagnostic=true`、`not_production_subtitle_design=true`、`production_subtitle_design=false` を付与する。fake / fixture transcript は `source_type="transcript_segments"` のままで production candidate にはしない
- `src/cli/render_tiny_proof.py` — `edit_pack.subtitles[]` を subtitle source として使う既存 OUT-01d 経路を維持し、`subtitle_burn_in.source_ref.subtitle_source_type` / `derived_from_real_transcript` / transcript provider / model / `source_segment_ids[]` を receipt / manifest / report に readback する。timing mapping、included/clamped/skipped/invalid/empty status、filter preflight、burn-in disabled 既存経路は維持する
- `tests/test_subtitle_generation.py` / `tests/test_real_transcript_pipeline.py` / `tests/test_tiny_render.py` — real transcript segments -> subtitle draft、subtitle draft -> `edit_pack.subtitles[]`、`source_segment_ids[]` 保持、real transcript source readback、edit_pack subtitle source の render 利用、OUT-01d timing mapping 維持、fixture transcript 非 production 扱い、burn-in disabled 既存経路を targeted test で確認する
- Smoke readback — ignored `episodes/out01e_real_transcript_subtitle_smoke_20260516` で Windows TTS 由来の local diagnostic `source.wav` を Vosk model `_tmp/stt_models/vosk-model-small-en-us-0.15` に通し、`transcript.json`（1 segment / 9.8028125 秒 / `real_transcript=true`）から 1 cut、1 subtitle draft、`renders/out01e_real_transcript_subtitle_render/rendered_video.mp4` を生成。output metadata は duration `8.82`、container `mov,mp4,m4a,3gp,3g2,mj2`、video codec `h264`、audio codec `aac`、resolution `640x360`、fps `24/1`、stream count `2`
- Boundary — ED-08 / OUT-01e は real STT subtitle provenance を diagnostic render に接続する slice であり、STT 品質評価、transcript correction UI、production subtitle design、typography/safe-area polish、URL video acquisition、GUI render button、publishing、FCPXML / Resolve XML には進んでいない。`production_candidate=false` / `creative_acceptance=false` / `publish_acceptance=false` のまま扱う

### Slice 2 (xxvii) OUT-01d done（subtitle timing / font-filter preflight）
- `src/cli/render_tiny_proof.py` — OUT-01c の optional diagnostic overlay を保ちつつ、subtitle event ごとに `original_start_seconds` / `original_end_seconds` / `render_start_seconds` / `render_end_seconds` / `status` を記録する。source timeline から render timeline へは `render_start_seconds` を offset として差し引き、window 内は `included`、window をまたぐものは `clamped_to_render_window`、window 外は before/after skipped、invalid timing / empty text は SRT へ書かず readback に残す
- `src/integrations/render/ffmpeg_tiny.py` — FFmpeg stderr から subtitle filter / libass / fontconfig / font provider / SRT parsing / path escaping 由来の詳細を `subtitle_filter_failed` の内訳として分類できるようにした。preflight は追加 subprocess を増やさず、成功 render は `passed_by_successful_render`、失敗 render は failure detail、SRT write は UTF-8 encoding readback を残す
- `tests/test_tiny_render.py` — normal timing mapping、render_start offset、included/clamped/skipped/invalid/empty status、source ref 維持、filter/font/path/SRT failure detail、burn-in skipped、burn-in disabled 既存経路、OUT-01b/OUT-01c readback 維持を targeted test で確認する
- Smoke readback — ignored `episodes/out01d_timing_font_preflight_smoke_20260514` で `src_video_out01d_timing` / `src_audio_out01d_timing` / `cut_out01d_timing_001` / `edit_pack.subtitles[]` から `renders/out01d_timing_font_preflight/rendered_video.mp4` を生成。output metadata は duration `12.0`、container `mov,mp4,m4a,3gp,3g2,mj2`、video codec `h264`、audio codec `aac`、resolution `640x360`、fps `24.0`、stream count `2`
- Boundary — OUT-01d は subtitle burn-in diagnostic の時間軸・環境差・失敗分類を固める slice であり、production subtitle design、typography/safe-area polish、URL video acquisition、GUI render button、publishing、FCPXML / Resolve XML には進んでいない。`production_candidate=false` のまま扱う

### Slice 2 (xxvi) OUT-01c done（subtitle burn-in diagnostic）
- `src/integrations/render/ffmpeg_tiny.py` — optional `subtitle_file_path` を render plan / command に追加し、FFmpeg `subtitles` filter で generated UTF-8 SRT を diagnostic overlay として焼き込めるようにした。filter / libass / font 由来の失敗は `subtitle_filter_failed`、subtitle file 欠落は `subtitle_source_missing` として分類する。既存の FFmpeg/FFprobe preflight、profile fallback、attempt readback、metadata probe は維持する
- `src/cli/render_tiny_proof.py` — `--burn-in-subtitles off|diagnostic` を追加。default は `off`。diagnostic mode では `edit_pack.subtitles[]` を優先し、無ければ sibling `transcript.json` segments を diagnostic source として使う。source timeline を rendered timeline に clamp して `diagnostic_subtitles.srt` を生成し、`subtitle_burn_in` / `subtitle_source_ref` / `subtitle_overlay_policy` を receipt / manifest / report に残す
- `tests/test_tiny_render.py` — subtitle filter command、filter failure classification、CLI burn-in readback、source missing failure、既存 OUT-01b timeline/profile readback 維持を追加・更新。既存 default render は `subtitle_burn_in.status=disabled` のまま
- Smoke readback — ignored `episodes/out01c_subtitle_burnin_smoke_20260513` で synthetic local input `_tmp/out01c_subtitle_burnin_input.mp4` を `src_video_out01c_subtitle` / `src_audio_out01c_subtitle` として登録し、fake transcript segments から `generate-subtitles` で `edit_pack.subtitles[]` を作成。manual selected cut `cut_out01c_subtitle_001`（`1.0` -> `13.0` 秒）から `renders/out01c_subtitle_burnin/rendered_video.mp4` を再生成
- Metadata / subtitle readback — source video は duration `14.0`、h264/aac、`640x360`、`24.0` fps、stream count `2`。source audio は duration `14.016`、`pcm_s16le`、`16000` Hz、mono。rendered output は duration `12.0`、container `mov,mp4,m4a,3gp,3g2,mj2`、h264/aac、`640x360`、`24.0` fps、stream count `2`。subtitle source は `edit_pack_subtitles`、subtitle IDs は `sub_001` / `sub_002` / `sub_003`、source segment IDs は `seg_out01c_001` / `seg_out01c_002` / `seg_out01c_003`
- Overlay policy — `position=bottom_center_fixed`、font strategy は FFmpeg subtitles filter default font provider、timing は source timeline から rendered timeline へ clamp、line handling は既存改行保持で line-wrap / kinsoku / safe-area / typography polish は行わない。selected profile / attempted profile は `mp4_h264_aac` のみ、fallback は発生していない
- Boundary — OUT-01c は subtitle artifact が visual artifact に接続できることの diagnostic proof であり、production render、creative edit acceptance、publishing、font/safe-area polish、GUI render button、URL video fetch、FCPXML / Resolve XML には進んでいない。`production_candidate=false` のまま扱う

### Slice 2 (xxv) OUT-01b done（longer local video render smoke）
- `src/cli/render_tiny_proof.py` — source audio readback で `fetch_receipt.json` top-level `audio_format` が無い場合も、既存 `preflight.audio_format` から WAV codec / sample rate / channel を manifest に補完する。render architecture は増やさず、OUT-01a の command plan / attempt / failure classification 経路をそのまま使う
- `tests/test_tiny_render.py` — 12 秒 local timeline の正常系と、source video duration が短い場合の clamp / duration target unmet / stream mismatch warning を追加。source_video / source_audio / edit_pack refs、selected profile、attempted profiles、fallback flag、output metadata、source audio WAV metadata を receipt / manifest / report で検証する
- Smoke readback — ignored `episodes/out01b_long_local_render_smoke_20260513` で synthetic local input `_tmp/out01b_long_local_input.mp4` を `src_video_out01b_long_local` / `src_audio_out01b_long_local` として登録し、manual selected cut `cut_out01b_long_001`（`1.0` -> `13.0` 秒）から `renders/out01b_long_local/rendered_video.mp4` を再生成
- Metadata readback — source video は duration `14.0`、container `mov,mp4,m4a,3gp,3g2,mj2`、h264/aac、`640x360`、`24.0` fps、stream count `2`。source audio は duration `14.016`、`pcm_s16le`、`16000` Hz、mono。rendered output は duration `12.0`、container `mov,mp4,m4a,3gp,3g2,mj2`、h264/aac、`640x360`、`24.0` fps、stream count `2`
- Timeline / profile — policy は `single_selected_cut_clamped_to_shortest_input_no_loop_no_speed_change_no_subtitle_burn_in`、duration target `12.0` を満たし、clamp は発生していない。selected profile / attempted profile は `mp4_h264_aac` のみ、fallback は発生していない
- Boundary — OUT-01b は longer local diagnostic render coverage であり、production render、creative edit acceptance、publishing、subtitle burn-in、font/safe-area polish、GUI render button、URL video fetch、FCPXML / Resolve XML には進んでいない。`production_candidate=false` のまま扱う
- Assistant-side validation — targeted OUT-01b / tiny render tests、source-video acquisition tests、ED-07b transcript tests、ED-06 export tests、`uvx pytest -q`、`npm run smoke`、`npm run smoke:electron`、`git diff --check`、rendered video FFprobe metadata readback を通過

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
- INT-02a で source audio の fake fetch、INT-02b で yt-dlp / FFmpeg 境界仕様、INT-02c で local-media-audio FFmpeg 正規化と実 FFmpeg operator smoke、INT-02d で `yt-dlp-audio` spec only、INT-02e で source audio URL fetch 限定の実装と real URL operator smoke、INT-02f で local source video acquisition と FFprobe metadata readback、INT-02g で `yt-dlp-video` boundary spec only、INT-02h で `fetch-source-video --mode yt-dlp-video` 実装と fake runner / dry-run / monkeypatch test、SH-05d で取得済み source audio の preview bridge、ED-06 で minimal NLE CSV export、ED-07b で real STT transcript path、ED-08 / OUT-01e で real STT subtitle draft linkage と diagnostic render smoke、OUT-01 で tiny rendered video proof、OUT-01c で diagnostic subtitle overlay、OUT-01d で subtitle timing / font-filter diagnostic readback は完了。次の推奨は INT-02h の actual operator URL smoke と Phase 0 一本通し（実 URL → rendered_video.mp4 + CSV cut list）で詰まり所を観測すること。日本語 STT 破綻は Phase 0 で観測根拠として受容し、Phase 1 候補（vosk-model-ja / whisper.cpp 等の operator setup）に回す。TH-01 walkthrough、SH-02 episode_pack、Publishing、GUI button は Phase 1 以降に分ける。
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
