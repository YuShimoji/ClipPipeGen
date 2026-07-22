---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-22
current_slice: OUT-13
phase: internal_editorial_review_ready
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
verified_implementation_head: c1566b359413e4fbd5034733ac41d03d17641aaa
base_main_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
remote_handoff_tip: this_commit_after_push
upstream_parity: 0 0
health: OUT13_CODE_VALIDATED_ARTIFACT_REVIEW_REQUIRES_RECOVERY
---

# Project Context - ClipPipeGen

## 現在の軸・レーン・スライス

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、publishing準備を
episode単位で接続する制作補助ツールである。OUT-12で取得済み実sourceから検証済みMP4までの
一コマンド経路を成立させ、OUT-13では明示的なcaption/transcript evidence付きeditorial planを
非連続cut、字幕、実MP4、review packageへ運ぶ後継経路を追加した。

現在の開発レーンは`editorial_real_video_internal_review`、active branchは
`codex/out-13-editorial-video-candidate-v1`。integration正本`main`は`5d6f69a`、active branchは
その2 commit先`c1566b3`が検証対象implementation headで、同期時のremote parityは`0 0`だった。本報告を
含むhandoff commitが次のremote tipになる。OUT-13をmainへmergeした事実や承認はない。

再開時のauthority順は`AGENTS.md` → `README.md` → `docs/RUNTIME_STATE.md` →
`docs/INVARIANTS.md` → `docs/AUTOMATION_BOUNDARY.md`。一画面の実行引継ぎは
`docs/CURRENT_HANDOFF.md`、このcheckout固有の同期・検証・目標は
`docs/SUPERVISOR_STATUS_REPORT.md`を読む。

## 最近閉じた判断と現在の未完了点

| slice | 確定したこと | 明示的に確定していないこと |
|---|---|---|
| OUT-10 / OUT-11 | five-source Shortをexact bytesへbindしてaccepted internal、winnerなしで修復loopを閉じた | universal caption/crop policy、rights、production/public use |
| OUT-12 | `build-real-video`のsource→Timeline IR→MP4→validation→review→resume縦糸をinternal operationalとして受理 | 作品内容、production subtitle/design/render、rights、thumbnail、publishing/upload |
| OUT-13 | `build-editorial-video-candidate`、explicit plan検証、字幕presentation、19項目QA、review package生成を実装しremote branchへpush | exact MP4のhuman editorial acceptance、rights、production、main統合 |

OUT-13のtracked契約は、6 cut / 4 section / 122.866016s、final SHA
`84ed7aa6...791d7e2`をsource-host実績として記録する。このroot checkoutにはsource、transcript、公式caption、
rights snapshotはあるが、`editorial_plan_input.json`とOUT-13生成packageはない。したがってコード・テストの
開発は可能だが、exact OUT-13 MP4の再視聴とhuman decisionは、生成host/packageへのアクセスまたは
hash-bound planを復元した別identityの再生成まで進められない。

## このcheckoutで確認した証拠

| 面 | 現在値 | 再開上の意味 |
|---|---|---|
| Git | implementation `c1566b3`を検証、同期時parity `0 0`; `main`は`5d6f69a` | OUT-13を未mergeのreview branchとして保持 |
| dependencies | `npm ci`成功、Electron 42.0.0、audit脆弱性0 | Node/Electron開発環境をlockfileから復元済み |
| Python | uv Python 3.13.3、`uvx --with Pillow pytest -q`で606 passed | OUT-13追加テストを含む全suite pass |
| GUI / CLI | Node/Electron smoke OK、OUT-13 CLI help解決 | GUIと新CLIの起動面は利用可能 |
| toolchain | uv/uvx 0.10.7、FFmpeg/ffprobe 8.0.1、yt-dlp 2026.03.17 | source/planが揃えば再生成可能 |
| OUT-12 local | final MP4とreadbackが存在し、SHA `5d391ffd...a584`一致 | predecessorのsame-machine evidenceは再検査可能 |
| OUT-13 local | source系入力は存在、plan/packageは不在 | exact reviewだけが未再開。コード欠陥ではない |
| hygiene | tracked/untracked変更0で開始、`episodes/` tracked 0、保護R3 session 28 files / 33,712,427 bytes | local evidenceと依存を消さずに開発可能 |

## 意図的に触っていない範囲

- NLMYTGenを含む他repository
- OUT-13 mediaの推測再生成、human decision template、main merge
- rights、production subtitle/design/render、thumbnail、winner、public/publishing/upload/OAuth
- OUT-08〜OUT-12のaccepted/operational exact identity
- protected `episodes/.../human_preview_session/`、`.serena/`、他worktree、credentials

## 次の安全な選択肢

現在の最短critical pathは`OUT-13 exact artifact access -> human editorial review -> passなら個別gate、
failならsource-specific bounded repair`である。

1. **Review** — 生成hostまたは承認済みprivate transportからexact OUT-13 packageを開き、編集構成・字幕・画面・音声を一本として判断する。
2. **Restore** — exact packageを移せない場合、欠けたplan authorityをhash付きで復元し、新artifact identityとしてOUT-13を再生成する。
3. **Audit** — mediaを待つ間にfailure receipt、plan validation、corrective-pass上限をコードとtestsから監査する。
4. **Advance after acceptance** — OUT-13受理後、rights、production subtitle design、production renderのうち一gateだけを開く。

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
`docs/CURRENT_HANDOFF.md`と`docs/SUPERVISOR_STATUS_REPORT.md`を読み、OUT-13 packageの実在を
`Test-Path`で確認してからlauncherや`--resume`を使う。package不在時にlocalhost URLを利用可能と報告しない。
