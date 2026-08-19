---
license: mit
pretty_name: BPL-v1.0
task_categories:
  - text-generation
tags:
  - agents
  - benchmark
  - tool-use
  - business-policy
  - policy-compliance
size_categories:
  - n<1K
configs:
  - config_name: scenarios
    default: true
    data_files: data/scenarios.jsonl
  - config_name: core_h2h
    data_files: data/core_h2h.jsonl
  - config_name: hard_h2h
    data_files: data/hard_h2h.jsonl
  - config_name: freeze
    data_files: data/freeze.jsonl
---

# BPL-v1.0

**BPL** (Business Process Logic) scores tool-using agents on business rules that
apply across a whole session inside a simulated company (spend caps, approvals,
confidentiality). The user message is trusted. Outcomes are checked with SQL on
a SQLite ledger.

Code: https://github.com/clayseal/bpl-benchmark

## Files

| Config | Contents |
|--------|----------|
| **`scenarios`** | 132 public scenarios (prompt, tools, family). The `role` column marks the 12-scenario **core** leaderboard set, the 24-scenario **hard** set, or diagnostic cases. |
| **`core_h2h`** | Live scores for **core** (8 episodes per cell; gpt-5-mini). |
| **`hard_h2h`** | Live scores for **hard** (separate table from core). |
| **`freeze`** | Protocol fingerprint (SHA-256). |

## Columns in h2h files

**`violation_rate`** — share of episodes where the oracle flagged a broken rule  
**`progress`** — share of work completed  
**`condition`** — gate name (`none` = undefended; others match the GitHub baselines)

`6a6560f26052b6b205c347c0ec2d0264a19c71a8a8ea69ce42e635b4fa6f422f`
