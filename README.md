# BPL-v1.0

[![CI](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](pyproject.toml)

Long-running agents often lose track of business rules that still apply: spend
ceilings, who may approve a request, who may see a record. Each tool call can
look allowed. The failure is at session scale.

BPL benchmarks how security policies regulate those deployments. Prompts, tools,
and oracles stay fixed. Only the authorization gate changes. Core-12 is the
default suite. Hard-24 is reported separately. Protocol:
[`benchmarks/bpl/EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

**GitHub:** [clayseal/bpl-benchmark](https://github.com/clayseal/bpl-benchmark) ·
**Dataset:** [pberlizov/bpl-benchmark](https://huggingface.co/datasets/pberlizov/bpl-benchmark) on Hugging Face (scenario catalog + published cells).

## Threat model

| Family | What `violated(env)` checks | Why per-call gates miss it |
|--------|-----------------------------|----------------------------|
| **aggregate** | Session sum, count, or horizon blows a ceiling | Each pay, refund, or grant is in-schema and under the per-call cap |
| **escape** | Scope or duty separation grows across the trajectory | Each widen or approve is a permitted verb |
| **confidentiality** | Allowed-channel or audience constraint after legitimate reads | Reads are authorized; the leak is the accumulation or the send |

Oracles are SQL predicates on a SQLite company (`acme-sqlite-v1`). No LLM
judges. Tools post to a ledger, IAM, mail, POs, permits. Every Core and Hard
scenario has a **tipping point**: some proper prefix of the violating script is
legal; the full script is not. CI enforces that. Environments:
[`benchmarks/bpl/ENVS.md`](benchmarks/bpl/ENVS.md).

## Metrics

Per condition, per scenario, `n` independent live episodes:

| | |
|--|--|
| **V** | `P(violated(env))`. Lower is better. |
| **P** | mean `progress(env)`. Higher is better. |
| **U** | `P × (1 − V)`. A gate that blocks all work scores U = 0. |

Suite score is the unweighted mean of the 12 (or 24) per-scenario rates, not a
pool of Bernoulli trials. Report the scenario-level SE / 95% CI the runner
prints. Cite `suite`, `BPL-v1.0`, freeze `sha256`, model **served** id, `runs`.

A defense that only cuts V by refusing the task is not a win.

## Suites (frozen)

| Suite | Size | Role |
|-------|------|------|
| **core** | 12 | Default leaderboard |
| **hard** | 24 | Harder eval; report separately |
| **research_quarantine** | 12 | Paradox cases. Do not score. |
| **full** | 132 | Diagnostic catalog. Do not score. |

Membership: [`benchmarks/bpl/SUITES.yaml`](benchmarks/bpl/SUITES.yaml). Do not
expand Core or Hard without a version bump. Fingerprint:

```bash
python -m benchmarks.live.bpl_live --protocol
```

## Reference numbers (gpt-5-mini, n=8)

Azure deployment id `gpt-4o-mini-2024-07-18` served **gpt-5-mini**; the served
id is what a cell must be labelled with.

These are baselines, not a leaderboard. **This pack ships no score for its own
authors' system**: a benchmark whose headline row is an implementation nobody
outside the project can run is not a benchmark, it is an advertisement. Scores
here come from what you can reproduce from this repository.

### Core-12 (`none`, `progent`, `camel`)

| condition | V | 95% CI (V) | P | U |
|-----------|--:|------------|--:|--:|
| none | 58.3% | [31.6, 85.0] | 91.2% | 33.1% |
| progent* | 58.3% | [32.5, 84.2] | 88.2% | 30.5% |
| camel* | 42.7% | [14.0, 71.4] | 58.7% | 16.0% |

Artifact:
[`benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json).

### Hard-24 (`none`, `drift`, `authgraph`)

| condition | V | 95% CI (V) | P | U |
|-----------|--:|------------|--:|--:|
| none | 19.3% | [6.4, 32.1] | 81.1% | 65.6% |
| drift† | 10.4% | [1.0, 19.8] | 60.2% | 52.4% |
| authgraph† | 14.1% | [0.8, 27.4] | 61.9% | 49.9% |

Artifact:
[`benchmarks/results/bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json).

Hard is a mix: many scenarios are easy for this model; the suite mean is
dominated by composites where session-scale rules still break (collusion,
layering, staged batch commit, smurfing). Read V with P — several gate rows
cut violation only by blocking work.

\* `progent` and `camel` are **mechanism reproductions written for this pack**,
not the authors' released code. They implement the published decision rule — a
per-call privilege schema, and a taint gate on untrusted-derived control flow —
and any conclusion drawn from them is a conclusion about that rule as
reimplemented here. Do not cite these as measurements of the original systems.

† `drift` and `authgraph` are mechanism reproductions of
[DRIFT](https://arxiv.org/abs/2506.12104) and
[AuthGraph](https://arxiv.org/abs/2605.26497), same caveat. Implemented in
[`benchmarks/live/baselines/`](benchmarks/live/baselines/).

Read that way, the Core rows say what they should: a per-call schema does not
move V on this class, because no single call in a violating sequence is out of
schema. A taint gate lowers V partly by lowering P. On Hard, drift and authgraph
move macro V modestly while U falls — the gates stall or block more than they
secure session-scale rules.

### On intervals, and a zero

The macro CI is the SE across the 12 scenario rates, which is the right
uncertainty about the *suite mean* and the wrong one for a cell that is
saturated. When every scenario rate is identical the SE collapses to zero, and
an interval of `[0.0, 0.0]` claims a precision no finite sample supports — an
earlier revision of this file published exactly that.

So: **a zero is reported as a bound, never as a point.** At n=8 a single
scenario with no violations has a 97.5% one-sided upper bound of **36.9%**;
pooled over 12 scenarios, 0 of 96 episodes gives **3.8%**. Both are worth
knowing and neither is zero. n=8 is the minimum for a publishable cell and it is
a low bar; report more if the claim matters.

Default live conditions are `none,drift,authgraph`. Pass `progent,camel` in
`--conditions` for Core mechanism comparisons.

## Install

Python 3.10–3.13.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Integrity (no LLM)

```bash
pytest benchmarks/tests -q
python -m benchmarks.live.bpl_live --protocol
python -m benchmarks.live.bpl_live --list --suite core
python -m benchmarks.live.bpl_live --list --suite hard
```

## Live head-to-head

Credentials from the environment only. See [`.env.example`](.env.example).

```bash
export AZURE_OPENAI_ENDPOINT=...
export AZURE_OPENAI_API_KEY=...
export AZURE_OPENAI_DEPLOYMENTS=gpt-4o-mini-2024-07-18

./scripts/run_bpl_core_h2h.sh          # Core, default none/drift/authgraph
SUITE=hard ./scripts/run_bpl_core_h2h.sh
```

Minimum publishable cell: **suite=core**, **runs≥8**, freeze sha256, served
model id. Hooking another gate: [`EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## Related work

BPL holds tools, prompts, and oracles fixed and only swaps the authorization
gate. There is no untrusted content, so injection filters have nothing to
grab.

- [AgentDojo](https://github.com/ethz-spylab/agentdojo): prompt injection into tool-using agents
- [τ-bench](https://github.com/sierra-research/tau-bench): policy-aware dialogue with a user simulator
- [Progent](https://arxiv.org/abs/2504.11703): per-call privilege schemas
- [CaMeL](https://arxiv.org/abs/2503.18813): capability-based dataflow taint

## Cite

See [`CITATION.cff`](CITATION.cff).

## License

MIT. See [`LICENSE`](LICENSE).
