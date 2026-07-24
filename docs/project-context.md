---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-24
current_slice: OUT-13
phase: human_editorial_review_pending
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
verified_implementation_head: 3fdad157c09cc925a50750135e14fff5faa832f2
sync_baseline_head: 3fdad157c09cc925a50750135e14fff5faa832f2
base_main_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
remote_handoff_tip: this_commit_after_push
upstream_parity: 0 0
health: OUT13_CANDIDATE_005_LOCAL_REVIEWABLE_CODE_PORTABLE
---

# Project Context - ClipPipeGen

## 現在の軸・レーン・スライス

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、publishing準備を
episode単位で接続する制作補助ツールである。OUT-12で取得済み実sourceから検証済みMP4までの
一コマンド経路を成立させ、OUT-13では明示的なcaption/transcript evidence付きeditorial planを
非連続cut、字幕、実MP4、review packageへ運ぶ後継経路を追加した。

現在の開発レーンは`editorial_real_video_internal_review`、active branchは
`codex/out-13-editorial-video-candidate-v1`。integration正本`main` / `origin/main`は
`5d6f69a`、active branchは`3fdad15`でmainより8 commit先にある。OUT-13はmainへ未統合で、
今回のhandoff docs更新後のcommitが次のremote resume tipになる。

再開時のauthority順は`AGENTS.md` → `README.md` → `docs/RUNTIME_STATE.md` →
`docs/INVARIANTS.md` → `docs/AUTOMATION_BOUNDARY.md`。一画面の実行引継ぎは
`docs/CURRENT_HANDOFF.md`、監修・同期・目標の証跡は`docs/SUPERVISOR_STATUS_REPORT.md`を読む。

## 最近閉じた判断と現在の未完了点

| slice | 確定したこと | 明示的に確定していないこと |
|---|---|---|
| OUT-10 / OUT-11 | five-source Shortをexact bytesへbindしてaccepted internal、winnerなしで修復loopを閉じた | universal caption/crop policy、rights、production/public use |
| OUT-12 | `build-real-video`のsource→Timeline IR→MP4→validation→review→resume縦糸をinternal operationalとして受理 | 作品内容、production subtitle/design/render、rights、thumbnail、publishing/upload |
| OUT-13 | `build-editorial-video-candidate`、explicit plan検証、字幕presentation、強化されたauthority/lineage/immutability契約、review package生成をremote branchへpush | candidate 005のhuman editorial acceptance、rights、production、main統合 |

現在の正本候補は`clip-out13-editorial-video-candidate-v1-005`。7 cut / 5 semantic sections /
8 omitted ranges、Timeline IR 128.795s、最終MP4 128.833333s、SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`である。candidate 004は
parallel review targetとして保持するが、005を受理済みとは扱わない。

## このcheckoutで確認した証拠

| 面 | 現在値 | 再開上の意味 |
|---|---|---|
| Git | HEAD / origin branch `3fdad157...832f2`、tracking parity `0 0`、worktree clean | 同じbranchを別端末から再取得できる |
| mainとの差 | `origin/main...HEAD = 0 8`、mainは`5d6f69a` | OUT-13はreview branchであり、main統合済みではない |
| package | candidate 005は25 files / 87,123,995 bytes、package tree digest `ed45fd4c...040` | このThank端末では即レビュー可能 |
| media | H.264 High / AAC / yuv420p / 1920x1080、128.833333s、MP4 SHA `a76babda...bbb5` | exact candidate identityを人間判断へ渡せる |
| machine readback | `validation_readback.status=passed`、caption 102 cues、mapping 1.0、full decode / faststart / signal pass | 技術的review surfaceは成立。human acceptanceではない |
| browser | page 200、MP4 Range 206、横overflowなし、初期paused/muted、media warning/error 0 | launcherとreview surfaceの再開確認済み |
| human gate | `visual_observation=unverified`、human全編視聴未実施、rights pending | accept / bounded repair / rejectが次の判断 |
| hygiene | `git ls-files episodes` = 0、candidate packageは`.gitignore`対象のlocal evidence | code/docsはportable、media/inputはprivate transfer対象 |

## 意図的に触っていない範囲

- NLMYTGenを含む他repository
- `episodes/` の生成media、candidate 004 / 005の上書き・削除・Git追跡
- rights、production subtitle/design/render、thumbnail、winner、public/publishing/upload/OAuth
- OUT-08〜OUT-12のaccepted/operational exact identity
- `.serena/`、他worktree、credentials、保護されたpreview session

## 次の安全な選択肢

現在の最短critical pathは`candidate 005 human editorial review -> 必要なら006以降のbounded repair ->
feature branch acceptance -> main integration判断`である。rights、production、publicは独立gateとして
閉じたままにする。

1. **Review** — Thank端末でcandidate 005を全編視聴し、accept / repair / rejectをfinal SHAへbindする。
2. **Restore** — 別端末で映像確認が必要なら、candidate 005のexact packageとinputsを承認済みprivate transferで回収し、全SHAを照合する。
3. **Rebuild** — exact transferを選ばない場合は、新plan・new artifact identityとして再生成し、旧SHAの復元とは主張しない。
4. **Advance after acceptance** — editorial closure後、rights、production subtitle design、production renderのうち一gateだけを開く。

## 別端末での最短再開

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

期待値はactive branchのparity `0 0`、tracked `episodes/` 0件。次に
`docs/CURRENT_HANDOFF.md`と`docs/SUPERVISOR_STATUS_REPORT.md`を読み、candidate 005 packageの実在を
`Test-Path`とSHAで確認する。packageがない端末ではlauncherを実行可能と報告せず、private transferまたは
new identity rebuildのowner判断を待つ。
