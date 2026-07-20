# 監修AI向け現状報告 — OUT-11 five-source combined review ready

更新日: 2026-07-20

対象: ClipPipeGen / `codex/out-11-five-source-short-portfolio-wave-v0`

状態: `OUT11_FIVE_SOURCE_SHORT_PORTFOLIO_COMBINED_REVIEW_READY`

## 結論

OUT-10の最終発話不足をexact endpoint evidenceで修復した後、上限内の公式source探索から
第4・第5の異なるreal recordingを取得し、source別のcaption/composition/endpoint方針で
reviewable Short二本を生成した。5-source scorecardと、未判断三本だけを並べるcombined reviewは
生成・ブラウザ検証済みである。

開いているgateは一つだけ。OUT-10/04/05のexact三SHAを同じ画面で上から順に見て、一本ごとの
成立性と違和感を自由記述するhuman reviewである。OUT-08/09はaccepted contextとして保持し、
再視聴・再受理しない。production、rights、thumbnail、public/publishing、winnerは未承認。

## 今回の変更と効果

| 作業 | 目的 | 実際の効果 | 現在状態 | 次の動き |
|---|---|---|---|---|
| OUT-10 final response repair | 27.711s終端後に残った返答を完了 | source 30.014s / 46 cue / new exact SHA | combined review先頭 | 自然な完結を人間確認 |
| endpoint preflight / evidence manifest | 終端判断を画像だけでなくhash-bound evidence化 | candidates/selection/source mappingをstrict検証 | reusable | 後続sourceでも利用可 |
| source-adaptive candidate builder | caption有無・native baked・neutral matteをsourceごとに選ぶ | 第4/5 sourceを共通contractでrender | tests pass | human semanticsのみ残る |
| shared loudness gate repair | pass-throughとfinal QAの隙間を解消 | SOURCE-04を1 correctiveでQA帯へ | regression test追加 | production mix承認ではない |
| five-source scorecard | 5 sourceの証拠と負債を同じ列で比較 | accepted 2 / pending 3、winnerなし | review package内 | acceptance後のsystem audit基礎 |
| combined review | 判断面の分散を解消 | 一画面・三動画・一質問・安全初期状態 | localhost ready | 一度だけhuman review |

## Exact identities

| slot | recording / range | MP4 SHA | acceptance |
|---|---|---|---|
| OUT-08 | `youtube:7J5aS_pcBj4` / 2 accepted candidates | `f7ea3f70...e388a`, `47c844b1...d593b` | accepted_internal context only |
| OUT-09 | `youtube:D4i4fjs9PWc` / 33.333008s | `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50` | accepted_internal context only |
| OUT-10 | `youtube:TlnviOwLRmk` / `0.000–30.014s` | `a53d0416e17dcc682fa172ca47c7dd268a9dff2cf926bd3c44c6f5a2711134f2` | human_review_pending |
| SOURCE-04 | `youtube:PQ54uUV41-k` / `0.000–18.500s` | `465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524` | human_review_pending |
| SOURCE-05 | `youtube:gUwJBRUIWow` / `202.586–217.650s` | `370850c5222b70d944f7ba879849f33a2b448edae355e4e41dc35977bf22b578` | human_review_pending |

## 成果物

| artifact_id | repo_relative_path / local path | 開き方 |
|---|---|---|
| `clip-out10-third-source-short-portfolio-expansion-v0-001` | `docs/output_layer/OUT_10_THIRD_SOURCE_PORTFOLIO_EXPANSION.md`; ignored OUT-10 package | combined reviewにexact copy |
| `clip-out11-source04-indonesia-laugh-short-v0-001` | `episodes/out11_source04_indonesia_laugh_20260720/review/out11_source04_candidate/` | combined reviewの2本目 |
| `clip-out11-source05-dramatic-xviltration-short-v0-001` | `episodes/out11_source05_dramatic_xviltration_20260720/review/out11_source05_candidate/` | combined reviewの3本目 |
| `clip-out11-five-source-short-portfolio-wave-v0-001` | `episodes/out11_five_source_short_portfolio_20260720/review/out11_five_source_short_portfolio/` | `open_preview.ps1 -Serve` / URL `http://127.0.0.1:8074/index.html` |

combined manifest self SHAは
`b690230e944bcd6f3df4e5ec6fa8b0877831db16544a9fefb3ef08de08666a0c`、
scorecard SHAは`a40c7e84f66a60384c8b7aecd94730934f0a42b71aeae7a0a2769bdaad837678`。

## Commands run and results

- `init-episode`でOUT-11 combined episodeを作成。
- `build-endpoint-preflight` / `build-endpoint-evidence-manifest`で各sourceの終端証拠を生成。
- `bind-source-adaptive-candidate-plan`でsource/caption/endpoint hashをplanへ固定。
- `build-source-adaptive-short-candidate`でSOURCE-04/05を生成。
- `build-five-source-short-portfolio`で三MP4 exact copyと5行scorecardを一括生成。
- OUT-11 direct test群はpass。Ruffもpass。
- page HTTP 200、三MP4のRange 206、source copy hash/size一致。
- in-app browserでdesktop/mobile/no-overflow/safe initialization/exclusive playback/console 0を確認。
- ffmpegで三本の終端3秒contact sheet/waveformを生成・実見。
- 検証listenerは停止し、port 8074 listener 0を確認。
- docs dashboardは連続2回の生成で4出力すべてbyte-stable。
- `uvx --with Pillow pytest -q` は579 passed。初回のPillowなし起動はcollectionで停止したため、
  repo既定の一時依存を明示して有効な全suiteを実行した。過去のOUT-06環境依存2件も再現なし。

## 残る不確実性

| 残作業 | なぜ自動決定しないか | owner | 次のmove |
|---|---|---|---|
| 三本の自然な成立性 | 意味・テンポ・可読性・音の印象は人間判断 | human reviewer | 統合質問へ自由記述 |
| SOURCE-04 speaker differentiation | cue単位speaker authorityなし | later subtitle-design owner | production gate時に推測なしで比較 |
| SOURCE-05 lyric/motion closure | 音楽句と白transitionの印象は主観 | human reviewer | 候補名と時点を回答 |
| rights | 公開利用の判断はlocal renderから導けない | rights owner | 別gateで確認 |
| production/public | internal reviewはproduction/public acceptanceではない | owner | human acceptance後も別承認 |
| media portability | `episodes/`はignored | artifact owner | private/artifact-store戦略が明示された時だけ扱う |

## 監修者が次に行うこと

1. combined reviewを一回だけ開く。
2. OUT-10、SOURCE-04、SOURCE-05を上から順に見る。
3. 統合質問へ候補別の自由記述を返す。
4. 回答をexact三SHAへbindして、候補別accept / bounded repair / rejectを決める。
5. 全受理の場合だけ、OUT-10 closureを先、OUT-11 closureを後に扱う統合計画へ進む。

## 閉じたgate

rights、production render/subtitle/image quality、thumbnail、winner、public/publishing、upload、OAuth、
visibility、made-for-kids、cross-machine media portability、PR/main mergeはこの作業では開いていない。
