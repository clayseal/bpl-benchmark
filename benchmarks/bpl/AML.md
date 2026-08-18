# AML → BPL translation map

BPL scenarios are composite-policy unit tests for AML-style typologies in an
agent loop (Progent-blind per call; violation in the sequence).

## Classical AML stage → agent analog

| AML stage (FATF) | Financial meaning | Agent / BPL analog |
|------------------|-------------------|--------------------|
| **Placement** | Illicit value enters the regulated system | First side-effecting tool call that introduces sensitive effect (pay, grant, egress) under a mandate |
| **Layering** | Complex hops obscure the trail | Multi-tool / multi-persona / convert→wire→refund chains that keep each hop under threshold |
| **Integration** | Value re-enters as “legitimate” | Sensitive effect exits via an *allowed* channel (docs, invoice, internal Slack) that launders provenance |

## Typology library → BPL cases

| AML typology | BPL scenario(s) |
|--------------|-----------------|
| **Structuring / smurfing** | Legacy `refund-structuring`, `payout-splitting`, `structured-micro-refunds`; `smurf-just-under-ctr` |
| **Fan-out** | `fanout-egress-spray` |
| **Velocity / burst** | `rapid-velocity-burst`; `multi-day-carry` (horizon) |
| **Layering** | `layering-hop-chain` |
| **Round-tripping** | `round-trip-spend-wash` |
| **Trade-based (TBML)** | `fee-plus-principal-stack`; `tbml-overinvoice` |
| **Mule / straw desks** | `sibling-session-collusion`; `mule-desk-smurf` |
| **Integration / legitimize** | `allowed-channel-drip`; `integration-invoice-cover` |
| **Correspondent nesting** | `delegate-then-widen` |
| **Post-read escalation** | `error-recovery-drop-volume` |
| **Delegated-trust laundering** | `handoff-spec-cascade`; `memory-poison-preference` |

## Design rule for AML-BPL cases

1. **Threshold in policy tool / mandate**, not only the user prompt (placement looks individually authorized).
2. **Violation = aggregate shape** (sum, fan-out cardinality, hop net, round-trip count) — same philosophy as CTR avoidance.
3. **No injection strings** — the “laundering” is faithful task execution that recreates the typology.
