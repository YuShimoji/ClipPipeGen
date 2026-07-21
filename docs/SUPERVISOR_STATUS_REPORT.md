# 監修AI向け現状報告 — OUT-12 operational remote handoff

更新日: 2026-07-21 JST

正本branchは`main`。handoff更新直前の`main` / `origin/main`は
`f9cfc1194368087c49ffd98b69f880d6109cabfb`、parity `0 0`、tracked `episodes/` 0件である。
最終handoff commitをpullした別端末は、`docs/CURRENT_HANDOFF.md`からOUT-12の実装状態、判断境界、
次の一手を復元できる。実sourceと生成mediaだけはGitへ含めず、同一マシン証拠として保持する。

## この端末での同期・開発準備

2026-07-21 JSTに`main`を`b3cec5de0e7d79c0d570aa5ec4b91d5287c77eb2`から最終handoff
commit `8faaab254320ddec03a5a3d0de1c671b9990e3e1`へfast-forwardした。取り込み後は
`main...origin/main`、ahead / behind `0 0`、tracked worktree clean、tracked `episodes/` 0件である。
依存とtoolchainを更新後のlockfile・実装入口に合わせ、次の結果をこの端末で再検証した。

| 確認面 | この端末での結果 | 開発・監修上の意味 |
|---|---|---|
| JavaScript依存 | `npm ci`成功、24 packages audit、脆弱性0 | `package-lock.json`どおりのElectron開発環境 |
| Python実装 | Python 3.11.0 / uv 0.10.0、`uvx --with Pillow pytest -q`で596 passed | 取り込んだOUT-09〜OUT-12を含む全suiteがlocal pass |
| GUI | `npm run smoke` / `npm run smoke:electron`ともにOK | Node側とElectron起動経路が利用可能 |
| media toolchain | FFmpeg / ffprobe 8.1.1、yt-dlp 2026.03.17を検出 | 新しい実sourceが用意されればOUT-12 routeを実行可能 |
| CLI入口 | `python -m src.cli.main build-real-video --help`成功 | source / intake identity、resume / force、review生成の引数を解決可能 |
| cleanup | pytest / ruff / Python cacheだけを明示パスで削除 | 保護対象previewと`node_modules`を維持したcleanな開発状態 |

local artifact境界も確認した。OUT-12の`validation_readback.json`、final MP4、`review/index.html`は
この端末には存在しないため、`127.0.0.1:8075`を現在利用可能なreview URLとしては扱わない。一方、
保護対象のR3 `human_preview_session/index.html`は存在し、cleanup対象から除外した。したがって現在は
**tracked codeの開発・テストは可能、OUT-12 exact mediaの再視聴だけは生成元hostまたはsource復元が必要**
という状態であり、remote handoffのportable / same-machine境界と一致する。

## 到達した状態

OUT-10 / OUT-11では5 sourceのShort候補をexact bytesへbindしてinternal acceptanceを閉じ、winnerを
選ばず、追加Short修復・再レビューを終了した。その入力境界からOUT-12を開き、取得済みの実source
一本をprovenance確認から長尺MP4、machine validation、localhost reviewまで一コマンドで処理する
vertical sliceを完成させた。状態は`AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1`で、automation
acceptanceはtrue、人間内容レビュー待ちはfalseである。

`build-real-video`はsource fingerprint、content/scene/black/silence解析、chronological Timeline IR、
caption timing remap、H.264/AAC render、13項目validation、manifest、review packageをatomicに作る。
成功済みpackageは`--resume`でpayloadとfingerprintが一致するときだけ再利用し、不一致はfail closedに
する。異なる入力を上書き生成する場合だけ、意図を確認したうえで`--force`を使う。

## 現在のexact artifact

| 面 | 確定値 | 監修上の意味 |
|---|---|---|
| artifact | `clip-out12-one-command-real-video-automation-v1-001` | OUT-12 automation acceptanceのidentity |
| source | `youtube:gUwJBRUIWow`; SHA `8decc04ddcd805cadb77100eb5f7cbf2dc9883a32cb42aba0ed4c216fd0037cf`; 260.643991s | 3分以上の実sourceとしてpreflight済み |
| timeline | 11 cut / 3 semantic sections / coverage 1.0 | full-source chronologyとsource mappingを保持 |
| output | 260.693767s; 1920x1080; H.264/AAC; 142,789,781 bytes | internal long-form実動画が生成済み |
| output SHA | `5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584` | local artifactを再確認するときのexact identity |
| captions | 468 timing cues; overlap / negative / orphan 0 | timing/containmentのみ。歌唱・歌詞・speaker・意味は未主張 |
| signal | -14.15 LUFS; -1.44 dBTP; 最大隣接cut差1.27 LU; black 0.7007s; silence 0 | internal machine QA pass。production mix承認ではない |
| resume | 2.095s; analysis/caption/render/validation cache hit; render false;同一SHA | 高コスト処理のhash-verified再利用を確認 |
| review | HTTP 200 / Range 206; desktop/mobile overflowなし; initial paused/muted/time0; console/media error 0 | localhost reviewのaccessとsafe media stateを確認 |

review入口は同一マシンで`http://127.0.0.1:8075/review/index.html`。server停止後は次でforeground再開する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation\review\serve_preview.ps1
```

## 実装と失敗修復の意味

初回runでAV stream duration差とtrue peak超過を検出したため、失敗証跡を消さずにcorrective passを
実行し、duration差0.008767秒、true peak -1.44 dBTPへ修復した。mobile review表のdocument overflowと、
Windows browserがRange requestを中断した際のserver traceも生成CSSとconnection handlingで直した。
いずれもSOURCE-05だけを通す手作業ではなく、次の実source runにも適用されるroute修復である。

この成果は作品内容の良否を自動判定したものではない。source-native baked textを保持し、caption authorityは
timing/containmentへ限定した。OUT-12の任意内容確認はできるが、automation acceptanceを再びreview待ちに
戻したり、意味・rights・production qualityを推論したりしない。

## 別端末へ移るものと移らないもの

| 対象 | Gitで移るか | 再開方法 |
|---|---|---|
| code / tests / authority docs / schemas | 移る | `main`をfetchしてff-only pull |
| exact artifact identity / validation数値 /判断経緯 | 移る | Runtime、Current Handoff、output contract、decision logを読む |
| source MP4 / final MP4 / contact sheet / waveform / localhost package | 移らない | 同一マシン`episodes/`を保持。別hostでは再取得・再生成または承認済みprivate transport |
| credentials / OAuth / upload state | 存在させていない | 新しい外部連携gateが承認されるまで作らない |

新しい端末では次を実行する。

```powershell
git fetch --prune origin
git switch main
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

期待値はclean worktree、parity `0 0`、tracked `episodes/` 0件。`episodes/`が空でもcode/context再開の
欠陥ではなく、media再検査だけが同一マシンまたは再生成を要求する。

## 未承認gateと次の取っ掛かり

| 入口 | 目的 | 効果 | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|---|
| Advance | 異なる3分以上の実sourceで同じrouteを通す | source固有成功ではなくrepeatabilityを観測 | rights snapshotを含む取得済み実source一本 | proposed | preflight後、別artifact idで一回run |
| Audit | OUT-12 failure taxonomyとcorrective passを監査 | 次sourceでの失敗分類・再実行判断を安定化 | 現在のreadback/manifestだけで可能 | 未着手・低リスク | code変更なしの監査packetを作る |
| Verify | 別hostでmedia再検査可能にする | Gitに大容量mediaを入れずreview portabilityを得る | private transport方式と保持期間のowner承認 | 未承認 | transport gateを別sliceで設計 |
| Explore | production subtitle designまたはrender品質を開く | internal automationからproduction候補へ一段進む | 対象gate、評価基準、owner acceptanceを明示 | 閉じている | subtitle/design/renderを一括にせず一つ選ぶ |
| Release | rights / thumbnail / public publishingを閉じる | 公開候補として扱える | rights、production、thumbnail、visibility/upload各証拠 | 全て未承認 | 前段の個別gateが閉じるまで実施しない |

現在の推奨は`Advance`。別source一本を同じCLIで処理すると、OUT-12の最大の残余不確実性である
source repeatabilityを最小範囲で測れる。rights、production subtitle/design/render、thumbnail、winner、
public/publishing、uploadは依然として別owner gateで、本handoffやinternal validationから承認を推論しない。

## 監修AIが維持する境界

- 正本は`main`と`docs/RUNTIME_STATE.md` / `docs/CURRENT_HANDOFF.md`。古いresume capsuleをcurrent扱いしない。
- OUT-10 / OUT-11のaccepted exact bytesとOUT-12 automation acceptanceを、理由なく再審査へ戻さない。
- `episodes/`をtrackせず、`git ls-files episodes`を0件に保つ。
- source textから歌唱、歌詞、speaker identity、rightsを追加推定しない。
- gateを一括で開かず、目的とacceptanceが明示された一つのsliceだけ進める。
