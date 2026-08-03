# Benchmark Portfolio

`benchmark_registry.json` is the finite registration contract for the current
ClipPipeGen output benchmark set: Wiki添削, S1, and OUT-01 through OUT-13. It
counts family-scoped comparison slots, so an exact candidate reused by OUT-11
also remains visible in its original OUT family. `reuse_of` records that reuse;
the denominator is not a claim of unique media bytes.

Build the tracked review surface from the repository root:

```powershell
uv run --offline --no-project --python 3.13 python tools/benchmarks/build_benchmark_portfolio.py `
  --hash-local-media `
  --format json
```

Open `docs/benchmarks/index.html`. The builder emits one card per registered
candidate, `benchmark_portfolio.json`, and `COVERAGE_LEDGER.md`.

Coverage tiers are ordered by what can be inspected on the current host:

- `contract-only`: exact contract identity exists, but no static payload or
  local review package is present.
- `static-reviewable`: a tracked or retained local receipt, caption, plan, or
  HTML/JSON surface can be inspected without claiming playable target media.
- `playable-proxy`: an interactive or media-bearing proxy can be reviewed, but
  it is explicitly not the exact target bytes.
- `fully-viewable`: the candidate review entrypoint and all registered target
  media paths are present. This is technical availability, not fresh human
  acceptance.

The portfolio never changes acceptance, rights, production, publication,
monetization, upload, or visibility state. Generated cards and ledgers are
tracked; all `episodes/` media and review packages remain ignored and untracked.
