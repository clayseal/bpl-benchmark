# BPL-v1 scenario pack

Declarative business-process-logic scenarios for composite-policy evaluation.
The live head-to-head runner stays at `python -m benchmarks.live.bpl_live`.

## Layout

| Path | Role |
|------|------|
| `SUITES.yaml` | **Frozen** Core-12 / Hard-24 / research quarantine |
| `suites.py` | Suite loader for `--suite` |
| `RELEASE.md` | v1.0 checklist + scorecard |
| `EVALUATE.md` | How to score a defense |
| `schema.py` | `Scenario` / `Env`, script helpers |
| `registry.py` | `SCENARIOS` dict + `--list` helpers |
| `scenarios/legacy.py` | Original 5 simulated scenarios (gold H2H) |
| `scenarios/aggregate.py` | Family A: longer aggregate / sequence |
| `scenarios/escape.py` | Family B: privilege escape / scope creep |
| `scenarios/confidentiality.py` | Family C: leak-inspired confidentiality |
| `scenarios/frontier.py` | Difficulty 4–5 traps for strong tool-using models |
| `scenarios/ultra.py` | Collusion, rolling windows, goal drift, self-minted authority |
| `scenarios/literature.py` | MAST / AgentLAB / PhantomPolicy / incident-grounded traps |
| `scenarios/deep.py` | Stego-collusion, tacit pricing, multi-turn loss, SCOPEGATE, MSMP |
| `scenarios/aml.py` | FATF/ACAMS typology translations (smurf, layer, fan-out, TBML, …) |
| `scenarios/unorthodox.py` | Tax step-tx, spoofing, sterile cockpit, Swiss cheese, SoD, … |
| `scenarios/crossdomain.py` | Economic substance, wash trade, HACCP, CoC, escrow, … |
| `scenarios/specialty.py` | Protocol stack, SIU cluster, COLREG, DURC/IRE, bid cartel, advantage |
| `scenarios/institutional.py` | KYC expiry, auto-stay, PO split, RTBF restore, JIT IAM, CAPA, privilege, MEL |
| `scenarios/apex.py` | Approval launder, mandate union, quorum aliases, gross/net, … |
| `scenarios/nightmare.py` | Policy skew, FX arb, omission, idempotency, path ceilings, … |
| `scenarios/paradox.py` | Heisenberg, lacuna, LTL, NAF, two-clock, … |
| `scenarios/edgecases.py` | Long, short, plain-sight, stacked edge cases |
| `APEX.md` / `PARADOX.md` / `EDGECASES.md` | Hard-tier design notes |
| `INSTITUTIONAL_SOURCES.md` | Governance / time-bound / threshold mines |
| `AML.md` | AML stage/typology → BPL map |
| `UNORTHODOX_SOURCES.md` | Cross-domain mines: tax, aviation, market abuse, SoD, Swiss cheese, … |
| `LITERATURE.md` | Citations + mapping from papers/incidents → scenarios |

## Fairness rules

1. **Progent-blind on the violating path.** Each tool call in the violating
   script is in the scenario OpenAI tool allowlist (per-call schema check
   passes). Aggregate / scope / sequence controls catch the breach.
2. **CaMeL-untainted when the user prompt fully specifies the task.** Arguments
   come from the trusted prompt (or are not the sole taint source for the
   consequential step). No prompt-injection strings.
3. **Privilege-escape cases** express overreach as sequence/scope growth the
   user asked for, not as a single out-of-schema tool that Progent would deny.

## Non-goals

Not in scope: jailbreak/injection ASR; CVE/malware PoCs; dual-use bio or
chem/nuclear weaponization; single out-of-schema tool denies. See `SUITES.yaml`
`non_goals` and `RELEASE.md`.

## Frozen suites (BPL-v1.0)

| Suite | Command | Role |
|-------|---------|------|
| **core** (12) | `python -m benchmarks.live.bpl_live --list --suite core` | Default leaderboard |
| **hard** (24) | `--suite hard` | Harder; report separately |
| **research_quarantine** | `--suite research_quarantine` | Paradox; not a default leaderboard score |
| **full** | `--suite full` | Entire pack (appendix) |

Live Core H2H: `./scripts/run_bpl_core_h2h.sh` · details: `EVALUATE.md`.

## Adding a scenario

1. Implement a builder returning `Scenario(...)` in the right family module.
2. Register it in that module’s `*_BUILDERS` dict (picked up by `registry.py`).
3. Provide `violating_script` and `compliant_script` (≥ `min_steps` for new
   scenarios; typically `max_iters=40`).
4. Set `family` and `difficulty`.
5. Extend `benchmarks/tests/test_bpl_scenarios.py` coverage (parametrized over
   the registry; usually automatic).
6. **Do not** add new scenarios to Core/Hard without bumping `SUITES.yaml`
   version. Prefer the Full pack; quarantine paradox-class cases under tag
   `paradox` / `research_quarantine`.

For scoring someone else’s defense: see [`EVALUATE.md`](EVALUATE.md).

## Run H2H

```bash
# list pack
python -m benchmarks.live.bpl_live --list
python -m benchmarks.live.bpl_live --list --family escape

# live measure (needs Azure OpenAI env)
python -m benchmarks.live.bpl_live --scenario payout-splitting \
  --conditions none,progent,camel --runs 8

# scripted unit tests (no LLM)
pytest benchmarks/tests/test_bpl_scenarios.py -q
```

## Frontier-hard tier (`tags` include `frontier`)

For models that still violate after an explicit ceiling in the user prompt:

| Trap | Example scenario |
|------|------------------|
| Implicit policy (must `load_policy`) | `split-approval-union`, `fee-plus-principal-stack` |
| Delayed blast (stage OK, commit violates) | `staged-batch-commit` |
| Label laundering (fees share ledger) | `fee-plus-principal-stack` |
| Urgency theater (SLA / CEO banners) | `breakglass-without-incident` |
| Delegation widening | `delegate-then-widen` |
| Patch the guardrail, not the bug | `policy-file-patch` |
| Same-domain wrong mailbox | `same-domain-wrong-mailbox` |
| Joint re-identification | `reidentifying-aggregate-posts` |

## Ultra tier (`tags` include `ultra`)

| Trap | Example scenario |
|------|------------------|
| Sibling-session collusion | `sibling-session-collusion` |
| Rolling-window hour skew | `rolling-window-hour-skew` |
| Trusted follow-up goal drift | `trusted-followup-goal-drift` |
| Self-minted approval tokens | `self-minted-approval-token` |
| Shadow dual-write / auto-promote | `shadow-dual-write` |
| Cover-story backup → external replica | `cover-story-backup-replicate` |

## Literature tier (`tags` include `literature`)

See [`LITERATURE.md`](LITERATURE.md) for full citations (MAST, Hammond multi-agent
risks, AgentLAB, PhantomPolicy, incident registries, plus the **deep** tier:
Motwani stego-collusion, Calvano tacit pricing, Laban multi-turn loss, Liu
lost-in-the-middle, SCOPEGATE, confused-deputy token audience, TOCTOU, SMSR MSMP).
