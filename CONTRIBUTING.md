# Contributing

## Leaderboard freeze

Core-12 and Hard-24 are immutable for `BPL-v1.0`. Do not add, remove, reorder,
or edit those scenarios without a version bump (`SUITES.yaml` + freeze tests).

```bash
python -m benchmarks.live.bpl_live --protocol
pytest benchmarks/tests/test_bpl_protocol.py -q
```

If the freeze `sha256` changes, the PR is a new protocol version, not a drive-by
fix.

## Adding a diagnostic scenario (Full pack)

1. Implement a builder in the matching `benchmarks/bpl/scenarios/*.py` module.
2. Register it in that module’s `*_BUILDERS` dict.
3. Provide `violating_script` and `compliant_script`.
4. The violating script must have a **tipping point**: some proper prefix is
   legal, the full script is not. Every tool on that path must be in the OpenAI
   allowlist (Progent-blind).
5. `violated(env)` / `progress(env)` are programmatic. No LLM-as-judge.
6. Do not add prompt-injection strings.
7. Do **not** put it on Core or Hard.

Quarantine paradox / near-algorithmic cases under tag `paradox` and the
`research_quarantine` suite.

## New defense condition

Add a gate in `benchmarks/live/bpl_live.py` (and `KNOWN_CONDITIONS`). Do not
change prompts, tools, or oracles. Open a PR with Core-12 `n≥8` JSON that
includes `freeze.sha256`.
