# BPL-v1 scenario pack

Scenarios for the long shift: an internal agent, authorized tools, a rule that
only exists after many steps. Live runner: `python -m benchmarks.live.bpl_live`.
Protocol: [`EVALUATE.md`](EVALUATE.md).

## Layout

| Path | Role |
|------|------|
| `SUITES.yaml` | Frozen Core-12 / Hard-24 / research quarantine |
| `suites.py` / `freeze.py` | Suite loader + freeze fingerprint |
| `schema.py` | `Scenario` / `Env` |
| `registry.py` | Builders |
| `scenarios/` | Scenario modules |

## Fairness

1. **Progent-blind.** Every tool on the violating path is in the OpenAI allowlist.
2. **No injection strings.** The user prompt is the task.
3. **Tipping point.** A proper prefix of the violating script is legal; the full script is not. CI enforces this on Core and Hard.

## Frozen suites

| Suite | Command | Role |
|-------|---------|------|
| **core** (12) | `--list --suite core` | Default leaderboard |
| **hard** (24) | `--list --suite hard` | Report separately |
| **research_quarantine** | `--list --suite research_quarantine` | Do not score |
| **full** | `--list --suite full` | Appendix |

Do not add scenarios to Core/Hard without a version bump. Prefer Full; tag
paradox cases `paradox` / `research_quarantine`.

```bash
python -m benchmarks.live.bpl_live --protocol
python -m benchmarks.live.bpl_live --list --suite core
pytest benchmarks/tests -q
```
