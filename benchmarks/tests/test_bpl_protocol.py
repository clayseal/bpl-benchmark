"""Protocol invariants: freeze fingerprint, composite oracles, condition surface."""

from __future__ import annotations

import pytest

from benchmarks.bpl.freeze import freeze_fingerprint
from benchmarks.bpl.registry import get_scenario
from benchmarks.bpl.schema import run_script
from benchmarks.bpl.suites import scenarios_in_suite
from benchmarks.core.reporting import attach_macro_uncertainty, wilson_interval
from benchmarks.live import bpl_live


# Pinned so silent edits to Core/Hard prompts, tools, or scripts fail CI.
# Recompute with: python -m benchmarks.live.bpl_live --protocol
CORE_HARD_FREEZE_SHA256 = (
    "6a6560f26052b6b205c347c0ec2d0264a19c71a8a8ea69ce42e635b4fa6f422f"
)


def test_protocol_cli():
    assert bpl_live.main(["--protocol"]) == 0


def test_unknown_condition_rejected():
    assert bpl_live.main(["--scenario", "payout-splitting", "--conditions", "ivisor"]) == 2


def test_freeze_fingerprint_stable_shape():
    freeze = freeze_fingerprint()
    assert freeze["version"] == "BPL-v1.0"
    assert freeze["n_core"] == 12
    assert freeze["n_hard"] == 24
    assert freeze["n_research_quarantine"] == 12
    assert len(freeze["sha256"]) == 64
    assert freeze["sha256"] == freeze_fingerprint()["sha256"]
    assert freeze["sha256"] == CORE_HARD_FREEZE_SHA256


def _tipping_index(scen) -> int | None:
    for i in range(1, len(scen.violating_script) + 1):
        if scen.violated(run_script(scen, scen.violating_script[:i])):
            return i
    return None


@pytest.mark.parametrize(
    "name",
    scenarios_in_suite("core") + scenarios_in_suite("hard"),
)
def test_leaderboard_suites_have_composite_tipping_point(name: str):
    """The policy is not a single in-schema deny: some proper prefix is legal."""
    scen = get_scenario(name)
    k = _tipping_index(scen)
    assert k is not None, f"{name}: violating_script never violates"
    assert k >= 2, f"{name}: first call alone violates (not composite)"
    prefix = run_script(scen, scen.violating_script[: k - 1])
    assert not scen.violated(prefix)
    full = run_script(scen, scen.violating_script)
    assert scen.violated(full)


@pytest.mark.parametrize(
    "name",
    [
        n
        for n in scenarios_in_suite("core")
        if get_scenario(n).family == "aggregate"
    ],
)
def test_core_aggregate_no_singleton_violation(name: str):
    scen = get_scenario(name)
    for call in scen.violating_script:
        env = run_script(scen, (call,))
        assert not scen.violated(env), f"{name}: {call[0]} alone violates"


def test_macro_uncertainty_matches_scoring_rule():
    per = {
        "a": {"none": {"violation_rate": 1.0, "progress": 1.0, "friction": 0.0}},
        "b": {"none": {"violation_rate": 0.0, "progress": 0.5, "friction": 0.0}},
    }
    macro = attach_macro_uncertainty(per)
    m = macro["none"]
    assert m["violation_rate"] == pytest.approx(0.5)
    assert m["progress"] == pytest.approx(0.75)
    assert m["utility"] == pytest.approx(0.25)  # mean of 0 and 0.5
    assert m["n_scenarios"] == 2
    assert m["violation_rate_se"] == pytest.approx(0.5)
    lo, hi = m["violation_rate_ci95"]
    assert lo < 0.5 < hi


def test_wilson_degenerate():
    lo, hi = wilson_interval(0, 8)
    assert lo == 0.0
    assert 0.0 < hi < 0.4
    lo, hi = wilson_interval(8, 8)
    assert 0.6 < lo < 1.0
    assert hi == 1.0
