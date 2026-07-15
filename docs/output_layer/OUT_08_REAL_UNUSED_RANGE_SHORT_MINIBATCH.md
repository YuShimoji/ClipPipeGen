# OUT-08 Real Unused-Range Vertical Shorts Mini-Batch

OUT-08 は、OUT-06 までに使用した実素材範囲を避け、残る real source authority
から内容の異なる vertical Shorts 候補を target 2 / minimum 1 で作る薄い
output slice である。実生成数は 2。artifact
`clip-out08-real-unused-range-short-minibatch-v0-001` は
`OUT08_REAL_UNUSED_RANGE_SHORT_MINIBATCH_REVIEW_READY` で、人間が各候補を
一本の編集単位として判断できる。これは internal review evidence であり、
production render、production subtitle-design acceptance、rights clearance、
public-ready asset、publishing action ではない。

## 直接見る入口

ignored package の canonical location は次である。

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/
```

Thank (`DESKTOP-H53P1T4`) では `http://127.0.0.1:8071/index.html` と exact
`src.cli.serve_review` route の page HTTP `200` / MP4 Range `206` を確認したが、
これは last-host evidence であって portable current entrypoint ではない。
Planner007 (`DESKTOP-U9P4LKJ`) の 2026-07-15 probe は `package_missing` /
`server_stopped`。したがって現在は URL や package 内 launcher を開かず、先に
exact private package recovery を行う。

```powershell
uvx python -m src.cli.main recover-out08-private-review-package --format json probe
```

Thank での export、利用者所有の private copy、Planner007 での atomic import は
`OUT_08_PRIVATE_REVIEW_PACKAGE_RECOVERY.md` を正とする。媒体を再生成せず、ZIP と
media を Git に追加しない。import 後の probe が
`package_verified_exact` / `server_running_verified` になったときだけ、その host
固有 localhost URL が current human entrypoint になる。

page は candidate 01 と 02 の playable video を縦一列に置き、details は
折り畳む。navigation JPG は候補を識別しやすくする final-video frame であり、
decorated thumbnail、thumbnail candidate、thumbnail acceptance ではない。

## Build contract

```powershell
uvx python -m src.cli.main build-real-unused-range-short-minibatch `
  --episode-dir episodes/jp_pilot01_hololive_bancho_20260525 `
  --output-dir episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch `
  --candidate-plan-input episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch_plan.json `
  --format json
```

builder は source video/audio、official caption、transcript、edit pack、material
ledger、rights manifest、cut decision packet、boundary evidence、declarative
candidate-plan input を読む。既存 OUT-06 使用範囲を candidate scan で除外し、
全 authority/input hash を記録する。staging package を検証してから専用 ignored
output へ atomic promotion し、既存 review package や authority は変更しない。

## 二本の編集構成

| 候補 | source ranges | semantic / media | 字幕 | MP4 SHA-256 | review purpose |
|---|---|---:|---:|---|---|
| `candidate_01` | `cut_004` `50.868–60.277`; `cut_005` `60.277–79.163` | `28.295s` / `28.266667s` | 17 | `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` | 勝負の提示から帽子を巡る認識違い、勝利扱いと困惑した別れまでが短い一場面として成立するかを見る。 |
| `candidate_02` | `cut_006` tail `81.298–98.315`; `cut_007` `98.315–116.467`; `cut_008` `116.934–135.219` | `53.454s` / `53.466667s` | 54 | `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b` | 遭遇と対立の進展から、相手の隙を突いて攻撃する転換点までが一本の流れとして持続するかを見る。 |

candidate 01 は `9.409s` に hard cut を持つ。candidate 02 は `17.017s`、
`35.169s` に hard cut を持つ。`cut_009` の final cut decision は `reject` の
ままで、authority は変更していない。candidate 02 の全 source range は
reject interval `135.219–144.000` と非交差で、`cut_009` 由来の映像・音声・
字幕・caption・segment は使わない。

修復前 package は `137.054–138.055` / `sub_102` を dependent payoff 例外として
含めていたが、supervisor correction により現行 plan・validator・package から除去した。

実レンダー後の readback で見つかった明確な語中分断は、`sub_038`、`sub_045`、
`sub_061`、`sub_063`、`sub_064`、`sub_067`、`sub_096`、`sub_098` に bounded
line-break hint を適用して修復した。`sub_061`、`sub_064`、`sub_067` は source
text を保持したまま display 上の ASCII 空白だけを除去し、その変換を readback
へ記録する。`sub_067` の「特殊 / な」と `sub_068` の「ホロ / モワール」は
3 行安全域内に収めた残存 review debt であり、production typography acceptance
を意味しない。

## Package readback

package は次の 17 files で構成される。

- `candidate_01.mp4` / `candidate_02.mp4`
- candidate ごとの `.ass` / `.srt`
- candidate ごとの `_navigation.jpg` / `_frame_qa.jpg`
- `candidate_scan_readback.json`
- `candidate_plan.json`
- `batch_readback.json`
- `batch_manifest.json`
- `index.html`
- `open_preview.ps1`
- `serve_preview.ps1`

manifest は自分自身を除く 16 payload files を byte SHA-256 で覆い、manifest
self-integrity `22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4`
を canonical JSON hash として別に記録する。source identity は
YouTube ID `7J5aS_pcBj4`、source video SHA-256
`6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`、
source audio SHA-256
`46e4bc9e26d52ed8f83b0b4088ddcd6ddac5a873fa1bb4a440c209834f026671`、
official caption SHA-256
`3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`
で固定した。tracked docs に caption plaintext は複製しない。

## Media、audio、browser evidence

両候補は H.264/AAC、1080x1920、30fps、yuv420p、faststart、video/audio 各
1 stream で、full FFmpeg decode を通過した。0.5 秒以上の black interval は
なく、-50dB で 1.5 秒以上の silence interval もない。candidate 01 の
normalized output は `-14.24 LUFS / -1.49 dBTP`、candidate 02 は
`-14.20 LUFS / -1.49 dBTP`。いずれも package readback に input/output
loudness、true peak、normalization decision を記録した。

現行 localhost browser check では両 video が `readyState=4`、media error
`null`。desktop/mobile viewport とも horizontal overflow なし、console
warning/error なしを確認した。HTTP `200`、byte range `206 Partial Content`、
ffprobe、full decode を再確認した。
automation browser では native control の direct seek/currentTime 進行を確実に
観測できていない。開始、主要境界、終端の frame QA は通過したが、direct
playback/seek は人間レビューに残し、編集の自然さを machine acceptance しない。

## 人間判断と閉じた gate

page が尋ねる一問は次である。

> 追加Shorts候補ごとに、一本の編集単位として成立するか、テンポ・境界・字幕・音声に違和感があれば自由記述してください。

返答は candidate ごとの自由記述で受ける。人間判断前は次を維持する。

- `human_review_pending=true`
- `internal_review_only=true`
- `authority_mutated=false`
- `cut009_final_cut_decision=reject`
- `navigation_frames_are_thumbnails=false`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights_status=pending`
- `public_ready=false`
- `publishing_acceptance=false`
- `publish_attempted=false`

OUT-07 は main commit `4fad107ca5ecb9c86de2df73f08dedfbe14cf9c9`
上の `PARK_PROVISIONAL_USABLE` predecessor で、追加 thumbnail iteration は
禁止されたままである。`artifacts/ACTIVE_REBUILD.json` はその parked OUT-07
rebuild contract であり、OUT-08 の active machine readback ではない。
