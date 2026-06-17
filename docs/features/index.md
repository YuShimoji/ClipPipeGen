# Feature Dashboard

This generated index is the scan-friendly v1.5 view of [../FEATURE_REGISTRY.md](../FEATURE_REGISTRY.md). Edit the registry or dashboard builder, then regenerate instead of hand-editing this table.

## Current Focus

- feature: `ED-10j`
- artifact: `clip-ed10j-kirinuki-font-audit-001`
- state: `ed10j_kirinuki_font_audit_requires_review`

## Feature Table

| id | title | status | health | progress_pct | active_artifact | next_action |
|---|---|---|---|---:|---|---|
| CR-01 | rights_manifest schema v1 と validator | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| MS-01 | material_ledger schema v1 と CRUD CLI | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| MS-02 | material_sidecar schema v1 と validator | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| MS-03 | 透過PNG 受け入れフロー | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| TH-01 | YMM4 サムネ slot patch（NLMYTGen CLI bridge） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-01 | CLI runner と config（NLMYTGen path 設定含む） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| TH-W01 | Slice 1 walkthrough 補助 | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| HoloEN-01 | Phase 0.5 publish-quality diagnostic pilot | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| JP-STT-01 | Japanese STT via vosk-model-ja | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| JP-Pilot-01 | Japanese public VOD diagnostic pilot | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| JP-Pilot-01R | ED-09 corrected rerun on JP public VOD | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| JP-Pilot-01R2 | review coverage + selected cut narrowing on JP public VOD | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| JP-Pilot-01R3 | official subtitle track import rerun on JP public VOD | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-07c | --language ↔ --model 一貫性 validation | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-01 | edit_pack schema v1 | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-02a | 手動/インポート cut candidate 追加 CLI | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-02 | カット候補抽出（音声・字幕ベース） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-03 | 文脈チェック | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-04 | 字幕案生成 | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-05 | 字幕表示幅計測（EAW、stdlib のみ） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-05b | text_measure bridge migration | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| ED-06 | 外部 NLE 用 minimal export | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-07 | transcript schema v1 + transcribe-audio CLI | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-07b | real STT transcript path | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-08 | real STT subtitle draft linkage | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-09 | transcript review / correction workflow | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10 | official subtitle track import / transcript alignment | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10a | R3 cut review packet / evidence summary | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10b | R3 chapter revision board / patch template | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10c | R3 cut decision packet | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10d | R3 cut_002/cut_003 proxy decision handoff | done | blocked | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10e | R3 cut boundary recommendation apply receipt | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| ED-10f | Representative Subtitle Design Review v1 | done | blocked | 100 | clip-review-acceptance-gate-001 | Keep as reference unless a regression or successor lane appears. |
| ED-10g | Subtitle Typography Decoration Comparison v0 | done | accepted_diagnostic_base | 100 | clip-ed10g-noto-overlay-proof-001 | Keep as historical diagnostic proof; the latest human review sends styling to ED-10i. |
| ED-10h | Subtitle Font Candidate Sweep v0 | approved | defined_not_generated | 15 | clip-subtitle-font-candidate-sweep-001 | Use the font candidate registry to choose a no-download or download-approved sweep route. |
| ED-10i | Kirinuki Gothic Weight Balance Comparison v0 | done | reviewed_not_accepted_as_normal_baseline | 100 | clip-ed10i-meiryo-overlay-proof-001 | Keep the Meiryo proof as reviewed reference; do not treat it as the normal subtitle baseline. |
| ED-10j | Kirinuki Subtitle Font Research & Candidate Audit v0 | in_progress | font_audit_requires_review | 70 | clip-ed10j-kirinuki-font-audit-001 | Review the ED-10j font audit contact sheet and choose the next narrow overlay proof candidate. |
| PB-01 | publish_draft schema v1 | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| PB-02 | private/unlisted upload integration | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| PB-03 | thumbnail 設定 integration | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| PB-04 | upload receipt 記録 | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| INT-01 | YouTube OAuth flow | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| INT-02 | asset_fetch（source audio / video 取得） | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| INT-02a | source audio material contract + fake fetch | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02b | asset_fetch boundary spec only | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02c | local-media-audio normalize | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02d | yt-dlp-audio boundary spec only | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02e | yt-dlp-audio source audio URL fetch | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02f | local source video acquisition | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02g | yt-dlp-video boundary spec only | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-02h | yt-dlp-video source video URL fetch | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01 | tiny render proof | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01a | render preflight / fallback readback | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01b | longer local video render smoke | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01c | subtitle burn-in diagnostic | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01d | subtitle timing / font-filter preflight | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01e | real STT subtitle diagnostic render smoke | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| OUT-01f | cut-scoped subtitle-overlay visual proof | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| INT-03 | bg_removal 受領フロー | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| INT-04 | bg_removal API 呼び出し | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| SH-02L | episode status adapter（GUI MVP 用） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-02 | episode_pack 統合 manifest | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| SH-03 | GUI MVP Phase 1（read-only operator console） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-03b | GUI Phase 2（action 導線） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-03c | GUI Editing tab（ED-01 / ED-02a 範囲のみ） | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-04 | NLMYTGen GUI への逆提案運用 | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-05 | local-preview-pack orchestrator | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-05b | local-preview-pack report QA / polish | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-05b+ | local-preview-pack visual evidence hardening | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-05c | GUI read-only preview pack ingest | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-05d | source-audio preview bridge | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-06 | Non-Repo Artifact Handoff | done | stable | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-07 | Operator Review UX contract | done | blocked | 100 |  | Keep as reference unless a regression or successor lane appears. |
| SH-08 | Human Preview Session Bundle | done | stable | 100 | clip-human-preview-session-001 | Keep as reference unless a regression or successor lane appears. |
| SH-09 | Docs Wiki Dashboard v1.5 | done | stable | 100 | clip-docs-dashboard-001 | Keep as reference unless a regression or successor lane appears. |
| OUT-02 | 音声合成（TTS） | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| OUT-03 | visibility 更新（public 化含む） | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| OUT-04 | 完全自動サムネ合成 | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| OUT-05 | .ymmp ゼロ生成 | proposed | backlog | 0 |  | Promote to approved only after an explicit slice decision. |
| OUT-06 | NLMYTGen 側ファイル編集 | rejected | retired | 0 |  | cross-project 指示なしには編集しない。再利用は CLI subprocess 経由 |
