# S2 Evidence-Linked Comparison

## Review identity

- artifact_id: `clip-s2-subaru-evidence-linked-comparison-v1-002`
- state: `EVIDENCE_LINKED_MULTI_SOURCE_COMPARISON_ARTIFACT_READY_FOR_HUMAN_REVIEW`
- local package: `episodes/s2_evidence_linked_comparison_20260729/artifacts/clip-s2-subaru-evidence-linked-comparison-v1-002/`
- review entry: `review/index.html`
- open command: `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\s2_evidence_linked_comparison_20260729\artifacts\clip-s2-subaru-evidence-linked-comparison-v1-002\review\open_preview.ps1`
- final MP4 SHA-256: `a959dc50a0b1b36d37644195fab9105403afdbc7e5f60dfc42ca90c70c72d00f`
- duration / size: `63.466667s / 7,829,406 bytes`

このidentityはprivate human review対象であり、editorial acceptance、rights
clearance、production acceptance、public/monetized use、publication、uploadを
含まない。

## Thesisと比較契約

thesisは「7月18日の第一印象と、7月25日の理解更新を並べて見る」。questionは
「最初に感じた読みやすさは、一週後の原作理解へどう更新されたか」。viewer benefitは
「二つの発言を同じ画面で見て、初見から理解更新までを短時間で追える」。

各comparison beatは次を満たす。

- 二つまたは三つのevidence bindingを表現できるIRを使う。current artifactは二つだけ。
- primary quote一件とpaired evidence一件以上を持つ。
- bindingごとにdistinct source identity、exact source range、visible source/date labelを持つ。
- foreground audio ownerはbeatごとに一件だけで、他bindingのaudioはmuteする。
- openingとtransitionにも実source frameを使う。AI画像、TTS、追加音楽、CTAは使わない。
- source captionとcreator-authored propositionを別provenanceとして扱う。

## Exact beats

| beat | foreground audio | primary quote | paired evidence | proposition |
|---|---|---|---|---|
| 1 | 2026-07-18 | `368.479–381.360` | 2026-07-25 `4093.799–4108.840` | 第一印象は、文字が少なく絵で進行を追える読みやすさ |
| 2 | 2026-07-25 | `4093.799–4108.840` | 2026-07-18 `370.599–381.360` | 一週後、読みやすさは原作そのものの面白さへ更新された |
| 3 | 2026-07-25 | `4182.040–4202.560` | 2026-07-18 `576.200–587.760` | 絵で進行が分かる発見から、戦いの危機感まで見える理解へ |

## Source binding

| source | media SHA-256 | reused evidence |
|---|---|---|
| `youtube:ib3DwHDI71Q` / 2026-07-18 | `cf6a010a26c1a159b902bb5412f952086c365ce7e73d3775ee5a25aaaa11d353` | receipt `6f0d6e85807f2504d26c6e40387712206f6fef32116d726b57b5158d09f8863f`; ledger `90ddf14c17a2c16c93077f64c68b9eb67afd4b72a9049cbf9b0e4fcd2a63d2fb`; caption `6036de7ed7ae7823354a5ce725f6c40d2a95842d63868721690425d3bc3e3eda` |
| `youtube:rltNvZ_FY8Q` / 2026-07-25 | `5e026c94f40acd0dfc32a5ab610300a7bccbe3cd66441a7d9cc703cc7b83d240` | receipt `7c8e32e6599a2eb5963416f290b04790f6bc056038a19cee25372484b2349426`; ledger `ba864bde9ef0ffdcc1109a6772dab4f6064fa070457a1cc7bf9f2003f9afdcac`; caption `011d8a823b040a03cafad8f6251409d50feb2ab659ca66527b98b5dc9f452739` |

S2はS1 inputのexact-byte local reuseだけを行った。新規acquisition、network access、
credential、OAuth、membership accessは0。processing snapshotsは
`local_private_review_only`とunderlying rights `pending_or_unverified`を分離し、
rights clearanceではない。

## Packageと検証

- output: H.264/AAC、yuv420p、1920×1080、30fps
- payloads: 12 files plus manifest
- payload tree digest: `ea2e6cb359325210ed2e1f267d5f3a0b9f6ca22d31b229cbe8b569a24b508090`
- manifest self-integrity: `4eda3d7f01a4fc1abc4c1d863a03d5dec2b061d3708149ba00259515d51b5479`
- direction/plan/source/provenance/audio-owner/closed-set validation: passed
- ffprobe and full non-audible A/V decode: passed
- focused S2 tests and S1 regression: passed
- browser: wide 1440×1000 / narrow 390×844、overflowなし、muted / paused /
  time zero / autoplay absent、console error 0
- actual frame inspection: opening、全3 transition、全3 comparison beatで両panelに
  実source frameを確認
- HTTP: page `200`、MP4 Range `206`
- browser/listener: stopped

v001はbrowser QAでfavicon 404を検出したbounded predecessor。v002はreview HTMLへ
data faviconを追加した。MP4 bytesとSHAは同一で、v001をactive identityとして扱わない。

## Portabilityとpredecessor

`episodes/`はignoredかつtracked 0。tracked code/tests/docsは別hostへ移るが、source media、
final MP4、review packageはGitでは移らない。同一マシン以外でreview-readyを推定しない。

S1 artifact `clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001`はhuman review
pendingのまま保存されている。S2はS1 source/packageを変更せず、S1を再受理・rejectせず、
acceptanceを継承しない。

## Campaign Horizon

| stage | purpose | benchmark family | state |
|---|---|---|---|
| ED-13 evidence-linked comparison explainer | quoteとsupportをexact rangeへ戻せる比較 | すばるかエレンか / みこちかスバルか / みこちかGACKTかローランドか | current artifactは二source一例、human verdict pending |
| ED-14 synchronized multi-participant camera director | 同一eventの参加者cameraを時刻同期 | ホロナルド / 7 Days to Die / Minecraft | proposed staged scenario |
| ED-15 event-centered reaction compiler | 一つのeventへ複数reactionを集約 | ホロライブラジコン企画 / カードショップシミュレーター高額カード反応 / ドラゴンボール名場面反応 | proposed staged scenario |
| ED-16 held-out genre variation proof | 別genreで過適合を検出 | comparison / multi-camera / reactionからheld-outを選定 | proposed、ED-13〜15のreview evidenceが必要 |

benchmark名は方向検証用のstaged scenarioであり、source/rights availability、
acquisition authority、production/public useを主張しない。

## Human decision gate

ownerはProduct owner / User / Supervisor。exact MP4 SHAへ
`accept / bounded repair / reject`をbindし、次を全編で判断する。

- 同時二画面が比較を速めるか。
- primary quoteとpaired evidenceの関係が誤解なく読めるか。
- foreground audio ownerの切替が自然か。
- 三つのpropositionが一つの理解更新として成立するか。

machine validationはeditorial acceptanceではない。acceptでもrights、production
subtitle/render/image quality、thumbnail、publishing、upload、public/monetized useは
独立gateのまま。

## Decision recording contract

`record-evidence-linked-comparison-decision`は上の人間判断を代行せず、明示済みJSONを
exact artifactへbindする。入力はartifact id、MP4 SHA、manifest self SHA、timezone付き
reviewed_at、全編視聴確認、summaryと次の4 dimensionを必須とする。

- `concurrent_panels_speed_comparison`
- `quote_evidence_clarity`
- `foreground_audio_transitions`
- `thesis_coherence`

dimension値は`pass / needs_repair / fail`。`accept`は全件passかつrepair instructionなし、
`bounded_repair`は一件以上のneeds_repair、failなし、具体的repair instruction必須、
`reject`は一件以上のfailかつrepair instructionなしでなければ記録しない。

```powershell
uv run python -m src.cli.main record-evidence-linked-comparison-decision `
  --artifact-dir episodes\s2_evidence_linked_comparison_20260729\artifacts\clip-s2-subaru-evidence-linked-comparison-v1-002 `
  --decision <human-decision.json> `
  --output <decision-receipt.json> `
  --dry-run `
  --format json
```

dry-runが通った同じ入力から`--dry-run`だけを外して記録する。receiptはclosed artifact
packageの外にある未使用pathへexclusive writeし、既存pathは常に拒否する。訂正時も既存
receiptを上書きせず新しいpathを使う。記録後もrights、production、
thumbnail、publishing、public/monetized use、uploadはすべて閉じたまま。
