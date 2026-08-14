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

対象は `clip-development-generated-video-challenge-v1-001`。exact package manifestのstateは
`DEVELOPMENT_GENERATED_VIDEO_CHALLENGE_REVIEW_READY` のまま変更しないが、current product
authorityでは `TECHNICAL_DIAGNOSTIC_ONLY / SOURCE_CLASS_INADMISSIBLE_FOR_CURRENT_TARGET` である。
production candidateでもaccepted artifactでもなく、従来の`USER_DECISION_REQUIRED` packetは
withdrawnで、creative / perceptual human reviewを要求しない。次のJSON objectをこのartifactに
対するformal requirement recordの正本とし、直後の表はそのreadable projectionとする。

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
      "requirement_id": "CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY",
      "lane": "C_AUTHORED_CONTENT_AND_STRUCTURE",
      "order": 250,
      "unit": "current_target_source_class_admissibility",
      "required": "The current target source must be ordinary-stream and actual-clipping-like, identify a named member and explicit date or topic, support a concept-first chronological or sectioned digest, and remain legible for low-attention viewing. Official animation is excluded unless a later explicit human exception changes this authority.",
      "observed": "youtube:7J5aS_pcBj4 is the official hololive short anime documented in README.md. It was selected for this challenge only as the shortest exact local render route, not as an admissible production-direction source. It therefore fails the current source class with decision_effect=BLOCK_CURRENT.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE"
      ],
      "evidence": [
        "README.md",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/challenge_plan.json"
      ],
      "authority_effect": "Classifies the immutable challenge as technical diagnostic evidence only and blocks editorial, perceptual, adoption, and production-direction review without rejecting or relabeling its exact bytes.",
      "status": "UNSATISFIED"
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
      "authority_effect": "Preserves the authored-intent definition as technical diagnostic evidence; source-class inadmissibility prevents it from becoming a current human review request or production-direction proposal.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT",
      "lane": "C_AUTHORED_CONTENT_AND_STRUCTURE",
      "order": 400,
      "unit": "premise_opening_endpoint_coherence_verdict",
      "required": "Only after current-target source-class admissibility is satisfied, a human must return an exact-identity verdict on premise, opening, endpoint, selected beats, and coherence.",
      "observed": "The source class is inadmissible for the current target, so an editorial verdict is neither eligible nor requested. The prior USER_DECISION_REQUIRED packet is withdrawn.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY",
        "CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html"
      ],
      "authority_effect": "Blocks creative review behind source-class admissibility and prevents the exact technical diagnostic from returning to the human review frontier.",
      "status": "BLOCKED_BY_DEPENDENCY"
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
      "authority_effect": "Establishes immutable technical-diagnostic realization only; it does not revive perceptual review, establish production direction, or grant editorial adoption.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT",
      "lane": "D_PRESENTATION_AND_REALIZATION",
      "order": 600,
      "unit": "subtitle_audio_visual_rhythm_verdict",
      "required": "Only after current-target source-class admissibility is satisfied, a human must judge subtitle readability and duration, foreground-audio clarity, actual visual crop or overflow, and visual rhythm on the exact media.",
      "observed": "The source class is inadmissible for the current target, so perceptual review is neither eligible nor requested; technical subtitle, audio, frame, and decode results remain diagnostic evidence only.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY",
        "CPG-CHALLENGE-D-TECHNICAL-REALIZATION"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html",
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/assets/frame_qa_contact_sheet.jpg"
      ],
      "authority_effect": "Keeps static, decode, and subtitle metrics from being promoted to perceptual acceptance and blocks a human review request for this inadmissible source class.",
      "status": "BLOCKED_BY_DEPENDENCY"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 700,
      "unit": "current_host_package_decode_review_route",
      "required": "The exact current-host package, manifest inventory, self-integrity, full decode, and muted local diagnostic route must be present and revalidated.",
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
      "authority_effect": "Establishes exact same-host technical-diagnostic availability only; it does not revive human review, establish source-class admissibility, grant human acceptance, or imply public readiness.",
      "status": "SATISFIED"
    },
    {
      "requirement_id": "CPG-CHALLENGE-E-ARCHIVE-TRANSPORT-OTHER-HOST",
      "lane": "E_INTEGRATION_EXPERIENCE_AND_RELEASE",
      "order": 750,
      "unit": "archive_transport_other_host_availability",
      "required": "Archive, transport, or another-host availability must be supported by an exact package receipt and destination readback rather than inferred from current-host bytes.",
      "observed": "Owner-only Drive object 1jrcOCETYoMIBTo7KjKmSDmThgoLRs0NU is recorded as shared=false/not_shared. Its raw re-download is 22647612 bytes with SHA-256 044b95d92895f22146f07ebf5c159408e6d29634c2da0c632a42fde886499d16 and closes a source package of 12 files / 22639762 bytes whose MP4 remains SHA-256 eff74435a27a61d49815709895592540fc14e5b725f675e7c4cf606133ba9e63.",
      "owner": "external_evidence_owned",
      "depends_on": [
        "CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE"
      ],
      "evidence": [
        "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/manifest.json",
        "docs/PRIVATE_ARTIFACT_TRANSFER.md",
        "direct owner readback authority dated 2026-08-14"
      ],
      "authority_effect": "Establishes exact owner-only transport/readback evidence for the immutable technical diagnostic only; it does not revive review, satisfy source-class admissibility, or grant rights, adoption, production, upload, or publication authority.",
      "status": "SATISFIED"
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
      "required": "Artifact adoption requires current-target source-class admissibility plus satisfied C editorial and D perceptual human verdicts bound to this exact challenge identity.",
      "observed": "Adoption is blocked by source-class inadmissibility; the downstream C editorial and D perceptual verdicts are therefore also blocked and no review request is active.",
      "owner": "human_owned",
      "depends_on": [
        "CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY",
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
| `CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY` | `C_AUTHORED_CONTENT_AND_STRUCTURE` | 250 | `UNSATISFIED` | `human_owned` | `CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE` |
| `CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION` | `C_AUTHORED_CONTENT_AND_STRUCTURE` | 300 | `SATISFIED` | `human_owned` | `CPG-CHALLENGE-A-EXACT-INPUT-BINDING`; `CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE` |
| `CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT` | `C_AUTHORED_CONTENT_AND_STRUCTURE` | 400 | `BLOCKED_BY_DEPENDENCY` | `human_owned` | `CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY`; `CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION` |
| `CPG-CHALLENGE-D-TECHNICAL-REALIZATION` | `D_PRESENTATION_AND_REALIZATION` | 500 | `SATISFIED` | `agent_owned` | `CPG-CHALLENGE-A-EXACT-INPUT-BINDING`; `CPG-CHALLENGE-C-AUTHORED-INTENT-DEFINITION` |
| `CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT` | `D_PRESENTATION_AND_REALIZATION` | 600 | `BLOCKED_BY_DEPENDENCY` | `human_owned` | `CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY`; `CPG-CHALLENGE-D-TECHNICAL-REALIZATION` |
| `CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 700 | `SATISFIED` | `agent_owned` | `CPG-CHALLENGE-D-TECHNICAL-REALIZATION` |
| `CPG-CHALLENGE-E-ARCHIVE-TRANSPORT-OTHER-HOST` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 750 | `SATISFIED` | `external_evidence_owned` | `CPG-CHALLENGE-E-CURRENT-HOST-REVIEW-PACKAGE` |
| `CPG-CHALLENGE-E-RIGHTS-CLEARANCE` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 800 | `UNSATISFIED` | `external_evidence_owned` | `CPG-CHALLENGE-B-EXACT-SOURCE-PROVENANCE` |
| `CPG-CHALLENGE-E-ADOPTION` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 900 | `BLOCKED_BY_DEPENDENCY` | `human_owned` | `CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY`; `CPG-CHALLENGE-C-HUMAN-EDITORIAL-VERDICT`; `CPG-CHALLENGE-D-HUMAN-PERCEPTUAL-VERDICT` |
| `CPG-CHALLENGE-E-PRODUCTION-PUBLIC-USE` | `E_INTEGRATION_EXPERIENCE_AND_RELEASE` | 1000 | `BLOCKED_BY_DEPENDENCY` | `human_owned` | `CPG-CHALLENGE-E-ADOPTION`; `CPG-CHALLENGE-E-RIGHTS-CLEARANCE` |

全recordでAからEの責務が存在するため、current stateに`N/A`はない。将来`N/A`を使う場合は、
通常fieldを省略せず、同じrecordに非空の`na_reason`と`na_dependency_effect`を追加する。
`na_dependency_effect`は、そのrecordを適用外にした時にdownstream dependencyとfirst-failed
導出がどう変わるかを明記しなければならない。

このschemaから導出されるfirst-failedは、order 250の
`CPG-CHALLENGE-C-SOURCE-CLASS-ADMISSIBILITY`である。Bのexact provenanceとCの
authored-intent definitionはSATISFIEDだが、official short animeはcurrent targetに必要な
ordinary-stream / actual-clipping-like source classを満たさない。Cのeditorial verdictとDの
perceptual verdictはこの依存でBLOCKEDであり、D/Eのtechnical greenやowner-only transportは
このrequirementを飛び越えない。このchallengeはacceptance-ready candidateでもcurrent human
actionでもなく、immutable technical diagnosticとしてparkする。

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

## Technical diagnostic transport and re-entry boundary

repo-relative HTML entryは
`episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001/review/index.html`。
これはpackage integrityを調べるtechnical diagnostic routeとしてのみ保持し、human review requestや
content acceptance surfaceとして提示しない。必要なmachine inspection routeは次で提供できる。

```powershell
python -m src.cli.serve_review --root "episodes/jp_pilot01_hololive_bancho_20260525/review/development_generated_video_challenge_v1_001" --port 8077
```

owner-only transportはDrive object `1jrcOCETYoMIBTo7KjKmSDmThgoLRs0NU`、
`shared=false/not_shared`としてreadback済みである。ZIPは22647612 bytes、raw re-download SHA-256は
`044b95d92895f22146f07ebf5c159408e6d29634c2da0c632a42fde886499d16`。source packageは
12 files / 22639762 bytesで、内部MP4 SHA-256は
`eff74435a27a61d49815709895592540fc14e5b725f675e7c4cf606133ba9e63`のまま閉じている。
再生成、再upload、共有変更は行わない。

別hostではtracked expectationやDrive metadataだけでmedia identityを推論しない。上記raw ZIP
identityを再照合したうえで、exact package directory、manifest self-integrity、全11 payloadの
byte size/SHAが揃った時だけ同じtechnical diagnostic identityとして再入する。このtransport
closureはsource-class admissibility、human review、rights、production、publicationを再開しない。
