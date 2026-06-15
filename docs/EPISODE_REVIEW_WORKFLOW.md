# Episode Review Workflow

Active Artifact: `clip-human-preview-session-001`

Legacy alias: `clip-episode-review-surface-001`

この文書は、ClipPipeGen を「pipeline 実験集」ではなく、episode 単位で source media / transcript / cut / subtitle / diagnostic video / NLE handoff / rights readback を接続し、動画制作者が生成結果を確認できる Review Surface を持つ制作補助システムとして固定する。

ここでの補正は production render や publishing の承認ではない。ClipPipeGen は production/public acceptance を勝手に行わないが、生成済みの diagnostic video、subtitle overlay proof、代表 frame/contact sheet、artifact links、status readback、human decision question を creator に渡す責務を持つ。

## 責務の地図

| 領域 | ClipPipeGen が持つ責務 | 受け入れない判断 |
|---|---|---|
| source media readback | `material_ledger.json` と source video/audio material id/path/receipt を episode に接続し、review surface に出す | source media の権利承認、公開利用許可 |
| transcript / subtitle source | `transcript.json`、公式 subtitle track import、`edit_pack.subtitles[]` の由来を readback する | STT 品質 acceptance、production subtitle design acceptance |
| cut / context review | selected cuts、context `passed` / `needs_review`、retained risk、operator decision placeholder を表示する | final production edit、creative acceptance の自動決定 |
| diagnostic video review | `rendered_video.mp4` や `subtitle_overlay_visual_proof_cut_*.mp4` がある時は playable video として最初に見せる | production render acceptance、upload readiness |
| representative visual proof | subtitle overlay proof、sample frames、contact sheet、renderer_gap、wrapping/timing readback を束ねる | production typography / final renderer 同一性の保証 |
| NLE handoff | NLE CSV、render manifest、non-repo artifact handoff、operator patch templates を見える場所に集約する | FCPXML / Resolve XML を primary target にすること |
| rights / publishing boundary | rights status と false/pending flags を常時表示する | rights approval、OAuth、visibility change、public publishing |

`diagnostic render is not production render` は正しい。誤りなのは、そこから `therefore video confirmation is out of scope` と読むこと。ClipPipeGen は production/public acceptance を拒否しながら、diagnostic / representative の生成動画確認導線を持つ。

## 制作者の流れ

1. episode intake では、source media、rights readback、transcript source、cut/subtitle artifacts が揃っているかを Episode Dashboard で見る。
2. Review Surface は `review_manifest.json` を読み、最初に playable MP4 または contact sheet を出す。HTML report の探索は第一操作にしない。
3. Cut Review では、creator は keep / adjust / reject / blocked の判断だけを返す。Agent は採否や creative intent を自動補完しない。
4. Subtitle Design Review では、creator は diagnostic / representative の範囲で subtitle overlay evidence を進めるか、調整するかを答える。
5. Export / Handoff では、NLE CSV や render identity を外部編集の材料として確認する。
6. Acceptance Dashboard では、production render、production subtitle design、creative、rights、publishing、public use が false/pending のままかを確認し、次の limitation-lift slice を選ぶ。

## 画面マップ

| Screen | Creator が最初に見るもの | 決めること | 裏付け artifact | この画面では受け入れないもの |
|---|---|---|---|---|
| Episode Dashboard | reviewability、boundary badges、target cuts、missing artifact、primary review order | この episode が diagnostic review 可能か | `review_manifest.json`、`status-episode` readback | production readiness、rights approval |
| Source / Rights Readback | source URL/ID、material ids、rights status、production/public block | source と rights readback を理解したか | `rights_manifest.json`、`material_ledger.json`、non-repo handoff | rights clearance、public use |
| Transcript / Subtitle Source | transcript engine/provider、official subtitle track import、segment/subtitle counts | text evidence を diagnostic review に使えるか | `transcript.json`、`edit_pack.json` | transcript mutation、production subtitle design |
| Cut Review | selected cuts、context status、retained risk、decision placeholder | keep / adjust / reject / blocked | `cut_review_report.html`、`cut_decision_packet.json`、operator proxy handoff | final production edit、creative acceptance |
| Video Review Player | playable MP4 があれば `<video controls>`、無ければ contact sheet / representative PNG | generated video / overlay evidence を確認できるか | `subtitle_overlay_visual_proof_cut_*.mp4`、`rendered_video.mp4`、`visual_proof_contact_sheet.png` | production render acceptance、upload readiness |
| Subtitle Design Review | overlay report、sample frames、wrapping/timing readback、`renderer_gap` | representative subtitle design evidence を進めるか | `subtitle_overlay_visual_proof_report.*`、`representative_visual_proof_report.*` | production subtitle design acceptance |
| Export / Handoff | NLE CSV、render manifest/report、artifact identity、patch templates | 外部編集へ渡す材料が揃っているか | `nle_cut_list.csv`、`render_manifest.json`、`non_repo_artifact_handoff.*` | FCPXML / Resolve XML primary target、publishing |
| Acceptance Dashboard | false/pending flags と limitation-lift 候補 | 次に分離して解く gate | `review_manifest.json.boundary_flags` | implicit production/public acceptance |

## 既存設計の監査

| 既存断片 | 現在の効き方 | 足りない点 | この workflow での扱い |
|---|---|---|---|
| GUI MVP tabs | Episode / Rights / Materials / Editing / Thumbnail / Settings は CLI artifact の状態表示と一部 action に向いている | Video Review Player や acceptance dashboard はまだ tab として存在しない | 既存 GUI は否定しない。Review Surface は先に bundle contract と CLI で固定し、GUI は後続の read-only ingest 候補にする |
| Preview Pack | local media / source audio から read-only artifact preview を作り、GUI Preview Pack tab が既存 manifest を読む | rendered video preview ではなく、diagnostic generated video の確認責務は満たさない | Preview Pack は episode intake / artifact preview として扱い、video review は review bundle 側で扱う |
| Operator Review UX | reviewability first、最小ファイル、正確な質問、commands は appendix という原則がある | 複数 HTML/JSON/MP4 を 1 入口に束ねる contract が無かった | Review bundle が OPERATOR_REVIEW_UX の実体化になる |
| Subtitle overlay proof | `cut_002` / `cut_003` の MP4/PNG/HTML/JSON が diagnostic evidence として存在する | 人間が HTML/report paths を探す負担が残る | bundle の Video Review Player で playable MP4 を先に出す |
| Non-Repo Artifact Handoff | Git に入れない render/source artifact の identity と recovery boundary を記録する | 動画は embed せず、単独では creator review surface ではない | handoff は Export / Handoff screen の証跡として束ねる |

## 現在の user-facing burden

現行の再開導線は `RUNTIME_STATE.md`、`REPRESENTATIVE_SUBTITLE_DESIGN_REVIEW.md`、`OPERATOR_REVIEW_UX.md`、local ignored `episodes/` 配下の複数 HTML に分散していた。特に `subtitle_overlay_visual_proof_report.html`、`representative_visual_proof_report.html`、`cut_review_report.html`、`evidence_summary.html`、`non_repo_artifact_handoff.html` は役割が違うが、creator には「どれを最初に開くか」が残っていた。

`docs/REVIEW_ARTIFACT_BUNDLE_CONTRACT.md` と `build-episode-review-bundle` は、この負担を 1 つの `index.html` / `review_manifest.json` に寄せる。MP4 があるなら video を先に、MP4 が無ければ contact sheet / PNG を先に、JSON/HTML はその後の証跡として並べる。

Active `human_preview_session/` は、人間判断が消費されるまで local に保持してよい review entry point として扱う。利便性を優先し、同じ端末で既に `review_ready=true` の parser readback がある場合は、毎回再生成させず `open_preview.ps1` を最初に案内する。動画確認は production render acceptance ではないが、diagnostic / representative review の責務として in scope であり、散らばった HTML/MP4 を探させるより 1 つの retained local entry point を優先する。

## 現在の JP-Pilot R3 での入口

現在の代表 subtitle review は `cut_002` / `cut_003` の diagnostic overlay proof を使う。creator が最初に開くべき screen は Review Bundle の `index.html` であり、そこで playable `subtitle_overlay_visual_proof_cut_002.mp4` / `subtitle_overlay_visual_proof_cut_003.mp4` があれば最初に確認する。

その後の質問は 1 つに絞る。

```text
Diagnostic / representative review の範囲で、現在の cut_002 / cut_003
badge_left_dialogue presentation を、代表字幕デザイン evidence として
次工程へ進めてよいですか？ production subtitle design / production render /
rights / publishing / public use は承認しません。
```

`cut_008` は dense/stress target だが、現在は `needs_adjustment` と missing current overlay proof により、代表範囲拡張の前提として別 slice に残る。

## 次に進める入口

| 入口 | workflow 上の摩擦 | 選ぶと可能になること |
|---|---|---|
| Advance: review bundle actual run | scattered local HTML / MP4 paths を 1 入口に寄せる | creator が `index.html` から video / frame / report / boundary を確認できる |
| Review: representative subtitle design | subtitle design evidence と production acceptance の混同を避ける | `cut_002` / `cut_003` の diagnostic presentation を進めるか調整するか決められる |
| Audit: dense/stress route | `cut_008` の needs_adjustment と missing proof を分離する | representative scope を広げる条件を決められる |
| Verify: final render-path output | diagnostic overlay proof と final render-path output の違いを残す | production render acceptance 前の比較基準を設計できる |
