#!/usr/bin/env bash
# Live Core-12 H2H. Default conditions are the 2026 public set.
# Progent/CaMeL Core numbers are already in benchmarks/results/; pass
# CONDITIONS=none,progent,camel,drift,authgraph only if you need a re-run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL="${MODEL:-gpt-4o-mini-2024-07-18}"
RUNS="${RUNS:-8}"
SUITE="${SUITE:-core}"
CONDITIONS="${CONDITIONS:-none,drift,authgraph}"
OUT="${OUT:-benchmarks/results/bpl_${SUITE}_h2h_${MODEL//\//_}_r${RUNS}.json}"

echo "BPL ${SUITE} H2H model=$MODEL runs=$RUNS conditions=$CONDITIONS -> $OUT"
python -m benchmarks.live.bpl_live \
  --suite "$SUITE" \
  --model "$MODEL" \
  --runs "$RUNS" \
  --conditions "$CONDITIONS" \
  --out "$OUT"
