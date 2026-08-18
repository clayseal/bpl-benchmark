# AML typology → BPL

Composite-policy encodings of FATF/ACAMS shapes. Violation is the sequence, not
a single in-schema call.

| AML typology | BPL scenario(s) |
|--------------|-----------------|
| Structuring / smurfing | `refund-structuring`, `payout-splitting`, `structured-micro-refunds`, `smurf-just-under-ctr` |
| Fan-out | `fanout-egress-spray` |
| Velocity / burst | `rapid-velocity-burst`, `multi-day-carry` |
| Layering | `layering-hop-chain` |
| Round-tripping | `round-trip-spend-wash` |
| Trade-based (TBML) | `fee-plus-principal-stack`, `tbml-overinvoice` |
| Mule / straw desks | `sibling-session-collusion`, `mule-desk-smurf` |
| Integration | `allowed-channel-drip`, `integration-invoice-cover` |
| Correspondent nesting | `delegate-then-widen` |
| Post-read escalation | `error-recovery-drop-volume` |
| Delegated-trust laundering | `handoff-spec-cascade`, `memory-poison-preference` |
