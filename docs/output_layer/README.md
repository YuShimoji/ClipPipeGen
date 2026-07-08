# Output Layer Readback

This directory holds OUT-01 readback artifacts for the local output/video layer.
They classify current capability, missing inputs, and true gates without source
fetching, media processing, production render, or public upload.

Regenerate the artifacts from the repository root:

```powershell
python -m src.cli.main build-output-layer-gap-report --format json
```

Generated files:

- `video_output_gap_log.json` - machine-readable capability matrix, gap log, proof status, and recommended next slice.
- `output_capability_matrix.md` - reviewer-facing table of output-layer capabilities and blockers.
- `local_output_readback.html` - static no-media readback for quick local inspection.
