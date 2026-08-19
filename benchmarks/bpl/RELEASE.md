# BPL-v1.0 release notes

Frozen scenario lists: [`SUITES.yaml`](SUITES.yaml). Do not expand **core** or
**hard** without a version bump.

Fingerprint:

```bash
python -m benchmarks.live.bpl_live --protocol
```

## Environment

Episodes run on **`acme-sqlite-v1`** (SQLite company simulation).
See [`ENVS.md`](ENVS.md).

## Suites

| Suite | Scenarios | Use |
|-------|----------:|-----|
| **core** | 12 | Default leaderboard |
| **hard** | 24 | Harder set; separate table |
| **research_quarantine** | 12 | Not scored |
| **full** | 132 | Diagnostics only |

## Published scores (gpt-5-mini served, 8 episodes per cell)

### Core suite

| Gate | Violation rate | Task progress | Utility |
|------|---------------:|--------------:|--------:|
| none | 58.3% | 91.2% | 33.1% |
| progent | 58.3% | 88.2% | 30.5% |
| camel | 42.7% | 58.7% | 16.0% |

### Hard suite

| Gate | Violation rate | Task progress | Utility |
|------|---------------:|--------------:|--------:|
| none | 19.3% | 81.1% | 65.6% |
| drift | 10.4% | 60.2% | 52.4% |
| authgraph | 14.1% | 61.9% | 49.9% |

Artifacts: `benchmarks/results/`. Hugging Face:
https://huggingface.co/datasets/pberlizov/bpl-benchmark

## Metric definitions

**Violation rate** — episodes where the business rule broke (lower is better).  
**Task progress** — work completed toward the assignment (higher is better).  
**Utility** — progress × (1 − violation rate); down-weights gates that only block.

Suite rows are unweighted means over 12 or 24 scenarios, with SE / 95% CI on
those scenario rates.

Legacy gold scenarios measure fraction of requested work; other **core** scenarios
use policy-allowed completion.

## Commands

```bash
python -m benchmarks.live.bpl_live --list --suite core
pytest benchmarks/tests/test_bpl_scenarios.py -q
./scripts/run_bpl_core_h2h.sh
```
