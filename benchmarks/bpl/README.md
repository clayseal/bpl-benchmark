# BPL scenario pack

Scenario definitions for BPL-v1.0. Live runner:
`python -m benchmarks.live.bpl_live`. Protocol:
[`EVALUATE.md`](EVALUATE.md).

## Layout

| Path | Role |
|------|------|
| `SUITES.yaml` | Which scenarios belong to `core` (12), `hard` (24), research quarantine |
| `suites.py` / `freeze.py` | Load suites; compute the freeze fingerprint hash |
| `schema.py` | Scenario and environment types |
| `worlds/` | SQLite company simulation (`acme-sqlite-v1`) |
| `ENVS.md` | Environment contract |
| `registry.py` | Scenario registry |
| `scenarios/` | Scenario implementations |

## Fairness rules

Tools on the violating path must be in the model’s allowlist. User messages are
tasks, without injection payloads. The bad script must have a legal prefix; CI
enforces that on `core` and `hard`.

## Suites

| Suite | Count | Use |
|-------|------:|-----|
| **`core`** | 12 | Default leaderboard |
| **`hard`** | 24 | Harder set; report separately |
| **`research_quarantine`** | 12 | Not for scoring |
| **`full`** | 132 | Diagnostics only |

Do not add names to `core` or `hard` without a version bump.

```bash
python -m benchmarks.live.bpl_live --protocol
python -m benchmarks.live.bpl_live --list --suite core
pytest benchmarks/tests -q
```
