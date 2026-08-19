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

**BPL** (Business Process Logic) benchmarks tool-using agents on **session-scale
business rules** inside a simulated company: spend limits, approval rules,
confidentiality. The user prompt is trusted; pass/fail is checked with SQL, not
an LLM judge.

Runnable code: https://github.com/clayseal/bpl-benchmark

## Files in this dataset

| Config | Contents |
|--------|----------|
| **`scenarios`** | All 132 public scenarios (prompt, tools, family, difficulty). Only 12 + 24 are on the default leaderboard — see suite column (`core`, `hard`, or diagnostic). |
| **`core_h2h`** | Published live scores for the **core** suite (12 scenarios × gates × metrics). 8 episodes per cell; model served as gpt-5-mini. |
| **`hard_h2h`** | Same for the **hard** suite (24 scenarios). Report separately from core. |
| **`freeze`** | Version fingerprint (SHA-256). Results are comparable only at the same hash. |

## Metrics (column names in h2h files)

- **`violation_rate`** — fraction of episodes where the business rule broke
- **`progress`** — fraction of assigned work completed
- **`condition`** — gate name (`none` = undefended; others are reimplemented baselines from the GitHub repo)

Freeze hash: `6a6560f26052b6b205c347c0ec2d0264a19c71a8a8ea69ce42e635b4fa6f422f`
