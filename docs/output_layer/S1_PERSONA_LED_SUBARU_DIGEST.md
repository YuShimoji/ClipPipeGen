# S1 Persona-Led Subaru Digest v1

## 現在地

`clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001`は、大空スバルの通常配信
二本だけを使った、非公開・人間レビュー待ちのconcept-first digestである。openingで
人物、`2026-07-18 → 2026-07-25`、ドラゴンボール初見の変化、短時間で追える内容を
宣言してから、7 cutを日付順に提示する。

stateは
`PERSONA_LED_ORDINARY_STREAM_S1_CANDIDATE_READY_FOR_HUMAN_REVIEW`。
これはtechnical reviewabilityの成立を示すが、editorial acceptance、rights approval、
public/monetized use、publication、uploadを開かない。

## 方向宣言

- primary persona: `大空スバルのファン who wants a condensed catch-up`
- concept: `大空スバルの2026-07-18〜2026-07-25「おはスバ」ドラゴンボール初見キャッチアップ`
- viewer benefit: 初読で感じた読みやすさと、一週間後に原作とゲームの両方から人物・
  緊張感の見え方が変わった流れを、ながら見でも短時間で追える。
- 二本が必要な理由: 7/18は16巻まで読んだ時点の第一印象、7/25は原作とゲームを
  進めた後の人物理解と危機感の更新であり、連続する週の非重複な観察になる。
- direction SHA:
  `e4823530f3fcacc874d0ec202830731a6dfb7a432906c251391e3700a28df5bd`

方向はcut生成前に
`episodes/s1_persona_led_subaru_digest_20260728/predeclared_direction.json`へ記録し、
planがそのSHAへbindする。「latest」は主張しない。

## Source と処理境界

| archive | source | media | receipt / ledger | processing boundary |
|---|---|---|---|---|
| 2026-07-18 | `youtube:ib3DwHDI71Q` | 259,391,841 bytes / 5374.049524s / SHA `cf6a010a26c1a159b902bb5412f952086c365ce7e73d3775ee5a25aaaa11d353` | receipt `6f0d6e85807f2504d26c6e40387712206f6fef32116d726b57b5158d09f8863f`; ledger `90ddf14c17a2c16c93077f64c68b9eb67afd4b72a9049cbf9b0e4fcd2a63d2fb` | authority `CPG-AUTH-20260728-IB3DWH-PRIVATE-ACQUISITION-01`; anonymous exact-target acquisition 1件完了 |
| 2026-07-25 | `youtube:rltNvZ_FY8Q` | 244,453,290 bytes / 4848.047891s / SHA `5e026c94f40acd0dfc32a5ab610300a7bccbe3cd66441a7d9cc703cc7b83d240` | existing receipt `7c8e32e6599a2eb5963416f290b04790f6bc056038a19cee25372484b2349426`; existing ledger `ba864bde9ef0ffdcc1109a6772dab4f6064fa070457a1cc7bf9f2003f9afdcac` | exact bytesと既存provenanceのread-only reuse。network acquisition 0件 |

7/18 sourceの最初のwhole-source attemptは正規adapterの30分timeoutになった。adapterの
cleanup contract、空のtarget、receipt/ledger不在、関連process不在を読み取り専用で照合し、
完了効果0件を確定してから、同じ認可targetをレビューに十分なformat 18で完了した。
別source、Cookie、login、OAuth、browser profile、credential、membership accessは使っていない。

各sourceはprovider metadata、provider JSON3 caption、media、receipt、ledger、
source-specific processing snapshot、identity bindingのSHAへbindする。snapshotの
`user_granted_processing_scope`は`local_private_review_only`、underlying rightsは
`pending_or_unverified`、public/monetized useは`not_authorized`。このsnapshotは
**rights clearanceでもrights approvalでもない**。

## Ordered cuts と隣接関係

| cut | source range | topic / immediate function | 前からの関係 |
|---|---:|---|---|
| 001 | 7/18 `360.960–381.360` | 文字量の少なさから漫画を絵本のように読めるという発見 | concept-first openingから開始 |
| 002 | 7/18 `445.800–475.120` | 16巻まで、最初の冒険が好きな理由を読みやすさで具体化 | same topic continuation |
| 003 | 7/18 `538.640–557.120` | 絵の比重への発見 | same topic continuation |
| 004 | 7/18 `570.000–587.760` | 文字なしでも出来事と進行方向が分かる | same topic continuation。間の無関係な約13秒を除外 |
| 005 | 7/25 `4084.960–4108.840` | 原作とゲームを進めた一週後の漫画評価 | explicit date/topic change |
| 006 | 7/25 `4182.040–4217.760` | 悟空対ベジータ戦の危機感が原作で強く見えた | explicit topic change |
| 007 | 7/25 `4484.040–4519.360` | 原作の途中経過でピッコロの人物像がつながった | explicit topic change |

全隣接点は`transition_continuity.json`に記録し、visible section labelを持つ。
abstract common frameだけに依存するtransitionは0。source chronologyは
`2026-07-18_then_2026-07-25`、source switchは1回。

## Package とreadback

- final MP4:
  `episodes/s1_persona_led_subaru_digest_20260728/artifacts/clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001/final_video.mp4`
- SHA-256:
  `ca2cf751dfab68e56e4322208f7b6c677a8247fec10cf86813fd3cf80a24e76c`
- size / duration: `54,881,314 bytes / 187.920s`
- media: H.264 High / AAC LC / yuv420p / 1920x1080 / 30fps / stereo 48kHz
- package: 12 payload files＋`run_manifest.json`
- payload tree digest:
  `0c5e96f5a020d6828082917b4c2ab2be291d9ddcb9871735c0f4a908c20a9e21`
- manifest self-integrity:
  `659897fef35965ede7c514767021522a903e41c0e24701ce2f796809dafd020f`
- contact sheet:
  `review/evidence/cut_contact_sheet.jpg`

manifest closed set、独立manifest validator、ffprobe、full non-audible A/V decodeはpass。
review pageはrelative `../final_video.mp4`と`evidence/cut_contact_sheet.jpg`だけを使い、
private absolute pathを含まない。

wide 1440×1000とnarrow 390×844のactual-content browser inspectionはouter horizontal
overflow 0、console/page error 0。narrow tableは336pxの`overflow-x:auto` container内へ
収まり、document外へ漏れない。videoは両viewportで`muted=true`、`paused=true`、
`currentTime=0`、autoplay attributeなし、readyState 4。openingと全7 cut開始点を
muted・pausedのままseekし、1920×1080 frame、人物・日付・section label・字幕を確認した。
pageはHTTP 200、MP4 Rangeは206。検証後にbrowserとport 8079 listenerを停止した。

同一マシンで開く:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\s1_persona_led_subaru_digest_20260728\artifacts\clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001\review\open_preview.ps1
```

localhost fallback:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\s1_persona_led_subaru_digest_20260728\artifacts\clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001\review\serve_preview.ps1
```

## Human gate と旧artifact

human gateは、このexact MP4についてconcept-first promiseが直ちに理解できるか、
7 cutsが食事・作業中でも追えるか、各cutのproximal contextが十分か、二週の変化が
一つのdigestとして成立するかを`accept / bounded repair / reject`で判断すること。
machine passをcreative acceptanceとして扱わない。

旧`clip-s1-two-source-common-context-probe-v1-001`はexact bound HEAD
`bafe25afe0d2cad0cfaa0a2bda432b7ac0ef8471`への
`reject / BLOCK_CURRENT / superseded / not bounded_repair`として歴史証跡へ隔離した。
official-animation素材、抽象的なordered-cut similarity、concept-before-viewing不在、
viewerによるthesis再構成、高いlow-attention負荷というsignatureをactive/default/
accepted exposureから外した。旧packageは削除・上書きしない。

新artifactも現時点ではactive private human-review targetにすぎない。
rights、production、public/monetized use、publication、upload、releaseは閉じたまま。
