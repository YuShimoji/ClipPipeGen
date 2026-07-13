# 監修AI向け現状報告 — 2026-07-13

## 今どこまで進んでいるか

リモートから取り込んだ実装基点は、当時の最終更新ブランチ
`codex/out-07-internal-operator-delivery-pack-v0` の `f0f7d31` です。
このブランチは canonical `main` の OUT-06 accepted baseline より 5 commit
先にあり、OUT-07 operator delivery pack、Shorts poster direction proof、状態修正、
参照忠実度の補強まで含みます。ローカルブランチは同名の origin branch を追跡し、
切替時点で ahead/behind はともに 0 です。

現在の判断対象は、旧 16:9 サムネイル案ではありません。`context`、`tension`、
`payoff` の3案は `user_rejected` として履歴に残り、推奨案と
`selected_thumbnail` はともに `null` です。次の判断は、参照調査から作られた
1080x1920 の Shorts poster A/B/C のうち実用候補に最も近いものを選ぶか、
全案不採用とするかに限定されています。末尾 poster の出現が不自然な場合だけ、
その違和感も併記してください。

OUT-06 で受入済みの 38.633333 秒動画は OUT-07 でも byte-identical とされ、
記録済み SHA-256 は
`02cfc1b25afbc7b280481453cb53c8f66d915a39389098cb70e2f37b31504bf0`
です。poster proof はこの動画末尾 1.75 秒から 0.12 秒 dissolve、0.50 秒 poster
end-cap、0.16 秒 audio fade を用いる 2.133 秒の比較証跡です。タイトル、説明、
タグ、full-video integration、権利、production/public acceptance、upload、
visibility、made-for-kids、publishing は今回の判断範囲に含みません。

## 開発再開に使える状態

| 確認対象 | このマシンでの結果 | 開発判断への意味 |
|---|---|---|
| Git | OUT-07 branch `f0f7d31`、origin 追跡済み | 最新の未マージレビュー系列から継続できる |
| Python | Python 3.11.0 / uv 0.10.0、`461 passed` | stdlib 中心の本体と Pillow 使用経路を含め、現 HEAD の回帰は検出されなかった |
| GUI | `npm run smoke` と `npm run smoke:electron` が成功 | Node 側の構造確認と Electron 起動確認の双方が通る |
| Node dependencies | `npm ci` 完了、間接依存 `undici` を 7.28.0 へ更新後 `npm audit` 0件 | lockfile から再現でき、検出されていた high advisory を残さず開発を始められる |
| Media tools | FFmpeg / FFprobe 8.1.1 を検出 | render 系テストとローカル media probe の実行条件がある |

`package.json` の直接依存、CLI、schema、DB、認証、外部 API 契約は変更していません。
依存変更は Electron が参照する optional/dev の間接依存を修正版へ固定したものだけです。

## 追跡可能な証跡と、このマシンにない証跡

| 種別 | 状態 | 参照先または復旧条件 |
|---|---|---|
| Runtime と review scope | tracked / portable | `docs/RUNTIME_STATE.md` と `docs/CURRENT_HANDOFF.md` |
| OUT-07 実装・corpus・tests | tracked / portable | `src/integrations/render/shorts_poster_frame_proof.py`、`docs/output_layer/OUT_07_SHORTS_POSTER_REFERENCE_CORPUS.json`、関連 tests |
| OUT-07 A/B/C review package | このマシンでは missing | 本来は `episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/` |
| 再生成入力 | 一部 missing | source video は存在するが、OUT-06 accepted package、OUT-07 publish draft、凍結済み reference cache がない |

`episodes/` は意図的に Git 管理外で、source-derived media や第三者 reference pixels
を public Git に混ぜない契約です。そのため tracked builder の健全性はローカル test で
確認できましたが、このマシンから今すぐ `http://127.0.0.1:8071/index.html` を開いて
視覚監修することはできません。さらに、最新の参照忠実度修正後は whole-package の
deterministic digest が未再検証です。これはコード開発の blocker ではありませんが、
人間による A/B/C 判断の前には同一マシン成果物の復旧または再生成が必要です。

## 監修で次に見る一点

成果物が復旧したら、`open_preview.ps1 -Serve -Port 8071` を単一入口として開き、
次の問いだけに回答してください。

> A/B/Cのどれが実用候補に最も近いか、または全案不採用か。末尾posterの出現が不自然な場合だけ併記してください。

tests は artifact integrity と再現可能なロジックを支える証拠であり、見栄えの受入や
勝者を自動的に証明するものではありません。

## 次に進める入口

- **Verify — 同一マシン成果物を復旧する:** OUT-06 accepted package と凍結済み
  reference cache を正規保存元から戻せれば、ネットワーク再収集をせず OUT-07 package
  digest と localhost review を再検証できます。
- **Audit — A/B/C を監修する:** package 復旧後に問いを一つへ絞って選択すれば、
  H1 full-video integration に進める案、または全案撤回の判断が確定します。
- **Advance — tracked 実装をレビューする:** 視覚成果物の移送を待つ間も、OUT-07 の
  builder、reference corpus、mask/reference fidelity、copy fallback の code review は
  継続でき、branch review pending の技術側摩擦を減らせます。
