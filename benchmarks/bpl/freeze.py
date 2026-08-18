"""Immutable fingerprint of the BPL-v1.0 frozen suites.

A leaderboard cell is only comparable if this fingerprint matches. Expanding
the Full pack does not change it; editing a Core/Hard prompt, tool schema, or
scripted trajectory does. Replacing dict handlers with the SQLite world does
not change it (handlers are not hashed).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from benchmarks.bpl.registry import get_scenario
from benchmarks.bpl.suites import load_suites, scenarios_in_suite


def _scenario_record(name: str) -> dict[str, Any]:
    scen = get_scenario(name)
    return {
        "name": scen.name,
        "family": scen.family,
        "difficulty": scen.difficulty,
        "min_steps": scen.min_steps,
        "max_iters": scen.max_iters,
        "user_prompt": scen.user_prompt,
        "tools": scen.tools,
        "violating_script": list(scen.violating_script),
        "compliant_script": list(scen.compliant_script),
    }


def freeze_payload() -> dict[str, Any]:
    data = load_suites()
    suites = {
        "core": scenarios_in_suite("core"),
        "hard": scenarios_in_suite("hard"),
        "research_quarantine": scenarios_in_suite("research_quarantine"),
    }
    return {
        "version": data["version"],
        "suites": suites,
        "scenarios": {
            name: _scenario_record(name)
            for suite in suites.values()
            for name in suite
        },
    }


def freeze_fingerprint() -> dict[str, Any]:
    payload = freeze_payload()
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return {
        "version": payload["version"],
        "sha256": digest,
        "n_core": len(payload["suites"]["core"]),
        "n_hard": len(payload["suites"]["hard"]),
        "n_research_quarantine": len(payload["suites"]["research_quarantine"]),
    }
