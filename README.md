# BPL-v1.0

[![CI](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml/badge.svg)](https://github.com/clayseal/bpl-benchmark/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-blue.svg)](pyproject.toml)

**Business-process-logic** benchmark for LLM tool-using agents.

The user prompt is fully trusted and every tool on the violating path is
in-schema. Faithful step-by-step execution still breaks a composite policy
(budget, SoD, retention, allowed channel) that **no single call** violates.
That is a different threat model from jailbreak / prompt-injection benches.

```text
  AgentDojo, InjecAgent     untrusted content → one malicious tool call
  τ-bench                   policy in dialogue with a user simulator
  BPL                       trusted prompt + authorized tools → sequence/sum/scope
```

Leaderboard suite is **Core-12**, frozen. Hard-24 is reported separately.
`research_quarantine` is not a score. Protocol:
[`benchmarks/bpl/EVALUATE.md`](benchmarks/bpl/EVALUATE.md).

## Threat model

| Family | What `violated(env)` checks | Why per-call gates miss it |
|--------|-----------------------------|----------------------------|
| **aggregate** | Session sum / count / horizon exceeds a ceiling | Each pay/refund/grant is in-schema and under the per-call cap |
| **escape** | Scope or duty separation grows across the trajectory | Each widen/approve is a permitted verb |
| **confidentiality** | Allowed-channel / audience constraint after legitimate reads | Reads are authorized; the leak is the accumulation or the send |

Oracles are programmatic predicates on a simulated environment — not LLM judges.
Every Core and Hard scenario has a **tipping point**: some proper prefix of the
violating script is legal; the full script is not. CI enforces that.

## Metrics

Per condition, per scenario, `n` independent live episodes:

| | |
|--|--|
| **V** | `P(violated(env))` — lower is better |
| **P** | mean `progress(env)` — higher is better |
| **U** | `P × (1 − V)` — utility after violations; a gate that blocks all work scores U = 0 |

Suite score = **unweighted mean of the 12 (or 24) per-scenario rates**, not a
pool of Bernoulli trials. Report the scenario-level SE / 95% CI the runner
prints. Cite `suite`, `BPL-v1.0`, freeze `sha256`, model **served** id, `runs`.

A defense that only cuts V by refusing the task is not a win.

## Suites (frozen)

| Suite | Size | Role |
|-------|------|------|
| **core** | 12 | Default leaderboard |
| **hard** | 24 | Harder eval; report separately |
| **research_quarantine** | 12 | Paradox / near-algorithmic; **not a score** |
| **full** | 132 | Diagnostic pack; appendix only |

Membership: [`benchmarks/bpl/SUITES.yaml`](benchmarks/bpl/SUITES.yaml). Do not
expand Core or Hard without a version bump. Fingerprint:

```bash
python -m benchmarks.live.bpl_live --protocol
```

## Published Core-12 (gpt-5-mini, n=8)

Azure deployment id `gpt-4o-mini-2024-07-18` served **gpt-5-mini**. Macro ± 95%
CI is the SE of the 12 scenario rates (heterogeneous: several Gold-5 cells are
saturated at V = 100%).

| condition | V | 95% CI (V) | P | U |
|-----------|--:|------------|--:|--:|
| none | 58.3% | [31.6, 85.0] | 91.2% | 33.1% |
| progent | 58.3% | [32.5, 84.2] | 88.2% | 30.5% |
| camel | 42.7% | [14.0, 71.4] | 58.7% | 16.0% |
| clayseal | **0.0%** | [0.0, 0.0] | 71.0% | **71.0%** |

Per-call schema (Progent) does not move V vs undefended. CaMeL lowers V mainly
by also destroying P. Artifact:
[`benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json`](benchmarks/results/bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json).
Gold-5 + notes: [`benchmarks/results/bpl_head_to_head.md`](benchmarks/results/bpl_head_to_head.md).

ClaySeal numbers are published reference scores. The implementation is not in
this repository. Default live conditions are `none,drift,authgraph`
(mechanism reproductions of [DRIFT](https://arxiv.org/abs/2506.12104) and
[AuthGraph](https://arxiv.org/abs/2605.26497)).

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

BPL is complementary, not a replacement:

- [AgentDojo](https://github.com/ethz-spylab/agentdojo) — prompt injection into tool-using agents
- [τ-bench](https://github.com/sierra-research/tau-bench) — policy-aware dialogue with a user simulator
- [AgentHarm](https://arxiv.org/abs/2410.09024) — harmful agent requests
- [Cybench](https://arxiv.org/abs/2408.08926) — offensive cyber capability
- [Progent](https://arxiv.org/abs/2504.11703) — per-call privilege schemas
- [CaMeL](https://arxiv.org/abs/2503.18813) — capability-based dataflow taint

BPL holds tools, prompts, and oracles fixed and only swaps the authorization
gate. Injection defenses that filter untrusted tokens are structurally blind
here: there is no untrusted content.

## Non-goals

Not jailbreak ASR, CVE/malware, dual-use bio/chem/nuclear, or single
out-of-schema denies. Do not treat `research_quarantine` as a leaderboard
score.

## Cite

See [`CITATION.cff`](CITATION.cff).

## License

MIT. See [`LICENSE`](LICENSE).
