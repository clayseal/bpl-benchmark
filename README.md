# BPL-v1.0

[![CI](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](pyproject.toml)

Business-process-logic benchmark for LLM agents: composite policies that no
single in-schema tool call violates.

This pack ships mechanism reproductions of [DRIFT](https://arxiv.org/abs/2506.12104)
and [AuthGraph](https://arxiv.org/abs/2605.26497). Progent and CaMeL are optional
conditions; their Core-12 numbers are in `benchmarks/results/` and are not re-run
by default.

ClaySeal scores in `benchmarks/results/` are published reference numbers. The
ClaySeal implementation is not distributed here.

## Suites (frozen)

| Suite | Size | Role |
|-------|------|------|
| **core** | 12 | Default leaderboard |
| **hard** | 24 | Harder eval; report separately |
| **research_quarantine** | 12 | Paradox cases; not a default leaderboard score |
| **full** | ~132 | Entire pack; appendix |

Membership is [`benchmarks/bpl/SUITES.yaml`](benchmarks/bpl/SUITES.yaml). Do not
expand Core or Hard without a version bump. Protocol:
[`benchmarks/bpl/EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## Install

Python 3.10–3.13.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Integrity (no LLM)

```bash
pytest benchmarks/tests -q
python -m benchmarks.live.bpl_live --list --suite core
python -m benchmarks.live.bpl_live --list --suite hard
```

## Live head-to-head

Credentials from the environment only. See [`.env.example`](.env.example).

```bash
export AZURE_OPENAI_ENDPOINT=...
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_DEPLOYMENTS=gpt-4o-mini-2024-07-18

./scripts/run_bpl_core_h2h.sh          # Core
SUITE=hard ./scripts/run_bpl_core_h2h.sh
```

Default conditions: `none,drift,authgraph`. Report **V**, **P**,
**U = P(1−V)** with suite id, version `BPL-v1.0`, model id, and `runs`.

## Published Core-12 (gpt-5-mini, n=8)

| condition | V | P | U |
|-----------|---|---|---|
| none | 58.3% | 91.2% | 33.1% |
| progent | 58.3% | 88.2% | 30.5% |
| camel | 42.7% | 58.7% | 16.0% |
| clayseal | **0.0%** | 71.0% | **71.0%** |

Artifact: [`benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json).
Details: [`benchmarks/results/bpl_head_to_head.md`](benchmarks/results/bpl_head_to_head.md).

## Non-goals

Not jailbreak ASR, CVE/malware, dual-use bio/chem/nuclear, or single
out-of-schema denies. Do not treat `research_quarantine` as a default
leaderboard score.

## License

MIT. See [`LICENSE`](LICENSE).
