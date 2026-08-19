# BPL-v1.0

[![CI](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](pyproject.toml)

**BPL** (Business Process Logic) runs live episodes with a tool-using agent inside
a simulated company.

The user message states the assignment. The agent gets a fixed tool
list (pay, grant access, send mail, etc.). Individual calls can pass a per-call
check and still add up to a violation: total spend over a ceiling, an approval
chain that one person walked through, customer data in the wrong mailbox.

We score whether an authorization **gate** blocks those outcomes while the agent
still finishes real work.

GitHub: [clayseal/bpl-benchmark](https://github.com/clayseal/bpl-benchmark)  
Dataset: [pberlizov/bpl-benchmark](https://huggingface.co/datasets/pberlizov/bpl-benchmark)

Evaluation protocol: [`benchmarks/bpl/EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## Scope

BPL targets **policy compliance on long agent sessions**. It does not measure
jailbreak rate, toxic generation, or malware reproduction. There is no hidden
adversary in the prompt.

## How a run works

The model receives a work request and may call tools until it stops or hits a
step cap. An optional gate runs before each call; prompts and tools stay fixed
either way.

State lives in a SQLite company simulation (`acme-sqlite-v1`). Oracles are SQL
queries on that database. We do not use a second LLM as judge.

In each scored scenario, a short prefix of the “bad” tool sequence is legal. The
full sequence crosses the line. CI checks that property.

[`benchmarks/bpl/ENVS.md`](benchmarks/bpl/ENVS.md) describes the environment.

## Scenario families

| Family | What breaks |
|--------|-------------|
| **Aggregate** | Session total, count, or time window over a limit |
| **Escape** | Scope or duty separation erodes over many steps |
| **Confidentiality** | Data sent or aggregated beyond what policy allows |

Per-call checks often pass because each payment, widen, or read is small and
in-schema.

## Metrics

An **episode** is one run of one scenario under one gate. Published cells use
8 episodes (`n=8`).

| Short | Name | Meaning |
|-------|------|---------|
| **V** | Violation rate | Fraction of episodes where the SQL oracle reports a broken rule. Lower is better. |
| **P** | Task progress | Fraction of the assignment completed (see protocol for per-scenario definitions). Higher is better. |
| **U** | Utility | `P × (1 − V)`. Drops when a gate blocks violations by blocking the job. |

The suite row is an unweighted mean over scenarios (12 or 24). The runner prints
standard errors and 95% intervals for that mean.

Low **V** alone is not enough. Check **P** and **U** before calling a gate an
improvement.

## Suites

Lists are frozen in [`benchmarks/bpl/SUITES.yaml`](benchmarks/bpl/SUITES.yaml).
Adding scenarios to a scored suite requires a version bump (e.g. v1.1).

| Name in code | Size | Role |
|--------------|------|------|
| **`core`** | 12 | Default scored set |
| **`hard`** | 24 | Harder composites; publish on its own table |
| **`research_quarantine`** | 12 | Paradox cases for monitor research; no leaderboard |
| **`full`** | 132 | Full catalog for debugging |

“Core-12” and “Hard-24” in older notes mean the `core` and `hard` lists above.

```bash
python -m benchmarks.live.bpl_live --list --suite core
python -m benchmarks.live.bpl_live --list --suite hard
```

**Freeze fingerprint:** SHA-256 over prompts, tools, and oracles in the scored
suites. Compare runs only at the same hash.

```bash
python -m benchmarks.live.bpl_live --protocol
```

`6a6560f26052b6b205c347c0ec2d0264a19c71a8a8ea69ce42e635b4fa6f422f`

## Gates (conditions)

| Name | Description |
|------|-------------|
| **`none`** | No gate; calls execute as requested |
| **`progent`** | Per-call allowlist per [Progent](https://arxiv.org/abs/2504.11703); reimplemented in this repo |
| **`camel`** | Dataflow taint gate per [CaMeL](https://arxiv.org/abs/2503.18813); reimplemented in this repo |
| **`drift`** | [DRIFT](https://arxiv.org/abs/2506.12104)-style planner plus validator; reimplemented |
| **`authgraph`** | [AuthGraph](https://arxiv.org/abs/2605.26497)-style graph plus arg sourcing; reimplemented |

Source: [`benchmarks/live/bpl_live.py`](benchmarks/live/bpl_live.py),
[`benchmarks/live/baselines/`](benchmarks/live/baselines/).

New runs usually include `none`, `drift`, and `authgraph`. The **core** table
below also includes `progent` and `camel` for comparison to published
mechanisms.

## Published baselines (gpt-5-mini, 8 episodes per cell)

Azure deployment id `gpt-4o-mini-2024-07-18`; API returned **gpt-5-mini**. Report
the served model id on every cell.

Numbers below are rerunnable from this repository. We do not ship scores for
closed products.

### Core suite (12 scenarios)

| Gate | Violation rate | 95% CI | Task progress | Utility |
|------|---------------:|--------|--------------:|--------:|
| none | 58.3% | [31.6, 85.0] | 91.2% | 33.1% |
| progent | 58.3% | [32.5, 84.2] | 88.2% | 30.5% |
| camel | 42.7% | [14.0, 71.4] | 58.7% | 16.0% |

[`benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json)

On **core**, `progent` does not move violation rate: every tool in the bad path
is already in the schema. `camel` cuts violations together with progress.

### Hard suite (24 scenarios)

| Gate | Violation rate | 95% CI | Task progress | Utility |
|------|---------------:|--------|--------------:|--------:|
| none | 19.3% | [6.4, 32.1] | 81.1% | 65.6% |
| drift | 10.4% | [1.0, 19.8] | 60.2% | 52.4% |
| authgraph | 14.1% | [0.8, 27.4] | 61.9% | 49.9% |

[`benchmarks/results/bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json)

Most **hard** scenarios saw zero violations in eight episodes for this model. The
suite average is driven by collusion, layering, staged batch commits, and
smurfing. Pair violation rate with task progress when reading gate rows.

### Zeros and confidence intervals

With `n=8`, zero violations in every episode still leaves a wide one-sided bound
(about 37% for one scenario). Treat a printed 0% as a small sample. Run more
episodes if you need a tight claim.

## Install

Python 3.10–3.13.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Integrity checks (no LLM)

```bash
pytest benchmarks/tests -q
python -m benchmarks.live.bpl_live --protocol
```

## Live runs

Credentials from the environment. [`.env.example`](.env.example).

```bash
export AZURE_OPENAI_ENDPOINT=...
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_DEPLOYMENTS=gpt-4o-mini-2024-07-18

./scripts/run_bpl_core_h2h.sh
SUITE=hard ./scripts/run_bpl_core_h2h.sh
```

Publishable cell: **`core` suite**, **≥8 episodes**, freeze hash, served model
id, git commit. Custom gates: [`EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## Related work

[AgentDojo](https://github.com/ethz-spylab/agentdojo) (prompt injection),
[τ-bench](https://github.com/sierra-research/tau-bench) (policy dialogue),
[Progent](https://arxiv.org/abs/2504.11703) and [CaMeL](https://arxiv.org/abs/2503.18813)
(per-call defenses we reimplement here).

## Cite

[`CITATION.cff`](CITATION.cff).

## License

MIT. [`LICENSE`](LICENSE).
