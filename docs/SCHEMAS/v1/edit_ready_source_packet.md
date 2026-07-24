# Edit-Ready Source Packet v1

`build-edit-ready-source-packet` が生成する、取得元・実 media・transcript authority・
rights snapshot・consumer readiness を一つの identity に束ねる機械可読契約である。
この契約は編集入力の準備完了を表し、編集内容、production、rights、公開を承認しない。

## 生成コマンド

```powershell
python -m src.cli.main build-edit-ready-source-packet `
  --packet-id <packet-id> `
  --episode-id <episode-id> `
  --source-locator <local-media-path-or-public-url> `
  --source-identity <provider:identity> `
  --language <bcp47-language> `
  --rights-manifest <rights-manifest.json> `
  --caption-track <provider-caption.json3> `
  --caption-authority provider_official `
  --caption-provider-locator <provider-caption-locator> `
  --root episodes
```

Caption の代わりに既存の real transcript を `--transcript` で渡すか、明示した
`--stt-engine vosk --stt-model <path>` を使用できる。fake / fixture transcript は
authority に昇格できず、real provider / real STT の失敗時に fixture へ fallback しない。

## authority の優先順位

| 優先度 | kind | 適格条件 |
|---:|---|---|
| 300 | `official_provider_caption` | provider locator、言語、cue timing、text、coverage が有効 |
| 250 | `verified_caption_sidecar` | 同じ caption 検証を通り、利用者が verified sidecar と明示 |
| 200 | `verified_imported_subtitle_transcript` | `real_transcript=true`、audio SHA・言語・timing・coverage が一致 |
| 100 | `configured_real_stt` | 明示 provider/model の real STT。schema、audio SHA、言語、timing、coverage が一致 |

最大 priority の適格候補だけを採用する。適格候補がなければ
`EDIT_READY_SOURCE_PACKET_BLOCKED_V1` を返す。fake、fixture、暗黙 fallback は候補にしない。

## Caption 検証

次のいずれかを検出すると packet を生成せず typed blocked result を返す。

- start が負、duration が 0 以下、または `end <= start`
- cue の start が前の cue より前
- raw cue ID の重複
- 正規化後に text が空
- cue end が source duration を許容差 0.25 秒より越える
- provider locator の言語と要求言語が不一致
- source duration に対する union coverage が 0.05 未満

正規化は空白・改行を整えるだけで、発話内容、話者、歌唱、歌詞、固有名詞、意味を
推定・書換えしない。各 segment の `notes` に raw caption event ID/index または元
transcript segment ID を残す。

## Packet の必須面

| 面 | 主な内容 |
|---|---|
| identity | `packet_schema`, `schema_version`, `packet_id`, `episode_id`, `state`, `created_at` |
| input binding | `input_fingerprint`。source locator/input hash、source identity、language、rights/caption/transcript hash、STT 設定を canonical SHA-256 化 |
| source | provider identity/locator、packet 内 path、SHA-256、byte size、duration、resolution、acquisition mode、material ID |
| acquisition | video/audio fetch receipt、output SHA、warning、高コスト stage、resume capability |
| materials / rights | ledger、sidecar、normalized audio、入力 rights の exact snapshot と runtime copy。approval は別 gate |
| transcript candidates | 候補 kind、priority、eligible、選択理由、hash、language、count、coverage、検証 readback |
| authority | selected candidate、kind、selection reason、fixture prohibition |
| normalized transcript | path、language、segment count、covered seconds、coverage、元 segment への mapping |
| readiness | warning、typed blocking reason、named consumer ごとの ready/blocked |
| integrity | artifact manifest の file SHA-256 と packet canonical payload SHA-256 |

`EDIT_READY_SOURCE_PACKET_OPERATIONAL_V1` が解放する consumer は
`editorial_planning`、`timeline_ir_generation`、`subtitle_processing`、
`render_pipeline` の入力読込みだけである。次は常に false または pending のまま保持する。

- human/editorial acceptance
- rights approval
- production acceptance
- public/publishing readiness
- upload

## Resume

`--resume` は既存 packet の `input_fingerprint`、packet canonical integrity、manifest
配下の全 file hash、HTML readback の存在を検証する。すべて一致した場合だけ取得・音声正規化・
STT を再実行せず既存 packet を返す。異なる入力、欠落 file、hash 破損、packet 改変は
fail closed とし、既存の成功 packet を上書きしない。

## 保存境界

実 media、caption snapshot、normalized transcript、packet JSON、HTML readback は
`episodes/<episode-id>/` 以下の ignored local artifact であり Git に追加しない。
portable な正本は本契約、CLI、pipeline validation、tests である。
