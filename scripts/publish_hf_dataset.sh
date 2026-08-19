#!/usr/bin/env bash
# Build and upload pberlizov/bpl-benchmark on Hugging Face.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PY="${BPL_PYTHON:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3)"
fi
"$PY" scripts/build_hf_dataset.py
if [[ -z "${HF_TOKEN:-}" && -z "${HUGGING_FACE_HUB_TOKEN:-}" ]]; then
  echo "Set HF_TOKEN (write) and re-run." >&2
  exit 1
fi
"$PY" - <<'PY'
from huggingface_hub import HfApi
from pathlib import Path
api = HfApi()
root = Path("hf")
for path in sorted((root / "data").glob("*.jsonl")):
    api.upload_file(
        path_or_fileobj=str(path),
        path_in_repo=f"data/{path.name}",
        repo_id="pberlizov/bpl-benchmark",
        repo_type="dataset",
    )
    print("uploaded", path.name)
api.upload_file(
    path_or_fileobj=str(root / "README.md"),
    path_in_repo="README.md",
    repo_id="pberlizov/bpl-benchmark",
    repo_type="dataset",
)
print("uploaded README.md")
PY
echo "https://huggingface.co/datasets/pberlizov/bpl-benchmark"
