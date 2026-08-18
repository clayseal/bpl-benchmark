# BPL-v1.0 release notes

Frozen suites live in [`SUITES.yaml`](SUITES.yaml). Do not expand Core/Hard
without a version bump.

## Suites

| Suite | Size | Use |
|-------|------|-----|
| **core** | 12 | Default paper / leaderboard |
| **hard** | 24 | Harder defense eval; report separately |
| **research_quarantine** | 12 | Paradox / near-algorithmic; not a default leaderboard score |
| **full** | ~132 | Growing pack; appendix only |

## Scorecard

Per scenario × condition (`none` / `progent` / `camel` / `drift` / `authgraph`
and published ClaySeal numbers in `benchmarks/results/`):

- **V:** violation rate (lower better)
- **P:** mean task progress (higher better)
- **U = P × (1 − V):** utility-aware suite macro

Progress convention:

- **Gold-5 legacy:** fraction of requested work (unchanged vs published H2H)
- **Other Core:** fraction of policy-allowed work (budget fill / legal completion)

## Commands

```bash
python -m benchmarks.live.bpl_live --list --suite core
pytest benchmarks/tests/test_bpl_scenarios.py -q
./scripts/run_bpl_core_h2h.sh
```

## Non-goals

See `non_goals` in `SUITES.yaml`. Not jailbreak ASR, CVE/malware, dual-use
bio/chem/nuclear, or single out-of-schema denies.

## Pre-release checklist

1. [x] Freeze Core-12 + Hard-24 in `SUITES.yaml`
2. [x] Normalize progress on non-legacy Core aggregates
3. [x] Live Core H2H (≥8 runs). Done for one model (gpt-5-mini via Azure).
4. [x] Results page (gold + Core; Full appendix)
5. [x] How-to evaluate / add scenario docs
6. [x] Explicit non-goals
7. [x] Quarantine paradox from Core/Hard
