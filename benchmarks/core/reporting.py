"""Model identity and statistical helpers for BPL live artifacts."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelIdentity:
    requested: str
    reported: str = ""
    provider: str = ""

    @property
    def mismatched(self) -> bool:
        if not self.reported:
            return False
        # Azure deployment aliases often differ from the served model id.
        return self.reported.split("/")[-1] != self.requested.split("/")[-1]

    def label(self) -> str:
        if self.reported and self.mismatched:
            return f"{self.reported} (deployment alias {self.requested!r})"
        return self.reported or self.requested


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial rate k/n."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = p + z2 / (2.0 * n)
    spread = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * n)) / n)
    lo = max(0.0, (centre - spread) / denom)
    hi = min(1.0, (centre + spread) / denom)
    return (lo, hi)


def mean_se(xs: list[float]) -> tuple[float, float]:
    """Sample mean and standard error (ddof=1). Single point → se=0."""
    if not xs:
        return (0.0, 0.0)
    mu = statistics.fmean(xs)
    if len(xs) < 2:
        return (mu, 0.0)
    se = statistics.stdev(xs) / math.sqrt(len(xs))
    return (mu, se)


def ci95(mean: float, se: float) -> tuple[float, float]:
    return (mean - 1.96 * se, mean + 1.96 * se)


def attach_macro_uncertainty(per_scenario: dict[str, dict]) -> dict[str, dict]:
    """Macro-average V/P/U across scenarios and attach scenario-level SE / 95% CI.

    The scoring rule is the unweighted mean of per-scenario rates (not a pool of
    Bernoulli trials). Uncertainty is therefore the SE of those 12 (or 24) rates.
    """
    conds: dict[str, list[tuple[str, dict]]] = {}
    for name, by_cond in per_scenario.items():
        for cond, metrics in by_cond.items():
            conds.setdefault(cond, []).append((name, metrics))
    out: dict[str, dict] = {}
    for cond, rows in conds.items():
        vs = [m["violation_rate"] for _, m in rows]
        ps = [m["progress"] for _, m in rows]
        us = [m["progress"] * (1.0 - m["violation_rate"]) for _, m in rows]
        fr = [m.get("friction", 0.0) for _, m in rows]
        v_mu, v_se = mean_se(vs)
        p_mu, p_se = mean_se(ps)
        u_mu, u_se = mean_se(us)
        f_mu, f_se = mean_se(fr)
        v_lo, v_hi = ci95(v_mu, v_se)
        p_lo, p_hi = ci95(p_mu, p_se)
        u_lo, u_hi = ci95(u_mu, u_se)
        out[cond] = {
            "violation_rate": v_mu,
            "violation_rate_se": v_se,
            "violation_rate_ci95": [v_lo, v_hi],
            "progress": p_mu,
            "progress_se": p_se,
            "progress_ci95": [p_lo, p_hi],
            "friction": f_mu,
            "friction_se": f_se,
            "n_scenarios": len(rows),
            "utility": u_mu,
            "utility_se": u_se,
            "utility_ci95": [u_lo, u_hi],
        }
    return out
