# Acme environments

BPL episodes run inside a SQLite company (`acme-sqlite-v1`). One in-memory
database per episode. Tools mutate tables. Oracles `SELECT`. The freeze
fingerprint (prompts, tool schemas, scripts) is unchanged.

Code: `benchmarks/bpl/worlds/`.

## Engine

`acme-sqlite-v1`: one in-memory database per episode (`benchmarks/bpl/worlds/`).

| Table | Holds |
|-------|--------|
| `journal` + `accounts` | Double-entry cents (pays, refunds, wires) |
| `employees` / `grants` / `repo_state` / `deploy_keys` | IAM and repo scope |
| `customers` / `documents` | CRM + retention |
| `messages` | Mail and Slack, with destination and sensitivity |
| `purchase_orders` | Procurement lines |
| `drafts` / `approvals` | SoD prepare/approve |
| `permits` | Site-level cumulative impact |
| `tool_log` | Every tool call, args, result |
| `state_snap` | JSON snapshot of legacy `env.state` (Hard / Full) |

Live artifacts record `environment.name = acme-sqlite-v1`. Each episode may
include `world.digest` (sha256 of the SQL dump).

## Scored suites

| Suite | Runtime |
|-------|---------|
| **Core-12** | Native. Tools write the tables above. `violated` / `progress` are queries. |
| **Hard-24** | Same kernel. Handler logic is unchanged; every call is journaled and `env.state` is snapshotted so the episode is inspectable. |
| Full / quarantine | Same journal as Hard. |

Core-12 return strings are byte-stable vs BPL-v1.0 dict handlers so published
Progent / CaMeL / DRIFT / AuthGraph cells remain comparable.

## Inspect

```python
from benchmarks.bpl.registry import get_scenario
from benchmarks.bpl.schema import run_script

scen = get_scenario("payout-splitting")
env = run_script(scen, scen.violating_script)
print(env.world.summary())
print(env.world.dump_sql()[:500])
```

Integrity: `pytest benchmarks/tests/test_bpl_worlds.py`.
