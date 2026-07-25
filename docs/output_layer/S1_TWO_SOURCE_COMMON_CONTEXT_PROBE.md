# S1 Two-Source Common-Context Probe v1

## 到達点

`build-common-context-probe` は、取得済みの実 source 2 本だけを exact media / caption /
transcript / rights hash へ結び、creator-authored thesis と commentary を source caption から
分離した一つの argumentative timeline を内部レビュー package にする。schema は
`clippipegen.s1.common_context_probe_plan.v1`、実 artifact は
`clip-s1-two-source-common-context-probe-v1-001`。

この実装は generic N-source architecture ではない。二本が一つの論として成立したという
意味判断も行わない。終端は
`S1_S3_COMMON_CONTEXT_PROBE_READY_FOR_S4_HUMAN_REVIEW` であり、人間が S4 で判断する。

## 実ペアと問い

在庫の provider caption と rights snapshot を比較し、次の二本を選んだ。

| source | material / identity | exact media SHA | 選定根拠 |
|---|---|---|---|
| SOURCE-04 | `src_video_out11_source04` / `youtube:PQ54uUV41-k` | `f3aa118f...09d63` | ドッキリ反転後に医者・魔法使い・科学者を試し「頼れる人がいない」へ至る caption evidence |
| 秘密の診察室 | `src_video_hololive_out10` / `youtube:TlnviOwLRmk` | `8cbb98ee...a3a4` | 症状・軽い打撲が、役割遊び・急患・オペ・過剰処置・普通の病院要求へ進む caption evidence |

editorial question は「助けを求める状況は、なぜ自信満々だが適合しない解決策の連鎖で
悪化するのか？」。working thesis は creator-authored synthesis として明示し、各 cut と
commentary は source-namespaced evidence ID へ戻せる。

OUT-09 は caption 内容と source title の接続がこの問いに弱く、SOURCE-05 は歌唱・歌詞意味を
確認済みにしない既存境界がある。Bancho source との組合せより、選定ペアは「困りごと・助け手・
失敗終端」を直接字幕で往復できるため、最も狭く防御可能だった。

## Timeline と表示契約

timeline は 6 cut、各 source 3 cut、source switch 5 回、約 98.896 秒。各 source 内の時系列を
保ち、output clock は連続、transition は hard cut のみ。各 interval は一つの
`source_id`、FFmpeg input index、source range へ一意に逆引きできる。

`neutral_evidence_commentary_overlay_v1` は source video を主表示にする限定 direction。
source caption は下部二行、creator commentary は上部の compact neutral band、source label は
左上の従属表示とする。実フレームと OUT-13 の 1920x1080 / bottom-center / two-line safe-area
契約を先に確認し、opening title、PiP、split screen、motion effects、BGM、SFX、generated
imagery、MEME は使わない。

## Package

新規空 directory にだけ出力し、成功 package は次を含む。

- `final_video.mp4`
- `source_pair_selection_readback.json`
- `common_context_plan.json`
- `timeline_ir.json`
- `argument_trace.json`
- `commentary_track.json`
- `provenance_snapshot.json`
- `range_rights_inventory.json`
- `caption_readback.json`
- `commentary_presentation_readback.json`
- `validation_readback.json`
- `run_manifest.json`
- `pre_render_design_basis.json`
- `review/index.html` と localhost launcher/server
- setup / comparison / synthesis の実出力 frame と contact sheet

manifest は自身を除く closed payload set の SHA-256 / byte size を列挙し、canonical JSON
self-integrity を持つ。review は MP4 を最初に表示し、問い、仮説、source legend、cut/range/
argument relation、source caption と creator commentary の provenance、range rights、
seek control を後続で示す。

## CLI

```powershell
uvx python -m src.cli.main build-common-context-probe `
  --plan episodes\s1_two_source_common_context_probe_20260726\common_context_probe_plan_input.json `
  --design-basis episodes\s1_two_source_common_context_probe_20260726\pre_render_design_basis.json `
  --output-dir episodes\s1_two_source_common_context_probe_20260726\review\clip_s1_two_source_common_context_probe_v001 `
  --review-port 8077 `
  --format json
```

既存 output への force / resume / overwrite は持たない。URL 取得、network acquisition、
credential、cookie、OAuth、payment、upload は呼ばない。

## 検証と閉じた gate

render は二 input の各 cut を `scale` / `pad` で 1920x1080 に揃え、stretch せず H.264/AAC /
faststart MP4 にする。full decode、stream、codec、resolution、duration、timestamp monotonicity、
A/V delta、loudness / true peak、source-switch loudness delta、black/silence、両 source range の
video/audio decode、mapping coverage、caption/commentary containment を validation readback に残す。

package は `visual_observation.status=unverified`、`human_review_pending=true`、
`internal_probe_only=true`、`production_acceptance=false`、
`rights_approval=not_granted`、`public_use=false`、`monetized_use=false`、
`upload_attempted=false` を保持する。S4 人間レビューは、中心点が理解可能か、二 source が隣接
するだけでなく互いを変化・深化させるか、attribution/context が正直か、commentary が関係を
明確にしているかだけを判断する。
