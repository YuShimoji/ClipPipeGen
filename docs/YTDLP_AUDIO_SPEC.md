# INT-02d — yt-dlp-audio Boundary Spec

INT-02d は **spec only**。`yt-dlp-audio` の実装、network fetch、yt-dlp 実行、CLI mode 追加、GUI fetch button 追加は行わない。目的は、URL 取得を `asset_fetch` に閉じ込め、STT / Editing / render / GUI へ浸透させないための実装前 contract を固定すること。

この仕様は、URL fetch、network access、yt-dlp、FFmpeg 正規化、receipt、権利確認、人間責務、GUI 非露出、STT 非接続を明確に分離する。

Post-spec implementation note: INT-02e はこの contract に従い `fetch-source-audio --mode yt-dlp-audio` を source audio URL fetch のみに限定して実装済み。technical smoke URL の actual run で receipt / sidecar / ledger / WAV readback を確認済み。

## Responsibility Split

| 領域 | 責務 | 禁止 |
|---|---|---|
| URL input | future `fetch-source-audio --mode yt-dlp-audio` の入力 URL と episode / material ID を受ける | `transcribe-audio` や Editing CLI に URL を渡す |
| network access | future `src/integrations/asset_fetch/` adapter の actual 実行時だけ outbound access を行う | dry-run で network access する、pipeline / GUI / STT から network fetch する |
| yt-dlp | URL から元 media を一時取得し、provider / extractor / format / downloaded bytes / warnings を readback する | audio normalize、STT、cut、concat、render、encode、creative 判定 |
| FFmpeg | yt-dlp が得た media から `source.wav` を PCM WAV / mono / 16kHz / 16-bit に正規化する | URL 取得、cut、concat、subtitle burn-in、render、encode |
| receipt | command summaries、tool versions、input URL、provider、output hash、warnings、stderr digest、rollback を保存する | full stderr、secret、creative acceptance、publish 可否を保存する |
| rights | rights status / warnings を readback として snapshot する | rights status だけで local fetch を hard gate する |
| human responsibility | URL 選定、権利・規約 review、公開可否、creative acceptance を判断する | これらの判断を `asset_fetch` receipt に委譲する |
| GUI | INT-02d では表示・実行導線を追加しない | fetch button を先に出す、GUI から yt-dlp / FFmpeg を直接呼ぶ |
| STT | `source.wav` 生成後、既存のローカル音声として読む | URL / VOD fetch を `transcribe-audio` に追加する |

## Future Mode Contract

`yt-dlp-audio` を実装する後続 slice は、少なくとも次を満たす。

| 項目 | Contract |
|---|---|
| CLI mode | `fetch-source-audio --mode yt-dlp-audio` として追加する。INT-02d ではまだ追加しない。INT-02e で source audio URL fetch 限定として追加済み |
| dry-run | subprocess / network を呼ばず、URL、output paths、tool discovery、command plan、conflicts、expected outputs を JSON で返す |
| actual execution | yt-dlp fetch → FFmpeg normalize → sidecar / receipt / ledger write の順に限定する |
| intermediate policy | downloaded media は一時 file とし、success / failure とも削除する。保持しないため ledger 登録しない。receipt には `intermediate.retained=false` と処理概要を残す |
| output | `materials/<material_id>/source.wav`, `sidecar.json`, `fetch_receipt.json`, `material_ledger.json` entry |
| source.wav | PCM WAV / mono / 16kHz / 16-bit |
| tools | `tools[]` に `yt-dlp` と `ffmpeg` の path source / version を保存する |
| commands | `commands[]` は yt-dlp fetch と FFmpeg normalize を分け、summary / exit_code を保存する |
| stderr | full stderr は保存しない。secret scrub 後の digest / tail のみ保存する |
| rollback | generated `source.wav`, sidecar, receipt, ledger material ID を対応付ける。retained intermediate はない |
| failure cleanup | partial `source.wav` と temporary intermediate を削除する。sidecar / receipt / ledger は成功後だけ書く |

## Explicit Non-Scope

- `yt-dlp-audio` を source audio URL fetch 以外へ広げること
- yt-dlp 実行を `src/integrations/asset_fetch/` 外へ出すこと
- dry-run で network fetch すること
- `fetch-source-video`
- GUI fetch button
- `transcribe-audio` への URL / VOD fetch 追加
- Editing core / STT / render / encode / cut / concat への FFmpeg / yt-dlp 浸透
- rights status の hard gate 化
- creative acceptance / preview 判定

## Test Requirements Before Implementation

後続の実装 slice は、最低限以下を確認する。

1. dry-run が network / subprocess を呼ばない。
2. actual success が `source.wav` / sidecar / receipt / ledger を作る。
3. receipt が URL、provider、yt-dlp version、FFmpeg version、commands、warnings、stderr digest、rollback を持つ。
4. rights status が `pending` / `failed` でも fetch 実行の hard gate にならない。
5. `transcribe-audio` は URL を拒否し続ける。
6. `src/pipeline/*`、Editing CLI、STT CLI、GUI に `yt-dlp` / `ffmpeg` の直接呼び出しがない。
7. GUI smoke は fetch button なしで通る。
