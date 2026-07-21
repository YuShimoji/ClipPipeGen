---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-21
current_slice: OUT-12
phase: internal_automation_operational
active_branch: main
source_branch: codex/out-12-one-command-real-video-automation-v1
verified_implementation_head: a51a3fdb22ff44cb9e4528ed67c0c42d48d0d67a
verified_integrated_head_before_handoff: f9cfc1194368087c49ffd98b69f880d6109cabfb
remote_handoff_tip: this_commit_after_push
upstream_parity: 0 0
health: OUT12_AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1
---

# Project Context - ClipPipeGen

## 現在の軸・レーン・スライス

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、publishing準備を
episode単位で接続する制作補助ツールである。現在の製品軸は「取得済み実sourceから、追跡可能な
Timeline IR、実MP4、validation、review packageまでを一コマンドで作る」こと。担当レーンは
`real_video_internal_automation`、現スライスはOUT-12、正本branchは`main`である。

再開時のauthority順は`AGENTS.md` → `README.md` → `docs/RUNTIME_STATE.md` →
`docs/INVARIANTS.md` → `docs/AUTOMATION_BOUNDARY.md`。一画面の入口は
`docs/CURRENT_HANDOFF.md`、詳細artifact契約は
`docs/output_layer/OUT_12_ONE_COMMAND_REAL_VIDEO_AUTOMATION.md`に置く。

## 最近閉じた判断

| slice | 確定したこと | 明示的に確定していないこと |
|---|---|---|
| OUT-10 | exact SHA `62d4b45b...97cdd`を軽いsource-specific endpoint debt込みでaccepted internal | universal endpoint/caption policy |
| OUT-11 | SOURCE-04、OUT-10、SOURCE-05をexact bytesへbindし、5-source accepted internal・winnerなしでShort repair loopを閉じた | winner、共通crop/字幕/speaker-color policy、rights、production/public use |
| OUT-12 | `build-real-video`の実source→long-form MP4→validation→review→resume縦糸をinternal operationalとして受理 | 作品内容のhuman acceptance、rights、production subtitle/design/render、thumbnail、publishing/upload |

OUT-12は汎用frameworkを先行拡張せず、creator-visibleな一コマンド経路を成立させたthin sliceである。
source-native textは保持するが、歌唱、歌詞、話者、意味、利用許諾を自動推定しない。

## OUT-12 exact evidence

| 面 | 現在値 | 意味 |
|---|---|---|
| artifact | `clip-out12-one-command-real-video-automation-v1-001` | current internal automation proof |
| source | `youtube:gUwJBRUIWow`; SHA `8decc04d...d0037cf`; 260.643991s | 3分以上を満たしたpreflight唯一の候補 |
| timeline | full-source scene partition、11 cuts、3 sections、coverage 1.0 | chronologyとsource mappingを機械追跡可能 |
| final MP4 | 260.693767s、1920x1080、H.264/AAC、142,789,781 bytes、SHA `5d391ffd...a584` | exact internal output identity |
| validation | 13 checks passed、full decode/faststart、timestamp regression 0、AV delta 0.008767s | shipping media plumbing pass |
| audio/signal | -14.15 LUFS / -1.44 dBTP、max adjacent cut 1.27 LU、max black 0.7007s、silence 0 | initial AV/peak failuresをcorrective passで解消 |
| captions | timing cue 468、overlap/negative/orphan 0、native baked text保持 | containment証拠であり意味acceptanceではない |
| resume | 2.095s、analysis/caption/render/validation cache hit、render false、同一SHA | 高コストstageのfail-closed再利用 |
| review | HTTP 200 / Range 206、desktop 1280 / mobile 390、paused/muted/time0、seek、console/media error 0 | same-machine operator surface pass |

## Portableとlocal-onlyの境界

Gitで別端末へ渡るもの:

- CLI、render integration、tests、docs、exact hashes、authority/gate contract
- OUT-10/11 acceptance receiptとOUT-12再生成・resume手順
- dashboard、artifact registry、decision/idea/handoff state

同一マシンにしか存在しないもの:

- `episodes/`内のsource MP4、final MP4、contact sheets、waveform、localhost package
- source取得済みbytesとignored failure/debug evidence

`episodes/`は引き続きignoredで、tracked fileは0件を保つ。別端末はcode/contextから即再開できるが、
同じ映像を再生するにはexact source bytesの安全な移送、または契約に沿った再取得・再生成が必要。
mediaをGitへ追加しない。

## 意図的に触っていない範囲

- NLMYTGenを含む他repository
- rights、production subtitle/design/render、thumbnail、winner、public/publishing/upload/OAuth
- OUT-08/09/SOURCE-04のaccepted bytesとOUT-10/11 closure
- protected `episodes/.../human_preview_session/`と既存local review evidence

## 次の安全な選択肢

現在ブロッカーや必須human decisionはない。次のsliceは一つだけ選ぶ。

1. **Advance** — 別の3分以上real sourceで`build-real-video`を実走し、source-specific偶然でないか確認する。
2. **Audit** — current OUT-12動画を任意内容確認し、cut/tempo/contentのsource-specific観測だけを記録する。
3. **Verify** — rights、production subtitle design、production renderのいずれか一gateを明示開始する。
4. **Explore** — private artifact transportを設計し、別端末でもsame bytesをreviewできるようにする。

## 別端末での最短再開

```powershell
git fetch --prune origin
git switch main
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git log -1 --oneline --decorate
git ls-files episodes
```

期待値は`main`、upstream parity `0 0`、tracked `episodes/` 0件。次に
`docs/CURRENT_HANDOFF.md`を読み、同一マシンでartifactが必要な場合だけ記載launcherを使う。
