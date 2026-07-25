# OUT-13 M6 権利判断準備・監修報告

更新日: 2026-07-25 JST

対象: ClipPipeGen のみ

## 監修時に最初に押さえる結論

OUT-13 は、M4 main 統合完了、M5 integrated baseline verification 通過を維持したまま、
M6 の権利判断準備パケットを作成した。現在の正本状態は
`m6_packet_prepared_rights_decision_pending`、packet verdict は
`READY_FOR_HUMAN_RIGHTS_DECISION`である。

この verdict は、exact accepted mediaに使われた素材、使用range、一次規約、証拠class、
不明点、owner記録欄が、一人のhuman rights ownerが判断できる形へ揃ったことだけを表す。
rights approval、法的判断、production acceptance、thumbnail、publishing、upload、
public release、deploymentは一つも与えていない。

追跡可能な判断入口は
[`docs/rights/out13_m6_rights_decision_readiness_packet.json`](rights/out13_m6_rights_decision_readiness_packet.json)。
現在のfeature branchは`codex/m6-rights-decision-readiness-v1`、開発開始時のmainは
`5bd6e65318df129bebc87291c2ae733f143ed8d8`である。M4/M5で受け入れたfeature revision
`18641fe917b084259869263e8db05d78325aa2db`と、M2のexact media SHAは変更していない。

## 変更していない受領identityと運用境界

| 対象 | exact identity | 今回の扱い |
|---|---|---|
| accepted artifact | `clip-out13-editorial-video-candidate-v1-005` | 同じ判断対象 |
| final MP4 | SHA `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5` | byte変更なし |
| media readback | 82,594,810 bytes / 128.833333s / 1920x1080 / H.264 High + AAC | 同じM2受領対象 |
| M2 receipt | `docs/output_layer/out13_human_acceptance_receipt.json` | historical acceptance scopeを変更しない |
| accepted dimensions | composition、flow、subtitle presentation、内部用途のpicture/audio quality | rightsへ拡張しない |
| accepted feature | `18641fe917b084259869263e8db05d78325aa2db` | M4/M5の祖先関係を維持 |
| M6 baseline | `5bd6e65318df129bebc87291c2ae733f143ed8d8` | 今回feature branchの開始点 |
| private evidence | `episodes/`配下のCandidate 003–005と素材 | ignored、same-machine、read-only |

`episodes/`はGitへ追跡せず、Candidate 003–005のplan、caption、manifest、contact sheet、
audio、MP4、preview sessionを更新または削除しない。M6 packetはこれらのrepo-relative
locatorとhashを参照するが、private mediaをportableだとは表現しない。

## 実素材の棚卸し

M6 packetは、final mediaに入った素材と、検証だけに使った派生物を分けた。technical
provenanceとpermissionも分離している。

| material | finalへの使用 | 固定したidentity / scope | readiness | ownerが閉じる点 |
|---|---|---|---|---|
| source visual stream | 使用 | `youtube:7J5aS_pcBj4`、source SHA `6f78657e...103a`、7 range | `content_observation_required` | third-party character、logo、artwork、表示物、創作的変更の適合 |
| source AAC audio | 使用 | 同じsourceの7 range | `content_observation_required` | music、voice、performance、sound recordingの別条件 |
| normalized PCM WAV | 未使用、lineage証拠だけ | SHA `46e4bc9e...6671`、mono 16 kHz | `not_applicable` | finalへの別素材として扱わない |
| provider caption text | 102 cueをburn-in | exact JSON3 SHA `3c15535f...9919` | `missing_permission` | text再製のpermission basisとattribution |
| transcript derivative | 編集・mapping証拠だけ | SHA `4a7b4fd8...3495` | `not_applicable` | caption/source権利を継承し、独立許諾とはしない |
| Keifont glyph rendering | 使用 | exact resolved font SHA `d5795bdf...ed6f` | `missing_permission` | exact bytesと一次配布・Apache 2.0資料のbinding |
| generated cut/subtitle layers | 使用 | plan SHA `27ef1aa9...dac2`、7 cut、ASS/SRT layout | `not_applicable` | project-authored表明とunderlying素材を分離 |
| source-embedded concerns | 使用可能性あり | 7 range内の人物/声、character、music、logo、sign、artwork等 | `content_observation_required` | 全rangeの視聴観察と第三者条件の追加 |

source sidecarの`third_party_ip=[]`や`prohibited_assets=[]`は、技術metadataが空という
事実にすぎない。第三者要素が存在しない証拠にはしていない。sourceがpublicであること、
anonymous yt-dlpで取得できること、hashが一致することもpermissionではない。

## 使用した7区間と除外した8区間

selected durationは128.795秒、source utilizationは0.781671、final media durationは
128.833333秒。各rangeには映像、source音声、provider caption text、Keifont glyph、
生成subtitle/edit layerが関係する。

| range | source秒 | output秒 | editorial purpose | 現在の限定観察 | rights observation |
|---|---:|---:|---|---|---|
| `cut_001` | 2.453–17.167 | 0.000–14.714 | challenge宣言 | animated character、props、source-native text/graphic | 要 |
| `cut_002` | 22.606–24.041 | 14.714–16.149 | first encounter到着 | representative stillのみ | 要 |
| `cut_003` | 25.109–49.566 | 16.149–40.606 | first winと次の導線 | characters、action props、background、graphic | 要 |
| `cut_004` | 50.868–79.163 | 40.606–68.901 | second challengeとresolution | 複数characters、urban background、native graphic | 要 |
| `cut_005` | 81.298–94.945 | 68.901–82.548 | opponentsとbattle開始 | multi-character、stylized VS presentation | 要 |
| `cut_006` | 95.345–116.467 | 82.548–103.670 | battle escalationとsummoning | battle imagery、spellbook-like表示物/prop | 要 |
| `cut_007` | 116.934–142.059 | 103.670–128.795 | final winとresolution | summoned opponent、characters、resolution graphic | 要 |

全rangeで、music/sound recording、voice/performance、character/talent likeness、
logo/sign/artwork/displayed work、provider caption textをhuman ownerまたは委任された
qualified reviewerが確認する。contact sheetは代表静止画だけなので、音声や全時間の
不存在を証明しない。

除外区間は`0.000–2.453`、`17.167–22.606`、`24.041–25.109`、
`49.566–50.868`、`79.163–81.298`、`94.945–95.345`、
`116.467–116.934`、`142.059–164.768798`。source 0秒から末尾までの補集合として
記録済みで、判断対象を「元動画全部」へ曖昧に広げない。

## 証拠classを分けた理由

| evidence class | 判断に使えること | 単独では言えないこと |
|---|---|---|
| technical provenance | source/hash/range/acquisition/build lineageの同一性 | 利用許可、所有、法的適合 |
| content identity | exact audiovisual work、caption、font、generated layerの特定 | owner、permission |
| content observation | 観察した時間・画面・音声に何が含まれるか | 所有者、契約、未観察区間の不存在 |
| license / terms evidence | publisher/platform/font distributorが公開した条件 | exact artifactへの個別許諾、判断者authority |
| owner representation | identityとauthorityを持つ人によるowner/project-authorship表明 | 未記録の第三者権利、別利用への拡張 |
| permission / owner authority | 誰がどの利用をallow/deny/restrictしたか | 未列挙素材や別利用への自動拡張 |
| attribution obligation | source、creator、license、policyのcredit条件 | underlying permission |
| territory/platform/monetization restriction | public/visibility/地域/期間/収益化/channel条件 | underlying permission |
| unresolved legal/policy question | 誰が何を追加判断すべきか | 法的結論 |
| editorial acceptance | M2でどのmedia/dimensionsを受け入れたか | rights、production、publication |
| platform policy | upload/monetization時の追加制約 | underlying contentの権利付与 |

この分離により、「取得できたから使える」「内部で良い映像と判断したから公開できる」
「規約ページがあるから許諾済み」という誤昇格をtestで拒否できる。

## 一次規約と現在の利用proposition

一次規約snapshotは2026-07-25にread-only取得した。packetにはURL、title、
page/version marker、retrieval date、判断用propositionを記録し、legal conclusionや
exact artifactへのpermissionとして扱っていない。

- COVER / hololiveのDerivative Works Guidelinesは、clip固有条件、third-party IP条件、
  source URL/titleのdescription記載、monetization条件、Content ID禁止、規約変更可能性、
  creative modificationの適用判断をownerへ提示する。
- Keifont一次配布ページはcommercial use、利用上の要請、upstream glyph source、
  Apache License 2.0の記載をownerへ提示する。ただし現在のexact font bytesには、
  配布元とlicense/NOTICEを結ぶsidecarがない。
- YouTube Termsとmonetization policyは、他者contentへの権利がservice利用から生じないこと、
  visual/audioのcommercial rights、reused-content reviewがpermissionと別であることを
  ownerへ提示する。

単一の保守的なintended-use propositionは次の通り。

- exact accepted 128.833333秒MP4をYouTubeへpublic掲載
- worldwide、削除まで無期限を提案
- monetizationを検討対象とし、owner verdictを必須化
- 7区間をchronology-preservingに編集し、provider JSON3由来日本語captionを
  Keifontでburn-in
- description先頭にsource URL
  `https://www.youtube.com/watch?v=7J5aS_pcBj4`とtitle
  `【アニメ】押忍！！ば～んちょ だじぇ！`を置く
- Content ID登録は行わない
- thumbnailへのframe reuse、production render、credentials、upload、visibility設定、
  releaseは今回のpropositionから除外

## Human ownerが入力すべき判断

owner decision surfaceは、UI上の「権利者らしい人」を推測して埋めない。最低限、次を
人間が記録する。

1. decision makerの氏名またはrole、publisher/channelのlegal identity、個人・団体・法人の
   publishing capacity。
2. その人が判断できる根拠とauthority evidence locator。
3. exact intended-use propositionに対する`allow`、`deny`、
   `allow_with_restrictions`のいずれか。
4. 8 material rowsと7 range rowsを全体verdictが明示的にcoverすること、または個別verdict。
5. 全7rangeのaudiovisual rights-content observation結果。
6. caption textのpermission basisと、Keifont exact bytesのlicense binding。
7. attribution、channel registration、monetization、territory、duration、takedown等の制限。
8. decision date、recorded by、authority evidence、decision receipt locator。

現在値はowner identityなし、authority evidenceなし、全体verdict`undecided`。
したがってM6はpacket preparedで止まり、rights decision completeへは進まない。

## 現在のgateと残作業

| gate / 作業 | 目的 | 効果 | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|---|
| M6 packet inventory | exact対象とunknownを閉じる | ownerが同じ対象を判断できる | material/range/terms/identity | 完了 | packetを不変対象としてreview |
| owner identity | 判断主体を固定 | 誰のauthorityか監査可能 | legal identity、capacity、evidence | 未記録 | ownerが入力 |
| full range observation | embedded concernを発見 | third-party条件を局所化 | 全7rangeの映像音声確認 | 未完了 | qualified human review |
| caption permission | burn-in textのbasis | subtitle textの利用判断 | owner/terms/permission evidence | 未記録 | allow/deny/restrict |
| font binding | exact glyph bytesの条件を固定 | production subtitle gateへ接続 | distribution/license/NOTICE locator | 未完了 | 証跡追加またはsuccessor media |
| rights verdict | M6を閉じる | M7/M8を条件付きで開ける | 上記とowner receipt | `undecided` | human decision |
| production/public gates | deliveryと外部stateを管理 | rights判断から公開を分離 | 個別owner receipts | 未開始 | M6後も別承認 |

M6 packetを作ったことによるdriftはない。docsだけを増やして実装から離れる状態ではなく、
次consumerと入力欄をRights owner / Userへ固定し、未承認のproduction/public作業を
明確に止めるための最小tracked handoffである。

## 可能な限り先までの条件付き目標

| 段階 | 目標 | exit evidence | dependency / owner |
|---|---|---|---|
| M0 Remote convergence | remote最新と作業基準を一致 | parity、ancestry | 完了 |
| M1 Exact artifact convergence | source/plan/package/mediaをexact照合 | SHA、digest、readback | 完了 |
| M2 Internal editorial acceptance | exact mediaを内部判断 | human receipt、scope、dimensions | 完了 |
| M3 Main-integration preflight | branch全差分と境界を監査 | READY verdict、authority surface | 完了 |
| M4 Explicit main integration | accepted featureを非破壊統合 | authority、fast-forward、ancestry | 完了 |
| M5 Integrated baseline verification | final main treeの回帰確認 | full/focused suites、privacy、parity | 完了 |
| M6 Rights decision | packetへowner verdictをbind | identity、authority、observation、allow/deny/restrict receipt | 現在。Rights owner / User |
| M7 Production subtitle design | delivery字幕をrights-cleared素材で確定 | exact font/license、frames、safe-area verdict | M6 allow範囲後。Designer / User |
| M8 Production render profile | 配信用A/V仕様を確定 | codec、color、audio、device QC、output SHA | M6/M7後。Production owner |
| M9 Episode acceptance pack | rights/editorial/production receiptを束ねる | lineage-complete manifest、no scope widening | Supervisor |
| M10 Thumbnail candidate set | rights-cleared exact mediaから比較案を作る | multiple candidates、lineage、human selection | M9後。Creative / User |
| M11 Publishing metadata | title/description/attributionを決める | source credit、restrictions、policy review | M9/M10後。Publisher / User |
| M12 External-state dry-run | upload前contractを変化なしで検証 | idempotency、rollback、visibility plan | credentialなし。Agent |
| M13 Private/unlisted delivery | 限定公開でend-to-end確認 | upload receipt、visibility readback、rollback | explicit credential/visibility authority。User |
| M14 Public release decision | public化を個別判断 | rights/production/publishing receipts、final owner approval | User final gate |
| M15 Multi-episode operations | 複数episodeでqueue/retry/retentionを証明 | isolation、SLO、quality/rights trend | Operations owner |
| M16 Policy-constrained autonomy | 反復可能部分だけを安全委譲 | allowlist、budget、stop conditions、audit log | Supervisor / User |

critical pathは
`M6 owner verdict -> M7 subtitle design -> M8 render profile -> M9 episode pack`。
publish pathはM9完了後も自動で開かず、M10〜M14それぞれに人間判断を置く。

## 次に推奨する取っ掛かり

- **Advance**: Rights ownerがM6 packetのidentity、authority、全range observation、
  verdict、restrictionを埋める。これが完了すると、許された範囲だけでM7/M8を起票できる。
- **Audit**: 別のqualified reviewerが7rangeを映像・音声で観察し、第三者music、guest voice、
  logo、displayed workをrange別に追加する。empty metadataを不存在証明にする危険を減らす。
- **Verify**: Keifont exact SHAへprimary distribution、Apache 2.0、必要なNOTICEをbindingする。
  fontを維持できるか、successor mediaが必要かをM7前に確定できる。
- **Explore**: owner verdictを待つ間、M7/M8のexit criteriaだけをread-only設計する。
  production作業や新media生成を始めず、次の判断後の立ち上がりを短くできる。

次の単一actionは
`obtain_human_rights_owner_verdict_for_exact_m6_packet_without_starting_production_or_public_work`。
human verdictとauthority evidenceが記録されるまで、rights approvedともM6 closedとも扱わない。
