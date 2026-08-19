---
license: mit
pretty_name: BPL-v1.0
task_categories:
  - text-generation
tags:
  - agents
  - benchmark
  - ai-safety
  - tool-use
  - business-policy
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

Long-running agents often lose track of business rules that still apply.
BPL benchmarks how security policies regulate those deployments.

The runnable pack is on GitHub:
https://github.com/clayseal/bpl-benchmark

`scenarios` is the full public catalog (132). Core-12 and Hard-24 are the
scored suites. `core_h2h` and `hard_h2h` are published live cells (n=8,
gpt-5-mini served via Azure deployment `gpt-4o-mini-2024-07-18`). Load
`scenarios` (default), `core_h2h`, `hard_h2h`, or `freeze`.

Freeze `sha256`: `6a6560f26052b6b205c347c0ec2d0264a19c71a8a8ea69ce42e635b4fa6f422f`
