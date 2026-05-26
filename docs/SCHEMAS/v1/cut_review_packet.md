# cut_review_packet.schema (v1)

`build-cut-review-packet` turns an existing `edit_pack.json` and `transcript.json` into review artifacts for human final cut/context review. It does not change cut timing, select final cuts, render video, approve rights, or create production output.

## CLI

```powershell
python -m src.cli.main build-cut-review-packet `
  --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 `
  --nle-manifest episodes\jp_pilot01_hololive_bancho_20260525\exports\jp_pilot01r3_subtitle_import\nle_export_manifest.json `
  --render-manifest episodes\jp_pilot01_hololive_bancho_20260525\renders\jp_pilot01r3_subtitle_import_diagnostic_render\render_manifest.json `
  --output-dir episodes\jp_pilot01_hololive_bancho_20260525\review\jp_pilot01r3_cut_review `
  --format json
```

## Outputs

| File | Purpose |
|---|---|
| `cut_review_packet.json` | Machine-readable selected-cut review packet |
| `cut_review_report.html` | Human-readable comparison table for cut review |
| `evidence_summary.json` | Machine-readable ED-10/R3 input/output/boundary evidence |
| `evidence_summary.html` | Human-readable evidence summary and reproduction commands |

## Cut Fields

Each `cuts[]` entry includes:

- `cut_id`, `start_seconds`, `end_seconds`, `duration_seconds`
- `candidate_reason`, `context_status`, `context_notes`
- `source_segment_ids`, `source_segment_count`
- `subtitle_event_count`, `subtitle_density_per_second`, `subtitle_char_count`
- `needs_review_reason_category`, `needs_review_reason_categories`
- `suggested_human_review_focus`
- `decision_placeholder.final_decision="undecided"`

The packet deliberately does not set final decisions. Allowed future values are `accept`, `reject`, `adjust`, and `needs_more_review`, but choosing one is a human/acceptance step.

## Boundary

`production_candidate` is always `false`. Diagnostic render references are evidence only and remain non-production. `rights_manifest.compliance_check.status=pending` is allowed for local review packet generation, but it is not production/public-use approval.
