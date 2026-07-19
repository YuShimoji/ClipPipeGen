# OUT-10 Third-Source Portfolio Expansion v0

## 現在の結論

状態は`NO_ELIGIBLE_LOCAL_THIRD_SOURCE_DECISION_READY`。bounded local inventoryを5件、
distinct sourceの詳細preflightを3件に制限して監査したが、OUT-08 `7J5aS_pcBj4`、
OUT-09 `D4i4fjs9PWc`とは異なる、12〜60秒のreviewable Shortを作れる第三のreal sourceは
ClipPipeGenの既存ローカル素材内に存在しなかった。

このためsource選択、slice選択、render、ASS/SRT、frame QA、review page、3-source portfolio
scorecardは作っていない。synthetic fixtureや既存2sourceの別区間を第三sourceとして扱わず、
外部URLも取得していない。

## Bounded inventory

| 順位 | identity / episode | 利用可能な証拠 | 判定 | exact blocker |
|---:|---|---|---|---|
| 1 | YouTube `7J5aS_pcBj4` / JP Pilot | OUT-08 accepted authorityとignored package | fail | OUT-08と同一recording identity |
| 2 | YouTube `D4i4fjs9PWc` / HoloEN OUT-09 | OUT-09 accepted authorityとignored package | fail | OUT-09と同一recording identity |
| 3 | synthetic fixture SHA `68a10aa7...ddd6` / OUT-01b・OUT-01e | local receipts、ledger、FFprobe、tracked historical provenance | fail | syntheticであり、2 episodeで同一video byteを再利用。real recordingではない |
| 4 | MDN T-Rex audio SHA `ea500e8d...62b1` | yt-dlp receipt、ledger、FFprobe | fail | 2.07425秒、videoなし、speech transcriptなし |
| 5 | synthetic fixture SHA `f3032285...0f3d` / OUT-01a | local receipt、ledger、FFprobe、tracked historical provenance | fail | synthetic、2.5秒、160x90、transcriptなし |

上位2件は既存accepted baselineなので詳細preflight対象外。新規になり得る残り3 distinct sourceだけを
preflightし、契約上限を超える探索は行っていない。

## 詳細preflight

### Synthetic long fixture

`out01e_real_transcript_subtitle_smoke_20260516`のvideo SHA
`68a10aa7ba513831d4dfc7bf00714dde62cf9d2b31a756e6be662d755f52ddd6`は、
`out01b_long_local_render_smoke_20260513`と同一byteである。H.264/AAC、`640x360`、24fps、
14.0秒、各1 streamとしてdecode可能だが、tracked historyは`_tmp/out01b_long_local_input.mp4`を
synthetic local inputと明記する。OUT-01eのVosk segmentもsynthetic local TTS audio由来で、
9.8028125秒・1 segment・human acceptanceなし。real episode/recordingとしては使えない。

### MDN audio-only smoke

`https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3`由来のWAVは
SHA `ea500e8d9d05d0e16ebb415dff6fa6e8257c719741489abfb08ae49ef4c162b1`、2.07425秒、
mono PCMでdecode可能。しかしvideo、speech transcript、12秒以上のinterval、vertical
composition evidenceがない。

### Synthetic short fixture

OUT-01aのsource SHA
`f303228500d56b920ca10e5000c9af0031dc7b16dd312e51c3005e2bc8a30f3d`はH.264/AAC、
`160x90`、15fps、2.5秒でdecode可能だが、tracked historyがsynthetic local mediaと明記し、
transcriptもない。

## 機械可読receipt

`docs/output_layer/out10_third_source_inventory_receipt.json`に、inventory上限、3件のpreflight、
hash、probe値、rights snapshot、exact blocker、外部取得要否を保存した。evidence gradeはreceipt、
exact hash、FFprobe、tracked provenanceが揃うものを`A_local_machine_*`とした。これはlocal
eligibility判断の強さであり、rightsやproduction acceptanceのgradeではない。

## 再開条件

次のどちらか一つが必要である。

1. provenance付きの第三のreal local sourceをClipPipeGen episode/material ledgerへ追加する。
   video/audioがdecode可能で、実transcript authorityを持ち、12〜60秒の自然に閉じた区間と
   vertical composition上の重要内容保持を確認できること。
2. supervisor/userが一つの外部source取得を明示承認する。その場合もURL、rights snapshot、
   recording identity、取得範囲を先に固定し、login/cookies/DRM/anti-bot回避を行わない。

再開後はsource probeを先に行い、composition/caption strategyをsource条件から選ぶ。OUT-09の
caption-band suppression、blur、crop、matteをdefaultとしてコピーしない。

## 閉じたgate

- OUT-08/09のaccepted authority、media、ignored packageは変更していない。
- real candidate、MP4、ASS、SRT、manifest、review server、human review questionは未生成。
- `human_review_pending=false`は「受理済み」ではなく「レビュー対象が存在しない」を意味する。
- rights、production render/subtitle/image quality、thumbnail、public/publishing、upload/OAuth、
  cross-machine portabilityは閉じたままである。
