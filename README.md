# BPL-v1.0

[![CI](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](pyproject.toml)

**BPL** (Business Process Logic) is a live benchmark for tool-using agents that
work inside a company for a long session.

The user’s request is trusted. The tools are real company APIs (pay, grant
access, send mail, and so on). Each single call can look fine. The failure mode
is session-scale: the agent finishes the job and a business rule is already
broken — a spend ceiling, a two-person approval rule, a rule about who may see
a record.

This repo asks: **does a policy gate stop that, without stopping legitimate
work?**

**GitHub:** [clayseal/bpl-benchmark](https://github.com/clayseal/bpl-benchmark) ·
**Dataset (catalog + published scores):**
[pberlizov/bpl-benchmark](https://huggingface.co/datasets/pberlizov/bpl-benchmark)

Full evaluation protocol: [`benchmarks/bpl/EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## What BPL is not

BPL is **not** a jailbreak or prompt-injection benchmark. There is no attacker
hidden in the prompt. It is **not** a harmful-content or malware benchmark.

It is closer to **policy compliance for deployed agents**: rules that only make
sense across many steps.

## How a run works

1. The model gets a normal work request and a fixed tool list.
2. It calls tools until it stops or hits a step limit.
3. A **gate** may allow or block each call (see [conditions](#conditions-gates)
   below). Everything else stays the same.
4. A **SQLite** simulation of a company (`acme-sqlite-v1`) records what
   happened. **Pass/fail is checked with SQL**, not with another LLM.

Each scored scenario is built so that **some prefix of the bad path is legal**;
only the full sequence breaks the rule. That is enforced in CI.

Environment details: [`benchmarks/bpl/ENVS.md`](benchmarks/bpl/ENVS.md).

## Scenario families

| Family | Plain-language rule | Why one call at a time looks OK |
|--------|---------------------|----------------------------------|
| **Aggregate** | Total spend, count, or time window exceeds a limit | Each payment or refund is under the per-call cap |
| **Escape** | Scope creep or duty separation breaks over the session | Each widen or approve uses an allowed verb |
| **Confidentiality** | Data goes to the wrong place after allowed reads | Each read is authorized; the leak is what gets sent |

## Metrics

Each **episode** is one independent run of one scenario under one gate. Published
cells use **8 episodes** per scenario per gate (`n=8`).

| Short | Name | Meaning |
|-------|------|---------|
| **V** | Violation rate | Share of episodes where the SQL oracle says the business rule broke. Lower is better. |
| **P** | Task progress | Share of the assigned work completed (definition varies slightly by scenario; see protocol). Higher is better. |
| **U** | Utility | `P × (1 − V)`. Rewards gates that both block violations **and** let work finish. A gate that blocks everything gets U = 0 even if V = 0. |

**Suite score:** unweighted average across scenarios in that suite (12 or 24),
not one big pool of all episodes. The runner prints standard errors and 95%
confidence intervals for the suite mean.

Do not rank gates on **V** alone. A gate that “wins” by refusing the task shows
up as low **P** and low **U**.

## Suites

Suites are fixed lists of scenario names in [`benchmarks/bpl/SUITES.yaml`](benchmarks/bpl/SUITES.yaml).
Do not add scenarios to the scored suites without a version bump (e.g. v1.1).

| Name in code | Size | Role |
|--------------|------|------|
| **`core`** | 12 scenarios | **Default** scored set; use this for comparisons |
| **`hard`** | 24 scenarios | Harder composites; report separately from `core` |
| **`research_quarantine`** | 12 | Research-only paradox cases; **do not** put on a leaderboard |
| **`full`** | 132 | Full catalog for debugging; **do not** score as one leaderboard |

When docs say **“Core-12”** or **“Hard-24”**, they mean the `core` suite (12
scenarios) and the `hard` suite (24 scenarios).

Check membership:

```bash
python -m benchmarks.live.bpl_live --list --suite core
python -m benchmarks.live.bpl_live --list --suite hard
```

**Freeze fingerprint** — a SHA-256 hash of all prompts, tools, and oracles in
the scored suites. Comparable results must cite the same hash:

```bash
python -m benchmarks.live.bpl_live --protocol
```

Current hash: `6a6560f26052b6b205c347c0ec2d0264a19c71a8a8ea69ce42e635b4fa6f422f`

## Conditions (gates)

A **condition** is which authorization gate sits in front of the tools.

| Condition | What it is |
|-----------|------------|
| **`none`** | No extra gate; the model’s tool calls run as requested |
| **`progent`** | Reimplementation of a **per-call tool allowlist** ([Progent paper](https://arxiv.org/abs/2504.11703)); not the authors’ shipped code |
| **`camel`** | Reimplementation of a **dataflow taint** gate ([CaMeL paper](https://arxiv.org/abs/2503.18813)); same caveat |
| **`drift`** | Reimplementation of **DRIFT** ([paper](https://arxiv.org/abs/2506.12104)): plan from the user prompt, block some off-plan or tool-derived args |
| **`authgraph`** | Reimplementation of **AuthGraph** ([paper](https://arxiv.org/abs/2605.26497)): similar, with an authorization graph from prompt + catalog |

All gate code is in this repo ([`benchmarks/live/bpl_live.py`](benchmarks/live/bpl_live.py)
and [`benchmarks/live/baselines/`](benchmarks/live/baselines/)) so you can
audit it. Conclusions are about **these reimplementations**, not about unaudited
vendor products.

Default runs for new work: `none`, `drift`, `authgraph`. The **`core`** table
below also includes `progent` and `camel` for mechanism comparison.

## Published baselines (gpt-5-mini, 8 episodes per cell)

Runs used Azure deployment name `gpt-4o-mini-2024-07-18`; the API reported the
model as **gpt-5-mini**. Label results with the **served** model id.

These are **reproducible baselines**, not a vendor leaderboard. This pack does
**not** publish a score for a proprietary system you cannot run from this repo.

### Core suite (12 scenarios)

| Gate | Violation rate | 95% CI | Task progress | Utility |
|------|---------------:|--------|--------------:|--------:|
| none | 58.3% | [31.6, 85.0] | 91.2% | 33.1% |
| progent | 58.3% | [32.5, 84.2] | 88.2% | 30.5% |
| camel | 42.7% | [14.0, 71.4] | 58.7% | 16.0% |

JSON:
[`benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json)

On **core**, a per-call allowlist (`progent`) does not change the violation
rate: every tool in the bad sequence is already in the schema. The taint gate
(`camel`) lowers violations partly by doing less work (lower progress).

### Hard suite (24 scenarios)

| Gate | Violation rate | 95% CI | Task progress | Utility |
|------|---------------:|--------|--------------:|--------:|
| none | 19.3% | [6.4, 32.1] | 81.1% | 65.6% |
| drift | 10.4% | [1.0, 19.8] | 60.2% | 52.4% |
| authgraph | 14.1% | [0.8, 27.4] | 61.9% | 49.9% |

JSON:
[`benchmarks/results/bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json)

Many **hard** scenarios are easy for this model (zero violations in 8
episodes). The suite average is pulled up by composites such as collusion,
layering, staged batch commits, and smurfing. Read violation rate together with
task progress: some gates reduce violations only by blocking work.

### Zeros and confidence intervals

At `n=8`, a scenario with zero violations in every episode still has a
non-trivial upper bound (roughly 37% for one scenario). A suite macro interval
of `[0, 0]` is misleading when every scenario rate is identical. Treat “0%” as a
small sample, not proof of perfection. Use more episodes if the claim matters.

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

Credentials from the environment only. See [`.env.example`](.env.example).

```bash
export AZURE_OPENAI_ENDPOINT=...
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_DEPLOYMENTS=gpt-4o-mini-2024-07-18

./scripts/run_bpl_core_h2h.sh
SUITE=hard ./scripts/run_bpl_core_h2h.sh
```

Minimum publishable result: **`core` suite**, **≥8 episodes**, freeze hash,
served model id, git commit. Adding your own gate:
[`EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## Related work

- [AgentDojo](https://github.com/ethz-spylab/agentdojo): prompt injection in tool-using agents
- [τ-bench](https://github.com/sierra-research/tau-bench): policy-aware dialogue with a user simulator
- [Progent](https://arxiv.org/abs/2504.11703): per-call privilege schemas
- [CaMeL](https://arxiv.org/abs/2503.18813): capability-based dataflow taint

## Cite

See [`CITATION.cff`](CITATION.cff).

## License

MIT. See [`LICENSE`](LICENSE).
