# Literature → BPL

Citations for scenarios in `scenarios/literature.py` and `scenarios/deep.py`.

## Sources

| Source | Construct in BPL |
|--------|------------------|
| **MAST** — Cemri et al. ([site](https://sites.google.com/berkeley.edu/mast/home), arXiv:2503.13657) | Specification, inter-agent misalignment, verification theater |
| **Multi-Agent Risks from Advanced AI** — Hammond et al. (arXiv:2502.14143) | Miscoordination, conflict, collusion |
| **AgentLAB** — Jiang et al. (arXiv:2602.16901) | Objective drift, memory poisoning, long-horizon tool chaining |
| **PhantomPolicy** (arXiv:2604.12177) | Policy-invisible attributes; accumulated session leakage |
| Incident writeups (Oso, Curity, Unit 42, Meshgate) | Destructive “fix”, fail-open recovery |

## Mapping

| Construct | Scenario |
|-----------|----------|
| MAST FC1 handoff | `handoff-spec-cascade` |
| MAST FC3 verification theater | `rubber-stamp-verifier` |
| MAST FM-1.3 step repetition | `retry-storm-double-effect` |
| Hammond miscoordination | `miscoord-double-fulfill` |
| AgentLAB objective drifting | `observation-objective-drift` |
| AgentLAB memory poisoning | `memory-poison-preference` |
| PhantomPolicy invisible attribute | `invisible-inactive-recipient` |
| PhantomPolicy accumulated leakage | `accumulated-scope-union` |
| Destructive error recovery | `error-recovery-drop-volume` |
| Motwani et al., NeurIPS 2024 — secret collusion | `stego-weather-coord` |
| Calvano et al., AER 2020 — tacit pricing | `tacit-price-match` |
| Laban et al. 2025 — lost in multi-turn | `sharded-ceiling-forgetting` |
| Liu et al., TACL 2024 — lost in the middle | `buried-middle-mandate` |
| SCOPEGATE (arXiv:2606.28679) | `capability-gate-not-value-auth` |
| Confused deputy / RFC 8693 audience | `token-passthrough-audience` |
| TOCTOU | `toctou-stale-approval` |
| SMSR (arXiv:2606.12703) | `msmp-cross-session-retrieve` |
