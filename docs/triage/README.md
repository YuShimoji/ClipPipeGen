# Triage Reports

This directory keeps local, source-backed triage reports that help future
slices separate true safety gates from wording or workflow overcapture.

## TRI-01 Safety Overcapture

`safety_overcapture_report.json` and `safety_overcapture_report.md` classify
current safety language and tests into four groups:

- `true_external_gate`
- `deferred_local_action`
- `allowed_local_action`
- `overcapture_candidate`

The report is readback-only. It does not change fetch, render, rights,
publishing, credential, git, or media-tracking behavior. Later slices can use
it to compress repeated caveats into `automation_contract.json` or an
equivalent thin contract while preserving strict gates.

Regenerate:

```powershell
python -m tools.triage.build_safety_overcapture_report --output-json docs/triage/safety_overcapture_report.json --output-md docs/triage/safety_overcapture_report.md --format json
```

Validate:

```powershell
python -m json.tool docs/triage/safety_overcapture_report.json
python -m pytest -q tests/test_safety_overcapture_triage.py
git diff --check
git ls-files episodes
```
