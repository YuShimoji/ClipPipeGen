# Planner007 remote sync / development readiness / supervising handoff — 2026-07-17

## これは何か

この文書は `DESKTOP-U9P4LKJ` で実測した非正本の監修用 receipt である。portable な
現在値は [RUNTIME_STATE.md](RUNTIME_STATE.md)、実行再開点は
[CURRENT_HANDOFF.md](CURRENT_HANDOFF.md) を正本とする。今回、episode media、candidate
plan、human decision、rights / production / public gate は変更していない。

## 今の状態

現行ブランチ `codex/out-08-private-review-package-recovery-v0` は fetch / prune 後に
upstream `0 0`、`git pull --ff-only` は `Already up to date` だった。HEAD は
`180bd28`、`origin/main` の `4fad107` より 8 commits 先行しており、OUT-08 の
mini-batch、`cut_009` 完全除外修正、cross-terminal handoff、Planner007 readiness、
exact private package recovery を含む。追跡・未追跡の作業差分は開始時点で無く、
`git ls-files episodes` も 0 件のままである。

同じ source baseline から分岐した
`origin/codex/out-08-real-unused-range-short-minibatch-v0` には `a96e6f9` と
`2d45bd8` の監修報告更新だけが存在する。fetch により object はローカルへ取得済み
だが、その報告は Thank 上で package を直接開けた復旧前の状態を記述するため、現行
recovery branch へ機械的に merge していない。未取得の実装変更があるのではなく、
現行状態では本書と recovery contract が後継となる。

コードと開発環境はローカルで実行可能である。一方、OUT-08 の exact 17-file review
package は Thank にだけ残り、Planner007 の probe は `package_missing` /
`server_stopped` である。したがって、開発を継続できる状態と、候補動画をこの端末で
人間レビューできる状態は分けて扱う必要がある。現在の唯一の product bottleneck は
一度の私的 package 移送であり、再 render や Git への media 追加ではない。

| 監修判断 | 実測された現在値 | 次工程への意味 |
|---|---|---|
| remote 同期 | active upstream `0 0`、pull は更新不要、HEAD `180bd28` | 現行 recovery branch から安全に開発を続けられる |
| 開発環境 | `npm ci` で 23 packages を再配置、24 packages audit、脆弱性 0 | Node / Electron GUI を lockfile どおり再現できる |
| Python behavior | 全体 `542 passed in 53.91s`、OUT-08 focus `58 passed in 7.49s` | tracked behavior と recovery guard が現在ホストで green |
| entrypoint / lint | CLI help 正常、現行差分 11 Python files の Ruff は全 pass | OUT-08 変更範囲は追加修正なしで着手可能 |
| GUI | Node-only smoke / Electron smoke ともに pass | GUI の通常開発・起動 smoke は可能 |
| 全体 lint debt | `src tests` 全体では既存 14 findings / 9 files | 実行 blocker ではない。CI lint gate 化前に独立保守スライスで解消する |
| docs health | dashboard 再生成は成功、既存 27 findings（stale / unclear / over-guarded） | H0 を止めない。長大 HANDOFF の archive 化等は product decision 後の保守候補 |
| current-host review | probe は `package_missing` / `server_stopped`、current URL は null | exact import と server probe が終わるまで human playback を開始しない |
| public hygiene | `episodes/` は ignored、tracked 0、広域 ignored cleanup 未実施 | source-derived media と保護対象 review evidence を Git に漏らしていない |

検証ホストの toolchain は uvx `0.10.0`、Python `3.11.0`、Node `22.19.0`、npm
`10.9.3`、FFmpeg / FFprobe `8.1.1`。以前の Thank receipt と version が異なるため、
将来 version-dependent な media 差分が出た場合は host/toolchain を provenance に
含める。今回は media generation を行っておらず、candidate bytes は変化していない。

## Constraints / Risks（確定証拠と、まだ成立していないこと）

Thank evidence には candidate 01
`f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a`、candidate 02
`47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b`、manifest
self-integrity
`22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4` が保持されて
いる。candidate 02 の最大 source end は `135.219`、reject 済み `cut_009` の
`135.219–144.000` と source-time overlap しない。recovery kit は exact allowlist、
hash / size / self-integrity、host identity、archive safety、atomic promotion、existing
package preservation を fail-closed で検証し、別 revision の生成を許さない。

Planner007 では次の probe を 2026-07-17 に再実行し、仕様どおり
`recovery_kit_ready_package_not_yet_imported` を得た。

```powershell
uvx python -m src.cli.main recover-out08-private-review-package --format json probe
```

これは build failure ではないが、current `human_entrypoint`、direct playback / seek、
candidate acceptance は未成立である。rights は `pending`、production subtitle design、
production render、public/publishing、upload、visibility、made-for-kids、thumbnail
selection はすべて未承認または閉鎖中である。navigation JPG は移動補助であって
thumbnail candidate ではない。

## 次に進める入口

1. Thank で explicit な repo 外の新規 ZIP へ exact package を export する。
2. 利用者が選ぶ private channel で ZIP を一度だけ Planner007 へコピーする。
3. Planner007 で atomic import と server start を行い、probe が
   `package_verified_exact` / `server_running_verified` になったことを確認する。
4. candidate 01 / 02 を一本ずつ direct playback / seek し、テンポ、開始終端、字幕、
   音声の違和感を自由記述する。
5. 返答を candidate 単位の decision packet に正規化し、accept-internal、bounded
   repair、park/reject のどれか一つへ閉じる。

```powershell
# Thank
uvx python -m src.cli.main recover-out08-private-review-package --format json export --destination D:\private-transfer\out08-review.zip

# Planner007 after a user-owned private copy
uvx python -m src.cli.main recover-out08-private-review-package --format json import --archive D:\private-transfer\out08-review.zip --start-server
```

transfer channel の選択・upload・credential 操作は repository の責務外であり、
自動化しない。Planner-known source と Thank source の byte equivalence も未確立なので、
Planner source から再生成した候補を exact recovery と呼ばない。

## 可能な限り先まで見た目標階層（未承認提案）

以下は順序を監修する goal ladder であり、FEATURE の `approved`、production/public
操作、OAuth、rights 判断を許可するものではない。各段は前段の証拠と owner 判断を
受け取ってから一つずつ起票する。

| 地平 | 目標と完了条件 | 主な依存・停止条件 | 完了後に開ける開発 |
|---|---|---|---|
| H0: OUT-08 decision closure | exact 2 candidates を再生し、各々を accept-internal / bounded repair / park-reject に分類。修正するなら tempo / boundary / subtitle / audio の一領域だけを successor slice にする | private transfer、exact import、server probe、人間の自由記述 | 単発の感想を edit/render へ戻せる decision packet として固定できる |
| H1: real Shorts portfolio 3–5 本 | 少なくとも 3 本、できれば複数 episode で、尺・境界・字幕密度・cover 方向・判断理由を共通 scorecard 化する | H0 closure、rights readback 維持、個別候補への過適合を避ける | 再利用可能な編集規則を抽出し、OUT-07 thumbnail exploration 再開の是非を初めて評価できる |
| H2: production limitation lift | subtitle design、render、rights を独立 packet で acceptance。safe-area、line break、font/license、A/V/seek/full-decode を明示基準化する | H1 の反復証拠と人間 owner。どれか一 gate の pass を他 gate へ継承しない | internal candidate を production candidate へ昇格するための再現可能な品質 gate ができる |
| H3: portable episode delivery | tracked manifest と private payload receipt を分離し、provenance / access / retention / rollback 付きで別端末復旧を実証する | private artifact store / transport の明示承認、`episodes/` public Git 禁止、SH-02 契約 | 一回限りの OUT-08 recovery を episode 共通 handoff へ一般化できる |
| H4: controlled private publishing rehearsal | metadata-only dry-run の後、production-accepted video / thumbnail / metadata を private-unlisted upload、readback、rollback receipt まで接続する | H2/H3、PB-01..04、INT-01、OAuth/credentials、rights/publication の明示承認 | 公開前に failure と rollback を観測できる publishing integration が成立する |
| H5: multi-episode production-assist loop | 2–3 episodes で source→ledger→transcript→edit→review→production→private publish を反復し、lead time、手動判断数、再生成一致率、recovery 成功率を計測する | H4 成功、official caption が無い素材の STT quality route、failure telemetry | 繰り返し発生した境界だけを GUI / automation に昇格し、判断証拠を失わず制作摩擦を減らせる |

監修上の推奨は H0 の前半、すなわち exact transfer / import / probe を最優先にすること。
review 返答前に lint cleanup や portfolio expansion を混ぜると product bottleneck が
見えにくくなる。H0 後は bounded repair と portfolio expansion を同時に始めず、返答が
示した一方だけを次スライスにする。

## 実行した確認と残る不確実性

実行した主な確認は `git fetch --prune origin`、`git pull --ff-only`、branch parity、
`npm ci`、recovery probe、targeted/full pytest、changed-scope/full-repo Ruff audit、CLI
help、Node/Electron smoke、docs dashboard regeneration である。全体 Ruff の 14 findings
と docs health の 27 findings は今回の OUT-08 product decision 外で、自動 fix すると
pending human-review slice を広げるため変更していない。

残る不確実性は、Thank 上の private package が export 時にも exact 検証を通るか、
Planner007 への物理コピーと atomic import が成功するか、native-control seek と二本の
編集品質を人間がどう評価するか、rights / production / public owner が将来どの gate を
承認するかである。今回の作業は docs だけを product progress とみなさず、次の consumer
を exact package import と candidate decision に固定している。

---

# OUT-07 parked closure receipt — 2026-07-14

This non-authoritative receipt records the consumed human review. OUT-07 is
closed as `PARK_PROVISIONAL_USABLE`: the current cover is natural, balanced, and
provisionally usable for this episode, but it is not selected, canonical,
default, reusable as a standard, or accepted as a final thumbnail system.
Only one example exists, so reproducibility is unknown and accidental success
is not ruled out. The reference-collection process remains valid while the
reference-to-output lineage remains weak.

The Thank proxy package below is retained unchanged as historical local
evidence. It is no longer the current human entrypoint, and its review server is
stopped. Additional OUT-07 thumbnail iteration is prohibited. Revisit thumbnail
exploration only after 3–5 real Shorts exist, treating the reference corpus as
concrete examples rather than canonical design rules. Rights, production,
public/publishing, upload, and other external gates remain closed or pending.

---

# Historical Thank OUT-07 semantic direction proxy host receipt — 2026-07-14

This is a non-authoritative host receipt. The portable current state and next
action remain in [RUNTIME_STATE.md](RUNTIME_STATE.md). The current host verified
pre-closure state was `OUT07_THANK_NATIVE_SHORTS_COVER_DIRECTION_PROXY_REVIEW_READY`.

Thank has the known source SHA
`6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a`
and official caption SHA
`3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`.
The separate semantic proxy route validated provider `7J5aS_pcBj4`, source
`22.858s`, nearest decoded frame `22.866667s`, sequence `11.930s`, `cut_003`,
and `sub_010`, then reused the established vertical reframe, Keifont, and
subtitle treatment. It did not add an abstract poster background, headline,
mask, collage, or third-party pixel.

The output is
`episodes/jp_pilot01_hololive_bancho_20260525/review/out07_native_shorts_cover_direction_proxy/`.
The proxy PNG SHA is
`e7aaae24401b5b6c75e13926329af19c8a59008dd3c93229735d7465da2f18da`.
Its source and proxy fingerprints differ from the Planner-known fingerprints,
so the classification is `cover_direction_semantic_proxy`, not exact or
pixel-equivalent. Local scene/cue/timing evidence was directly observed;
continuity to Planner is inferred from provider identity and authoritative
mapping because Planner pixels are unavailable on Thank. Two consecutive builds matched every package byte; core and
package digests are `deb93e2f...652` and `0eeb4958...832`, with manifest
inventory and self-integrity passing.

The historical local entrypoint was `http://127.0.0.1:8071/index.html` on
`DESKTOP-H53P1T4`; it is not portable. The page presents list preview, one
1080x1920 proxy, UI overlap, 4:5 crop, mapped source frame, folded evidence, and
one question. It contains no exact baseline video or former candidate set.

Planner007's accepted baseline SHA `2c1c59bc...2d18` remains an accepted
historical fact but is absent on Thank. The strict exact route is unchanged and
still requires its exact SHA/size/duration and byte-copy acceptance gate. The
proxy is only a cover-direction decision surface. Rights, production,
public/publishing, upload, metadata mutation, visibility, made-for-kids, and
all external actions remain pending, false, closed, or unattempted.

The consumed human question was:

> このThank source revisionによる同一時刻・同一字幕のShorts一覧cover方向を採用してよいか。違和感があれば自由記述してください。

---

# Historical Planner007 OUT-07 host receipt — 2026-07-13

The section below records what Planner007 verified before the cross-device
pause. It is lineage evidence, not the current Thank entrypoint.

## What is true on this host

Planner007 explicitly accepted the current 38.633333-second vertical baseline
on 2026-07-13 JST for content/narrative, timing/tempo, cut continuity, A/V
continuity, subtitle timing/readability, and visual integrity. The accepted
baseline SHA-256 is
`2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`;
the qualified source is YouTube `7J5aS_pcBj4`, SHA-256
`e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`.
The official JSON3 caption authority is SHA-256
`3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919`, with
payload digest `e9a18053baf3b6d042f35a91bb18ee7c5b28c878ef9e9d66ce649563ce11c23b`;
the current tracked tip retains hashes and IDs, not caption plaintext.
This acceptance is explicit for the current bytes and does not inherit the
historical OUT-06 acceptance.

The last verified local package is
`episodes/jp_pilot01_hololive_bancho_20260525/review/out07_shorts_poster_frame_direction_proof/`.
Its builder verifies and copies the accepted MP4 byte-for-byte; it does not
render, remux, transcode, edit, retime, or alter subtitles/audio. The sole
recommended cover is the accepted vertical video's 11.930-second frame, mapped
to source time 22.858 seconds and retaining only the existing burn-in
`sub_010`. Its PNG SHA-256 is
`6d8cf92ae49658a9eacb98e7a6e584aa69d2a4ecbb56b553c93eec69e6a3a174`.

The review page provided list-scale, generic Shorts-UI overlap, full 9:16,
center-4:5, mapped-source-frame, metadata, accepted-baseline hash, provenance,
gate, and superseded-candidate readbacks. It was last opened through
`http://127.0.0.1:8071/index.html` on Planner007. PID `41872` was verified as
the OUT-07 `src.cli.serve_review` process serving that directory, then stopped;
port 8071 is now released. The URL and package are not portable current
entrypoints. The portable local artifact flag is `false`; `human_entrypoint`,
`review_open_command`, and `machine_readback` are all `null` in the durable
state. The last-host-only URL above is evidence, not a cross-device promise.

## Decision boundary

The previous active A/B/C are
`superseded_by_user_short_context_reframe`, not quality-rejected, and must not
be offered again. Historical `context` / `tension` / `payoff` directions remain
separately `user_rejected`. The only remaining human judgment is whether the
single native-frame cover direction works for the Shorts list surface.

`selected_thumbnail=null`, `selected_by_human=false`, and
`publish_ready=false`. Rights, production, public/publishing,
upload/visibility, metadata mutation, made-for-kids, and every external-system
action remain closed, pending, or unattempted; baseline acceptance does not
open any of those gates.

## Portability limit

The tracked rebuild contract retains subtitle IDs, cut/timing/segment
locators, text hashes, digest, and wrap break indices, but not the former bulk
caption plaintext. Another host must conditionally reacquire the official JSON3
caption authority when absent and must restore the exact accepted baseline
bytes; missing captions stop as `caption_authority_reacquire_required`, and the
active route is forbidden from recreating the accepted baseline by rendering.
Cross-machine resume therefore remains `conditional_reacquire`. Earlier commits
may contain the former plaintext snapshot; no history scrub is claimed.

## Durable handoff classification

| Class | Handoff meaning |
|---|---|
| tracked | builders, CLI, tests, hash-only caption/timing contract, accepted baseline SHA/size/duration, cover timestamp/SHA/fingerprints, Runtime/Handoff/dashboard/contracts, source/caption identity and recovery commands |
| ignored_local_retained | source media, exact accepted baseline MP4, official JSON3, native cover, review package, manifests/readbacks/previews, local reference cache on Planner007 |
| conditional_reacquire | source identity `7J5aS_pcBj4`, official caption authority, and dependencies; hash mismatch creates a new revision and never inherits acceptance |
| retained_artifact_reacquire | exact baseline SHA `2c1c59bcd6e311cbd9fab1a2dbc117cf1ced0e4c06217febde158867fcfb2d18`; absence stops as `accepted_baseline_reacquire_required` |
| derive | cover, previews, readbacks, package, and manifests only after exact baseline restoration |
| private_only | media bytes, caption plaintext, third-party pixels/cache, credentials, OAuth information |

H1 is cover acceptance followed by closure/full-suite work. H2 is a real
other-host recovery proof. H3 is rights, production, public/publishing, or
external-system work. None is executed by this closeout.
