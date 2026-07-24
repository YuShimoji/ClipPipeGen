# 監修AI向け現状報告 — Edit-Ready Source Packet と長期開発目標

更新日: 2026-07-24 JST
対象: ClipPipeGen のみ
Mission: `clip-edit-ready-source-packet-v1`

## Git 引き渡し状態

Mission 開始時は保護対象 branch
`codex/out-13-editorial-video-candidate-v1` / HEAD
`396432635710622f6573ae15e3f0537452a6c14f` にいたが、そこで作業を継続せず、
current `origin/main`
`5d6f69a64d510508a1f78ab3111a7780913a019c` から
`codex/edit-ready-source-packet-v1` を新規作成した。開始時 tracked/untracked は clean、
`episodes/` と `node_modules/` だけが ignored。target branch はlocal/remoteとも未作成で、
pre-existing user changeはなかった。

portable implementation、tests、contract、handoff、supervisor report は commit
`ff3ad3ce79c8ac72b0c73be8eecae6c1044694db`
（`feat: build provenance-bound edit-ready source packets`）にまとめ、指定どおり
`origin/codex/edit-ready-source-packet-v1` へpushした。push後に local HEAD / upstream /
remote refが同じ commit、ahead/behind `0 0` であることを確認した。main merge、main push、
PR、force push、history rewrite、tag、releaseは行っていない。この節を含む最終handoff metadata
は closure commit で同期し、remote tipはそのcommitになる。

## 今回到達した状態

`origin/main` の `5d6f69a64d510508a1f78ab3111a7780913a019c` を起点に、
`codex/edit-ready-source-packet-v1` を分離作成し、URL または local media locator から
編集工程が直接消費できる provenance-bound Source Packet を一コマンドで生成する経路を
実装した。

従来は source video/audio、fetch receipt、material ledger、rights、caption、transcript が
個別に存在し、後続工程が「どれを authority としてよいか」「同じ source bytes か」を再探索
する必要があった。今回の `build-edit-ready-source-packet` は、その判断を
`EDIT_READY_SOURCE_PACKET_OPERATIONAL_V1` に集約し、次の named consumer が同じ入力契約を
読める状態にした。

- editorial planning
- Timeline IR generation
- subtitle processing
- render pipeline

ここで operational になったのは入力準備だけである。human/editorial acceptance、
rights approval、production acceptance、public/publishing readiness、upload は一切開いていない。

## 実装と workflow 上の効果

| 変更面 | 実装した内容 | 後続工程で減る摩擦 |
|---|---|---|
| one-command intake | `build-edit-ready-source-packet` が既存 video acquisition と audio normalization を再利用 | consumer が downloader、FFprobe、FFmpeg、ledger 登録を組み直す必要がない |
| authority selection | provider caption、verified sidecar、verified imported transcript、configured real STT を明示 priority で選択 | fixture を誤って編集 authority にする経路と、provider failure の silent fallback を除去 |
| caption validation | timing、ordering、duplicate ID、empty text、source duration、language、coverage を fail closed 検証 | Timeline/字幕工程が壊れた cue を後段で発見する手戻りを前倒し |
| normalized mapping | 各 segment に元 caption event ID/index または transcript segment ID を保持 | 編集判断から原 evidence へ戻れる |
| provenance / integrity | source SHA、receipts、ledger、rights snapshot、caption/transcript snapshot、artifact manifest、packet canonical SHA を結合 | 「同じ入力を見ているか」の確認を packet identity だけで行える |
| resume | input fingerprint と全 artifact hash が一致した場合だけ高コスト stage を再利用 | 再取得・再正規化を省きつつ、異入力や破損 cache の誤利用を拒否 |
| readback | machine-readable JSON と passive HTML report | GUI を増設せず、監修者と後続 agent が同じ状態を確認可能 |

portable な変更は CLI、pipeline contract、tests、schema、automation boundary、runtime/handoff、
artifact registry に限定した。実 media、caption、transcript、packet は ignored `episodes/`
配下に置き、Git へ追跡していない。

## 実入力で成立した packet

artifact ID は `clip-edit-ready-source-packet-v1-001`。same-machine local artifact は
`episodes/edit_ready_source_packet_20260724/source_packet/clip-edit-ready-source-packet-v1-001/`
にある。

| 証跡 | 実測値 | 何を証明するか |
|---|---|---|
| source identity | `youtube:7J5aS_pcBj4` | provider 上の論理 identity |
| source bytes | SHA `e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`; 56,063,684 bytes | packet が参照する exact media |
| media readback | 164.768798秒; 1920x1080 | Timeline/render consumer の基礎 metadata |
| authority | `official_provider_caption`; language `ja` | fixture ではない採用候補 |
| transcript shape | 105 event → 105 segment; 122.99 covered seconds; coverage `0.746439869` | consumer が読める timed segment と有効範囲 |
| rights snapshot | SHA `e6ea94717b3bffceaa7cda9c608d2d2ecb6a0a46233958a9113f058c73464c12`; status pending | exact snapshot は保持するが approval は主張しない |
| input fingerprint | `fcd7c30b6a4b5a94c5559c94b71a22676468bed40719c75b08064e1fb2f4da87` | source locator/input hash、identity、language、rights/caption/STT 設定の binding |
| packet integrity | `4398a85882a5df253b92b371bfa791e4f046badf4ac12a877748c6b8627e0fe9` | canonical packet payload の改変検知 |
| artifact manifest | 11 files | source video/audio、receipts、sidecars、ledger、rights、caption、normalized transcript の hash binding |

正系実行コマンド:

```powershell
python -m src.cli.main build-edit-ready-source-packet `
  --packet-id clip-edit-ready-source-packet-v1-001 `
  --episode-id edit_ready_source_packet_20260724 `
  --source-locator episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4 `
  --source-identity youtube:7J5aS_pcBj4 `
  --language ja `
  --rights-manifest episodes/jp_pilot01_hololive_bancho_20260525/rights_manifest.json `
  --caption-track episodes/jp_pilot01_hololive_bancho_20260525/source_subs/7J5aS_pcBj4.ja.json3 `
  --caption-authority provider_official `
  --caption-provider-locator youtube-caption:7J5aS_pcBj4:ja `
  --root episodes --format json
```

readback は次で開く。

```powershell
Invoke-Item episodes\edit_ready_source_packet_20260724\source_packet\clip-edit-ready-source-packet-v1-001\source_packet_report.html
```

## fail-closed と resume の実測

同一入力で `--resume` を実行すると、同じ fingerprint、packet integrity、source SHAを返し、
`resume=true`、`acquisition_executed=false` となった。video acquisition と audio
normalization は反復していない。

source identity だけを異なる値にした resume は
`resume_input_fingerprint_mismatch` で拒否された。拒否前後の成功 packet file SHA はどちらも
`e6c19dd10e0c54adb613cdb0dcef5be7c3613820b0f8087e2460794506c42fe1` で、既存成功を
上書きしていない。

既存 episode の actual fake transcript を authority 入力にした負系は、source acquisition
より前に `fixture_transcript_authority_forbidden` で
`EDIT_READY_SOURCE_PACKET_BLOCKED_V1` となった。これは product success 証跡には数えず、
silent fallback がないことだけを証明する。

## 検証結果と初回失敗の扱い

| 検証 | 結果 | 判断への影響 |
|---|---|---|
| Source Packet 単体 | 12 passed | caption負系、dispatcher、正系、resume、mismatch、integrity、fixture禁止、secret-safe URL fingerprintを固定 |
| acquisition/transcript 関連 | 53 passed | 既存 INT-02 / transcript route の回帰なし |
| docs/current-focus targeted | 初回 33 passed / 2 failed、修復後 35 passed | 失敗は OUT-12 current focus 固定期待値。SH-10 runtime 正本へ更新 |
| full suite | 606 passed / 1 failed、57.31秒 | 唯一の失敗は同じ stale OUT-12 current-focus expectation。実装・artifact validity の失敗ではない |
| cause-based targeted repair | 37 passed | stale test を SH-10 と historical OUT-12 coexistence の期待へ修復。Mission 指示に従い full suite は再実行していない |
| CLI smoke | `build-edit-ready-source-packet --help` 成功 | dispatcher から一コマンド入口を解決可能 |
| diff hygiene | `git diff --check` clean | whitespace error なし |

full suite の一件は `tests/test_active_rebuild_contract.py` が、Runtime の current focus を
OUT-12 URL / artifact に固定していたことが原因。current をSH-10へ変えながら、OUT-12 exact
identity と OUT-07 parked rebuild contract の historical assertions は残した。したがって
今回の outcome を崩す evidence failure ではなく、current pointer の意図的更新に追随する
test repair と判断した。

## OUT-13 の保護状態

今回の作業は OUT-13 の review/production lane を前進させていない。以下は変更前後で保持した。

| 保護対象 | 状態 |
|---|---|
| branch | `codex/out-13-editorial-video-candidate-v1` |
| artifact | `clip-out13-editorial-video-candidate-v1-001` |
| video SHA | `84ed7aa6fc7aa1d478d7fa8f8783e349a5ffa56a7a59dc49c30daafa0791d7e2` |
| local path | `episodes/out13_editorial_video_candidate_20260722/` |
| human editorial review | pending のまま |

Source Packet operational を OUT-13 human acceptance、production acceptance、rights approval、
public decision、upload の代替には使わない。

## 残る不確実性

- actual positive は local-media path で成立した。URL route は既存 INT-02h adapter を呼ぶが、
  このMissionでは新規network acquisitionを追加実行していない。
- provider caption は operational transcript authority だが、人間による発話内容、固有名詞、
  歌唱/歌詞、話者、編集適合性の承認ではない。
- packet consumer は readiness を読めるが、editorial plan / Timeline IR を packet から作る
 専用入口はまだない。ここが現在の最大 bottleneck。
- same-machine artifact は portable ではない。別hostでは同じ source/caption を再取得するか、
  明示承認されたprivate artifact transportが必要。
- rightsはpending。技術的に編集入力がreadyでもproduction/public useは不可。

## 可能な限り先まで見通した目標

以下は依存順の提案であり、自動承認ではない。特に rights、production、credentials、private
transport、public release は各 owner の明示 gate が必要。

| 段階 | 解く bottleneck | 到達条件 | 現在 |
|---|---|---|---|
| G0: Source Packet contract | input断片化とauthority再探索 | real packet、fail-closed、resume、integrity | 完了 |
| G1: packet consumer adapter | planning側がsource/caption取得を再実装する摩擦 | packet validation → editorial brief / Timeline IR seed。source SHAとsegment mappingを保持 | 最優先候補 |
| G2: editorial evidence planner | 長尺segmentから編集候補を選ぶ根拠不足 | cut候補、context window、採用/除外理由、source coverageをmachine-readable化 | G1後 |
| G3: Timeline IR compiler | planning と renderer の中間契約不足 | chronological cut/subtitle/audio mapping、gap/overlap/範囲検証、deterministic fingerprint | proposed |
| G4: bounded preview loop | plan の視聴確認まで手作業が多い | diagnostic render、contact sheet、seekable review、decision patch、exact artifact binding | proposed |
| G5: multi-source repeatability | 一つのsource/providerへの偶然依存 | local/URL、caption/real STT、language差を含む複数packetで同一contractをpass | proposed |
| G6: failure taxonomy / observability | acquisition・caption・planning・render失敗の復旧判断が曖昧 | stage別typed receipt、retry可否、cache invalidation、operator escalationを統一 | proposed |
| G7a: subtitle design acceptance | operational textとproduction presentationの分離 | font/license、line-break、safe area、話者表現をexact visual receiptへbind | closed gate |
| G7b: production render acceptance | internal renderからdelivery品質への昇格 | codec/color/audio/device/full-decode QAとhuman production receipt | closed gate |
| G7c: rights clearance | technical readinessと利用許諾の分離 | source/range別allow/deny/restriction、reviewer、snapshot時刻をrights receipt化 | pending gate |
| G8: production candidate convergence | 独立gateの状態が散らばる | G7a–cを混同せずepisode manifestでaccepted/rejected/deferredを統合 | proposed |
| G9: thumbnail / metadata package | video完成後のoperator手戻り |複数cover、exact thumbnail choice、title/description/tags/category draft | proposed |
| G10: private artifact transport | same-machine artifactを別hostで再現できない | encryption/ACL/retention、manifest hash、restore SHA、audit、Git media 0件 | unapproved |
| G11: private/unlisted delivery | 外部deliveryのidempotency/rollback未証明 | 明示OAuth承認、dry-run、private/unlisted upload receipt、visibility/thumbnail rollback | unapproved |
| G12: explicit public release | 公開判断の責任と証跡不足 | rights/production/thumbnail/metadata全ownerの最終decision packetと公開後receipt | future gate |
| G13: multi-episode operations | 単発成功が継続運用になっていない | queue/retry/retention/metrics、失敗episode隔離、provider差、regression corpus | long-range |

critical path は
`G1 → G2 → G3 → G4 → G5/G6 → G7a+G7b+G7c → G8 → G9 → G11 → G12 → G13`。
G10 は cross-host review が必要になった時点で並行できる。直近では、G1 が Source Packet の
価値を実際の編集workflowへ接続する最小の一手であり、rights/production gateを開けずに進められる。

## 次に選べる取っ掛かり

| 入口 | 減らす摩擦 | 選ぶと次に可能になること |
|---|---|---|
| **Advance — G1 consumer** | packetがreadyでもplanning工程が直接読めない | real packetから再取得なしでeditorial brief / Timeline IR seedへ進める |
| **Audit — G6 failure taxonomy** | typed blocked codeはあるがstage横断の復旧規則が未統一 | URL/acquisition/STTを含む次runでretry、stop、human escalationを一貫させる |
| **Verify — G5 second packet** | local JA provider-caption一本への偶然依存 | URL routeまたはreal STT routeのcontract互換性とcache挙動を比較できる |
| **Explore — G10 private transport** | ignored artifactを監修hostへ渡せない | Gitを汚さずexact bytesをsecond hostで検証する設計判断へ進める |

監修上の推奨は **Advance — G1 consumer**。今回作った入力契約をconsumerが直接使うところまで
繋ぐと、取得/authority層の成果がdocsだけで止まらず、編集計画へ戻る。その後にG5で第二packet、
G6でfailure taxonomyを横展開する順が、現在のworkflow driftを最小にする。
