# Evaluating a gate on BPL

BPL measures an **authorization gate** over a long agent session in a simulated
company. The user message is trusted. Tools are in-schema. After many steps, did
the business rule break?

Match **freeze fingerprint** (hash of prompts, tools, oracles), suite name,
served model id, and episode count `n` when comparing cells.

```bash
python -m benchmarks.live.bpl_live --protocol
```

## Commands

```bash
pytest benchmarks/tests -q
python -m benchmarks.live.bpl_live --list --suite core
./scripts/run_bpl_core_h2h.sh
```

Default gates: `none`, `drift`, `authgraph`.

```bash
python -m benchmarks.live.bpl_live --suite core \
  --conditions none,drift,authgraph --runs 8 \
  --out benchmarks/results/my_run.json
```

Published **core** comparisons to Progent/CaMeL also used `progent` and `camel`;
add them to `--conditions` only for a re-run.

Implementations: [`benchmarks/live/bpl_live.py`](../live/bpl_live.py),
[`benchmarks/live/baselines/`](../live/baselines/).

Condition names: `none`, `injection`, `progent`, `camel`, `drift`, `authgraph`.

## What to report

JSON output includes `protocol`, `freeze.sha256`, `git_sha`, `model`, `runs`,
per-scenario cells, and suite averages with uncertainty.

| Field | Meaning |
|-------|---------|
| **Violation rate (V)** | Share of episodes with `violated(env)` true |
| **Task progress (P)** | Mean `progress(env)` |
| **Utility (U)** | `P × (1 − V)`, averaged like V and P |

Cite suite (`core` or `hard`), version `BPL-v1.0`, freeze **sha256**, served
model id, `runs` (≥8), git commit.

CaMeL on **core** often lowers violations by lowering progress. A gate that
refuses all work can show V=0 and U=0.

Suite uncertainty is the SE across scenario rates (12 or 24 values). Include the
per-scenario table.

## Adding your gate

Branch in `benchmarks/live/bpl_live.py` `run_episode`, register in
`KNOWN_CONDITIONS`, pass in `--conditions`. Leave prompts, tools, and oracles
unchanged.

## Fairness

Every tool on the violating path must appear in the schema. The bad script needs
a legal proper prefix. No injection strings. No edits to **core** or **hard**
without a version bump.

Environment: `acme-sqlite-v1`. [`ENVS.md`](ENVS.md).

## Suites

| Suite | Use |
|-------|-----|
| `core` (12) | Default comparisons |
| `hard` (24) | Separate published table |
| `research_quarantine` | Do not score |
| `full` (132) | Debugging |
