# ClipPipeGen content-production-lanes/v1

この文書は、共有モデル `content-production-lanes/v1` を ClipPipeGen の既存責務、
artifact、review gateへ対応付ける portable な project-local direction / authority surface
である。分類は責務と判断境界を明確にするために使い、artifact固有のhuman verdict、
rights判断、production/publication approvalを上書きしない。

## 非交渉ルール

- AからEは独立vectorであり、単一の進捗率へ集約しない。
- Bのsource、fact、profile、caption、receipt、provenanceはCの判断材料になれるが、
  premise、narrative、selected beats、composition intentを決定しない。
- flavor、mood、雰囲気、参考例を述べる proseは、明示的なCまたはDのdecisionに
  変換されない限りrequirementでもauthorityでもない。
- `N/A`は、対象artifactにそのvectorが存在しない具体的理由を同じrecordに持つ場合だけ使う。
- technical、hash、decode、subtitle、HTTPのpassはD/Eのintegrity evidenceであり、
  Cのeditorial adoptionやEのhuman acceptanceを成立させない。
- exact bytesが不在なら、同じidentityで再生成、alias、substitutionを行わない。

## ClipPipeGen責務との対応

| vector | ClipPipeGenで所有する意味 | 主なrepo surface | 自動化できる範囲 | 自動で決めないこと |
|---|---|---|---|---|
| A — replaceable assets / generation inputs / metadata | 差し替え可能なfont、layout token、generated/derived visual input、thumbnail slot、metadata draft。exact artifactへbindされた後の置換はsuccessor identityを必要とする | material sidecar、thumbnail template/slot、font receipt、render input metadata | schema検証、hash/size記録、非上書き生成、候補の機械的差し替え準備 | source fact、premise、beat選択、human acceptance |
| B — evidence / source / facts / profiles / provenance | source media、provider identity、caption/transcript、receipt、ledger、rights snapshot、source-time evidence。Cを支えるが支配しない | `material_ledger.json`、fetch receipt、caption/transcript、rights manifest、source binding | exact identity照合、provenance closure、source range readback、unknown/pendingの保持 | authored claim、topic、narrative、winner、rights verdict |
| C — authored content / narrative / composition intent / structure / selected beats | premise、topic、thesis、opening、endpoint、selected/omitted ranges、beat order、foreground focus、coherence intent | editorial plan、Timeline IR、cut decision、human-bound decision receipt | 明示planの構造検証、range一貫性、非上書きsuccessor準備 | source/canon/topic、major voice、major visual method、editorial winner、creative acceptance |
| D — presentation / realization | aspect ratio、reframe、subtitle layout/line break、font realization、audio mix、transition、encode、review page | `src/integrations/render/`、subtitle presentation、media validation、localhost review | bounded render、最大行数/overflow検査、foreground audio owner検査、decode、HTTP/Range | Cの意味選択、production design acceptance、知覚上の最終評価 |
| E — integration / final experience / rights / release / acceptance | closed package、manifest、transport/re-entry、human review、rights、production、publishing、upload/public gate | package manifest、validation readback、decision receipt、rights/publishing records | closed inventory、self-integrity、exact receipt binding、未承認gateのfail-closed保持 | human verdict、rights clearance、release、visibility、publication |

既存のCompliance / Material Sourcing / Editing / Thumbnail / PublishingはA-Eと一対一ではない。
たとえばMaterial Sourcingはreplaceable inputならA、source/provenanceならB、Thumbnailは
素材差し替えならA、realizationならD、公開採用ならEに分類する。この分類は既存FEATURE IDや
lane ownershipを改名しない。

## Exact generated-video challenge requirement records

対象は `clip-development-generated-video-challenge-v1-001`。これは
`DEVELOPMENT_GENERATED_VIDEO_CHALLENGE_REVIEW_READY` のlocal internal review artifactで、
production candidateでもaccepted artifactでもない。次のJSON objectをこのartifactに対する
formal requirement recordの正本とし、直後の表はそのreadable projectionとする。

`order`はstableかつuniqueなintegerである。first-failedは、非空の`required`が適用され、
`status=UNSATISFIED`で、`depends_on`の全recordが`SATISFIED`であるeligible recordのうち、
最小の`order`から導出する。file順、JSON array順、表の行順からは導出しない。
`order`の変更は単なる並べ替えではなくauthority changeであり、新しい明示decisionを必要とする。
`BLOCKED_BY_DEPENDENCY`はfirst-failed候補にならず、依存解消後に別の明示判定を受ける。

```json
{
  "schema_version": "content-production-lanes/v1",
  "artifact_id": "clip-development-generated-video-challenge-v1-001",
  "requirement_records": [
    {
      "requirement_id": "CPG-CHALLENGE-A-EXACT-INPUT-BINDING",
      "lane": "A_REPLACEABLE_ASSETS_AND_METADATA",
      "order": 100,
      "unit": "artifact_input_binding",
      "required": "Every replaceable or generated input used by this exact challenge must be bound by hash and size; changing one requires a successor identity.",
      "observed": "Resolved font, derived poster, subtitle realization inputs, and challenge metadata are closed by the exact current-host manifest. Replacing a bound input requires a successor identity.",
      "owner": "agent_owned",
      "depends_on": [],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/generation_receipt.json"
      ],
      "authority_effect": "Establishes the exact replaceable-input binding for this challenge identity; it does not select authored content or accept a successor.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE",
      "lane": "B_EVIDENCE_AND_REFERENCE",
      "order": 200,
      "unit": "source_provenance_binding",
      "required": "The exact source media, provider identity, media revision, source hashes, and provenance receipt must be bound without granting B authority over C.",
      "observed": "youtube:7J5aS_pcBj4, media revision planner007-e2206cef-20260525, source video SHA-256 e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889, and source audio SHA-256 7cd566dc62683651b05b10b1b4397c44699807249f90af784b88ba0f572cae5d are bound to the exact plan and receipt.",
      "owner": "agent_owned",
      "depends_on": [],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/challenge_plan.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/generation_receipt.json"
      ],
      "authority_effect": "Allows source facts and provenance to inform C while prohibiting B from choosing the premise, beats, winner, or human verdict.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION",
      "lane": "C_AUTHORED_CONTENT_AND_STRUCTURE",
      "order": 300,
      "unit": "authored_intent_definition",
      "required": "The challenge must define an authored premise, opening, endpoint, selected ranges, subtitle-cue intent, and coherence target before review.",
      "observed": "The exact plan defines source ranges 2.453-9.293, 12.329-17.167, and 22.606-49.566, a prompt opening premise, a complete-payoff endpoint, 29 subtitle cues, and one coherent-idea intent. Definition exists; human acceptance remains false.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-A-EXACT-INPUT-BINDING",
        "CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/challenge_plan.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html"
      ],
      "authority_effect": "Defines what the challenge asks a human to judge; definition alone does not accept the premise, opening, endpoint, or composition.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT",
      "lane": "C_AUTHORED_CONTENT_AND_STRUCTURE",
      "order": 400,
      "unit": "premise_opening_endpoint_coherence_verdict",
      "required": "A human must return an exact-identity verdict on premise, opening, endpoint, selected beats, and coherence.",
      "observed": "No human ACCEPT, REPAIR, or REJECT verdict is bound to the exact challenge for authored premise, opening, endpoint, selected beats, and coherence.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html"
      ],
      "authority_effect": "This is the first eligible failed requirement for VALID_PRODUCTION_PREMISE_RECOVERY; machine evidence cannot satisfy it.",
      "status": "UNSATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-D-TECHNICAL-REALIZATION",
      "lane": "D_PRESENTATION_AND_REALIZATION",
      "order": 500,
      "unit": "encoded_presentation_realization",
      "required": "The exact challenge must have a mechanically valid encoded realization with closed subtitle, audio-owner, frame, and decode checks.",
      "observed": "The current-host MP4 is H.264/AAC 1080x1920, 38.633333 seconds, 21602438 bytes, SHA-256 eff74435a27a61d49815709895592540fc14e5b725f675e7c4cf606133ba9e63. Mechanical subtitle checks report two lines maximum and zero one-character final lines; ffprobe and full decode pass.",
      "owner": "agent_owned",
      "depends_on": [
        "CPG-CHALLENGE-A-EXACT-INPUT-BINDING",
        "CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/assets/challenge.mp4",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/validation_readback.json"
      ],
      "authority_effect": "Establishes technical realization only; it does not establish perceptual readability, audio clarity, visual rhythm, or editorial adoption.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT",
      "lane": "D_PRESENTATION_AND_REALIZATION",
      "order": 600,
      "unit": "subtitle_audio_visual_rhythm_verdict",
      "required": "A human must judge subtitle readability and duration, foreground-audio clarity, actual visual crop or overflow, and visual rhythm on the exact media.",
      "observed": "No human verdict is bound to the exact challenge for subtitle readability and duration, foreground-audio clarity, crop or overflow in actual viewing, and visual rhythm.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-D-TECHNICAL-REALIZATION"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/assets/frame_qa_contact_sheet.jpg"
      ],
      "authority_effect": "Keeps static, decode, and subtitle metrics from being promoted to perceptual acceptance.",
      "status": "UNSATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 700,
      "unit": "current_host_package_decode_review_route",
      "required": "The exact current-host package, manifest inventory, self-integrity, full decode, and muted local review route must be present and revalidated.",
      "observed": "On the current host, the exact package contains 11 manifest payloads plus manifest.json, manifest self-integrity SHA-256 e62429bfc704f1118478a2f43aee738c29e02054563239bb026a71cdd624eb69, a full-decodable MP4, and a muted no-autoplay local review route whose HTML and byte-range requests pass.",
      "owner": "agent_owned",
      "depends_on": [
        "CPG-CHALLENGE-D-TECHNICAL-REALIZATION"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/validation_readback.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html"
      ],
      "authority_effect": "Establishes exact same-host review readiness only; it does not prove archive, transport, other-host availability, human acceptance, or public readiness.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-ARCHIVE-TRANSPORT-OTHER-HOST",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 750,
      "unit": "archive_transport_other_host_availability",
      "required": "Archive, transport, or another-host availability must be supported by an exact package receipt and destination readback rather than inferred from current-host bytes.",
      "observed": "No exact archive, transport receipt, or other-host package readback is established. The current-host ignored package must not be treated as cross-device availability.",
      "owner": "external_evidence_owned",
      "depends_on": [
        "CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "docs/WORKTREE_CLEANUP_POLICY.md"
      ],
      "authority_effect": "Prevents local ignored bytes from becoming an unsupported archive, Drive, transport, or other-host availability claim.",
      "status": "UNSATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-RIGHTS-CLEARANCE",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 800,
      "unit": "rights_clearance",
      "required": "Rights clearance must be established by external evidence before production, public, monetized, upload, or publishing use.",
      "observed": "Rights remain pending; no clearance evidence authorizes production, public, monetized, upload, or publishing use.",
      "owner": "external_evidence_owned",
      "depends_on": [
        "CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json"
      ],
      "authority_effect": "Keeps source/provenance closure separate from rights clearance and release authority.",
      "status": "UNSATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-ADOPTION",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 900,
      "unit": "artifact_adoption",
      "required": "Artifact adoption requires satisfied C editorial and D perceptual human verdicts bound to this exact challenge identity.",
      "observed": "Adoption is not eligible for decision until the C editorial verdict and D perceptual verdict are both satisfied.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT",
        "CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html"
      ],
      "authority_effect": "Blocks adoption from being inferred from exact bytes, technical readiness, or an unconsumed review packet.",
      "status": "BLOCKED_BY_DEPENDENCY"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-PRODUCTION-PUBLIC-USE",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 1000,
      "unit": "production_publication_public_use",
      "required": "Production, publication, upload, monetized use, and public use require both exact artifact adoption and rights clearance.",
      "observed": "Production, publication, upload, monetized use, and public use remain closed until both adoption and rights clearance are satisfied by their owners.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-E-ADOPTION",
        "CPG-CHALLENGE-E-RIGHTS-CLEARANCE"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json"
      ],
      "authority_effect": "Keeps internal review readiness from becoming production, release, upload, or public-use approval.",
      "status": "BLOCKED_BY_DEPENDENCY"
    }
  ]
}
```

| requirement_id | lane | order | status | owner | depends_on |
|---|---:|---:|---|---|---|
| `CPG-CHALLENGE-A-EXACT-INPUT-BINDING` | `A_REPLACEABLE_ASSETS_AND_METADATA` | 100 | `SATISFIED` | `agent_owned` | none |
| `CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE` | `B_EVIDENCE_AND_REFERENCE` | 200 | `SATISFIED` | `agent_owned` | none |
| `CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION` | `C_AUTHORED_CONTENT_AND_STRUCTURE` | 300 | `SATISFIED` | `human_owned` | `CPG-CHALLENGE-A-EXACT-INPUT-BINDING`; `CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE` |
| `CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT` | `C_AUTHORED_CONTENT_AND_STRUCTURE` | 400 | `UNSATISFIED` | `human_owned` | `CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION` |
| `CPG-CHALLENGE-D-TECHNICAL-REALIZATION` | `D_PRESENTATION_AND_REALIZATION` | 500 | `SATISFIED` | `agent_owned` | `CPG-CHALLENGE-A-EXACT-INPUT-BINDING`; `CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION` |
| `CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT` | `D_PRESENTATION_AND_REALIZATION` | 600 | `UNSATISFIED` | `human_owned` | `CPG-CHALLENGE-D-TECHNICAL-REALIZATION` |
| `CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 700 | `SATISFIED` | `agent_owned` | `CPG-CHALLENGE-D-TECHNICAL-REALIZATION` |
| `CPG-CHALLENGE-E-ARCHIVE-TRANSPORT-OTHER-HOST` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 750 | `UNSATISFIED` | `external_evidence_owned` | `CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE` |
| `CPG-CHALLENGE-E-RIGHTS-CLEARANCE` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 800 | `UNSATISFIED` | `external_evidence_owned` | `CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE` |
| `CPG-CHALLENGE-E-ADOPTION` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 900 | `BLOCKED_BY_DEPENDENCY` | `human_owned` | `CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT`; `CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT` |
| `CPG-CHALLENGE-E-PRODUCTION-PUBLIC-USE` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 1000 | `BLOCKED_BY_DEPENDENCY` | `human_owned` | `CPG-CHALLENGE-E-ADOPTION`; `CPG-CHALLENGE-E-RIGHTS-CLEARANCE` |

全recordでAからEの責務が存在するため、current stateに`N/A`はない。将来`N/A`を使う場合は、
通常fieldを省略せず、同じrecordに非空の`na_reason`と`na_dependency_effect`を追加する。
`na_dependency_effect`は、そのrecordを適用外にした時にdownstream dependencyとfirst-failed
導出がどう変わるかを明記しなければならない。

このschemaから導出されるfirst-failedは、order 400の
`CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT`である。Cのauthored-intent definitionは
SATISFIEDだが、opening、endpoint、coherence、premiseのhuman verdictはUNSATISFIEDである。
D/Eのmachine greenはこのrequirementを飛び越えない。一方、current hostのexact package、
decode、review routeはSATISFIEDなので、Coordinatorがcurrent human actionとして選べる
acceptance-ready candidateではある。current actionへの昇格自体はこの文書では行わない。

## Identity separation

このchallengeは次のartifactを置換、復元、採用、棄却しない。

- missing four-way proof `clip-wiki-integrated-subtitle-cut-proof-v1-001`
- S2 `clip-s2-subaru-evidence-linked-comparison-v1-002`
- OUT-13 candidate `clip-out13-editorial-video-candidate-v1-001`
- OUT-13 candidate `clip-out13-editorial-video-candidate-v1-003`
- OUT-13 candidate `clip-out13-editorial-video-candidate-v1-005`

S2はcurrent authorityどおりhuman-review-pending / exact-package-missingであり、rejectedへ
変更しない。physically present four-MP4 semantic comparisonはNON_ADOPTED queueとして保持し、
このchallengeのreview readinessから再poll、winner選択、acceptance継承を行わない。

## Portable review and re-entry boundary

repo-relative review entryは
`episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html`。
localhost routeは次で提供できる。

```powershell
python -m src.cli.serve_review --root "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001" --port 8077
```

別hostではtracked expectationだけでmedia availabilityを推論しない。exact package directory、
manifest self-integrity、全11 payloadのbyte size/SHAが揃った時だけ同identityとして再入する。
archive、Drive、publication、access変更は別authorityを必要とする。
