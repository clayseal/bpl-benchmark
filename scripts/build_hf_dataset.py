#!/usr/bin/env python3
"""Build Hugging Face dataset files for pberlizov/bpl-benchmark."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "hf" / "data"
CORE = ROOT / "benchmarks" / "results" / "bpl_core_h2h_gpt-4o-mini-2024-07-18_r8.json"
HARD = ROOT / "benchmarks" / "results" / "bpl_hard_h2h_gpt-4o-mini-2024-07-18_r8.json"


def _flatten_h2h(path: Path, *, suite: str) -> list[dict]:
    data = json.loads(path.read_text())
    model = data["model"]
    runs = data["runs"]
    rows: list[dict] = []
    for scenario, by_cond in data["scenarios"].items():
        for condition, cell in by_cond.items():
            row = {
                "suite": suite,
                "model": model,
                "runs": runs,
                "scenario": scenario,
                "condition": condition,
                "violation_rate": cell["violation_rate"],
                "progress": cell["progress"],
                "friction": cell.get("friction", 0.0),
                "n": cell["n"],
            }
            if cell.get("model_served"):
                row["model_served"] = cell["model_served"]
            rows.append(row)
    rows.sort(key=lambda r: (r["scenario"], r["condition"]))
    return rows


def _scenarios_rows() -> list[dict]:
    from benchmarks.bpl.registry import SCENARIOS, get_scenario
    from benchmarks.bpl.suites import scenarios_in_suite

    core = set(scenarios_in_suite("core"))
    hard = set(scenarios_in_suite("hard"))
    quarantine = set(scenarios_in_suite("research_quarantine"))
    rows: list[dict] = []
    for name in sorted(SCENARIOS):
        scen = get_scenario(name)
        if name in core:
            role = "core"
        elif name in hard:
            role = "hard"
        elif name in quarantine:
            role = "quarantine"
        else:
            role = "diagnostic"
        rows.append(
            {
                "role": role,
                "name": scen.name,
                "family": scen.family,
                "difficulty": scen.difficulty,
                "min_steps": scen.min_steps,
                "max_iters": scen.max_iters,
                "user_prompt": scen.user_prompt,
                "tools": ";".join(t["function"]["name"] for t in scen.tools),
            }
        )
    return rows


def main() -> None:
    from benchmarks.bpl.freeze import freeze_fingerprint

    OUT.mkdir(parents=True, exist_ok=True)

    scenarios = OUT / "scenarios.jsonl"
    with scenarios.open("w") as f:
        for row in _scenarios_rows():
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    core_h2h = OUT / "core_h2h.jsonl"
    with core_h2h.open("w") as f:
        for row in _flatten_h2h(CORE, suite="core"):
            f.write(json.dumps(row) + "\n")

    hard_h2h = OUT / "hard_h2h.jsonl"
    with hard_h2h.open("w") as f:
        for row in _flatten_h2h(HARD, suite="hard"):
            f.write(json.dumps(row) + "\n")

    freeze = OUT / "freeze.jsonl"
    with freeze.open("w") as f:
        f.write(json.dumps(freeze_fingerprint()) + "\n")

    print(f"wrote {scenarios} ({len(_scenarios_rows())} rows)")
    print(f"wrote {core_h2h}")
    print(f"wrote {hard_h2h}")
    print(f"wrote {freeze}")


if __name__ == "__main__":
    main()
