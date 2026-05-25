# INT-02g — yt-dlp-video Boundary Spec

INT-02g は **spec only**。`yt-dlp-video` の実装、network fetch、yt-dlp 実行、CLI mode 追加、GUI fetch button 追加は行わない。目的は、URL 動画取得を `asset_fetch` に閉じ込め、render / Editing core / STT / GUI へ浸透させないための実装前 contract を固定すること。

この仕様は、URL fetch、network access、yt-dlp、FFprobe metadata readback、receipt、権利確認、人間責務、GUI 非露出、render 非接続を明確に分離する。

INT-02d (`yt-dlp-audio`) との違いは次の通り。

- 出力 artifact は `source_video.<ext>`（INT-02f `local-media-video` と同じ container 形）であり、`source.wav` ではない。
- FFmpeg normalize は行わない。yt-dlp が取得した container をそのまま `source_video.<ext>` として保存する。
- intermediate と output の区別はない。yt-dlp の出力ファイル自身が `source_video.<ext>` となる。intermediate retention は概念として持たないが、`fetch_receipt.json` には `source_pipeline.intermediate_retained=false` を明示する。
- 取得後の technical readback は FFprobe による metadata（duration / container / video codec / audio codec / resolution / fps / stream count）に限定する。

## Responsibility Split

| 領域 | 責務 | 禁止 |
|---|---|---|
| URL input | future `fetch-source-video --mode yt-dlp-video` の入力 URL と episode / material ID を受ける | `transcribe-audio` / Editing CLI / `render-tiny-proof` に URL を渡す |
| network access | future `src/integrations/asset_fetch/` adapter の actual 実行時だけ outbound access を行う | dry-run で network access する、pipeline / GUI / STT / render から network fetch する |
| yt-dlp | URL から source video を取得し、`source_video.<ext>` として保存し、provider / extractor / format / chosen format id / warnings を readback する | audio normalize、render / encode、cut、concat、subtitle burn-in、creative 判定 |
| FFprobe | 取得済み `source_video.<ext>` の metadata（duration / container / video codec / audio codec / resolution / fps / stream count）を読む | video を変換する、render / encode する、creative 判断 |
| FFmpeg | INT-02g では使わない。yt-dlp が選んだ container をそのまま保存する | URL 取得、normalize、cut、concat、subtitle burn-in、render、encode |
| receipt | command summaries、tool versions、input URL（scrub 済）、provider、chosen format、output hash / metadata、warnings、stderr digest、rollback を保存する | full stderr、secret、creative acceptance、publish 可否を保存する |
| rights | rights status / warnings を readback として snapshot する | rights status だけで local fetch を hard gate する |
| human responsibility | URL 選定、権利・規約 review、公開可否、creative acceptance を判断する | これらの判断を `asset_fetch` receipt に委譲する |
| GUI | INT-02g では表示・実行導線を追加しない | fetch button を先に出す、GUI から yt-dlp を直接呼ぶ |
| render | 取得済み `source_video.<ext>` を既存 `render-tiny-proof` の `source_video` material として読む。INT-02g 自身は render を呼ばない | URL / VOD fetch を `render-tiny-proof` に追加する |
| STT | INT-02g は `source.wav` を生成しない。STT との接続は INT-02e / INT-02c で取得した source audio を別途使う | URL 動画から音声 track を抽出して STT に渡す（INT-02g スコープ外） |

## Future Mode Contract

`yt-dlp-video` を実装する後続 slice（INT-02h）は、少なくとも次を満たす。

| 項目 | Contract |
|---|---|
| CLI mode | `fetch-source-video --mode yt-dlp-video` として追加する。INT-02g ではまだ追加しない |
| dry-run | subprocess / network を呼ばず、URL、output paths、tool discovery、command plan、conflicts、expected outputs を JSON で返す |
| actual execution | yt-dlp fetch → FFprobe metadata readback → sidecar / receipt / ledger write の順に限定する |
| intermediate policy | yt-dlp output 自身が `source_video.<ext>`。別 intermediate を残さない。receipt には `source_pipeline.intermediate_retained=false` を明示する |
| output | `materials/<material_id>/source_video.<ext>`, `sidecar.json`, `fetch_receipt.json`, `material_ledger.json` entry |
| source_video extension | yt-dlp が選んだ format から決まる container（`.mp4` / `.webm` / `.mkv` 等）。INT-02h で許容 container をホワイトリスト化する |
| tools | `tools[]` に `yt-dlp` と `ffprobe` の path source / version を保存する |
| commands | `commands[]` は yt-dlp fetch と FFprobe probe を分け、summary / exit_code を保存する |
| chosen format | yt-dlp が選んだ format id / format note / video codec / audio codec / resolution / fps / filesize を receipt に保存する |
| stderr | full stderr は保存しない。secret scrub 後の digest / tail のみ保存する |
| rollback | generated `source_video.<ext>`, sidecar, receipt, ledger material ID を対応付ける |
| failure cleanup | partial `source_video.<ext>` を削除する。sidecar / receipt / ledger は成功後だけ書く |

## URL Scrub Contract

実行時の URL は yt-dlp に渡すが、preflight / receipt / sidecar / command readback では次を scrub する（INT-02e と同じ contract）。

- query string（`?key=...`）
- fragment（`#...`）
- userinfo（`user:pass@`）
- yt-dlp が生成する access token / signed URL / signature parameter

`input.source_url` には scheme + host + path のみを残す。

## Explicit Non-Scope

- `yt-dlp-video` を source video URL fetch 以外へ広げること
- yt-dlp 実行を `src/integrations/asset_fetch/` 外へ出すこと
- dry-run で network fetch すること
- FFmpeg による normalize / cut / concat / subtitle burn-in / render / encode
- 取得した video から音声 track を抽出して STT に渡す（INT-02e で取得した `source.wav` を別途使う）
- GUI fetch button
- `transcribe-audio` への URL / VOD fetch 追加
- `render-tiny-proof` への URL fetch 追加
- Editing core / STT / render / encode / cut / concat への yt-dlp 浸透
- rights status の hard gate 化
- creative acceptance / preview 判定 / publishing acceptance

## Format Selection Constraint

INT-02h は yt-dlp の format selector を operator-controllable にする。INT-02g で固定する境界：

- default format selector は yt-dlp の default に依存させない。明示的な format expression を CLI で渡す（INT-02h で詳細決定）。
- format expression は yt-dlp が解釈し、選ばれた format の id / video codec / audio codec / container / resolution / fps / filesize を receipt に readback する。
- 選ばれた container は受容ホワイトリスト（INT-02h で確定）に含まれること。許容外は failure とし、sidecar / receipt / ledger を書かない。

## Test Requirements Before Implementation

INT-02h 実装 slice は、最低限以下を確認する。

1. dry-run が network / subprocess を呼ばない。
2. actual success が `source_video.<ext>` / sidecar / receipt / ledger entry を作る。
3. receipt が URL（scrub 済）、provider、chosen format、yt-dlp version、FFprobe version、commands、metadata、warnings、stderr digest、rollback を持つ。
4. rights status が `pending` / `failed` でも fetch 実行の hard gate にならない。
5. `transcribe-audio` は URL を拒否し続ける。
6. `render-tiny-proof` は URL を拒否し続け、material directory 経由でしか source video を読まない。
7. `src/pipeline/*`、Editing CLI、STT CLI、`render-tiny-proof` CLI、GUI に `yt-dlp` の直接呼び出しがない。
8. GUI smoke は fetch button なしで通る。
9. URL scrub が query / fragment / userinfo / signed URL token を receipt / sidecar / command summary から取り除いている。
10. 許容外 container を yt-dlp が選んだ場合、partial download を削除し sidecar / receipt / ledger を書かないこと。

## Rights Snapshot Contract

`fetch_receipt.json` の `rights_snapshot` は次を保存する（INT-02e と同じ readback、video へ拡張）。

| フィールド | 内容 |
|---|---|
| `rights_snapshot.compliance_status` | `pending` / `passed` / `failed` のいずれか。`set-compliance` の結果を snapshot |
| `rights_snapshot.warnings` | rights_manifest 由来の warning 文字列の配列 |
| `rights_snapshot.hard_gate` | 常に `false`。INT-02g 境界では rights status を hard gate にしない |
| `rights_snapshot.production_acceptance` | 常に `false`。technical fetch proof は creative / publishing acceptance ではない |

## Closure

INT-02g は spec only であり、commit は docs / boundary test だけを追加する。`fetch-source-video --mode yt-dlp-video` の CLI choice、`src/integrations/asset_fetch/yt_dlp_video.py` adapter、actual network fetch、real URL smoke は INT-02h で行う。

Post-spec implementation note: INT-02h はこの contract に従い、`fetch-source-video --mode yt-dlp-video` を source video URL fetch のみに限定して実装済み。許容 container は mp4 / mkv / webm、default format selector は `best[ext=mp4]/best[ext=mkv]/best[ext=webm]/best`、URL scrub と partial download cleanup を持つ。fake runner / dry-run / monkeypatch test で boundary を確認済み。archive.org `BigBuckBunny_124` で actual operator URL smoke も完了済み。
