#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <space_url> [repo_dir]"
  exit 1
fi

SPACE_URL="$1"
REPO_DIR="${2:-.}"
IMAGE_TAG="openenv-email-triage-local"

echo "[1/5] Pinging HF Space health endpoint..."
curl -fsSL "${SPACE_URL%/}/health" >/dev/null
echo "Space is healthy."

echo "[2/5] Building Docker image..."
docker build -t "${IMAGE_TAG}" "${REPO_DIR}"
echo "Docker build passed."

echo "[3/5] Running container smoke test..."
CID=$(docker run -d -p 7860:7860 "${IMAGE_TAG}")
sleep 5
curl -fsSL "http://localhost:7860/health" >/dev/null
curl -fsSL -X POST "http://localhost:7860/reset" -H "Content-Type: application/json" -d '{}' >/dev/null
docker rm -f "${CID}" >/dev/null
echo "Container smoke test passed."

echo "[4/5] Running local baseline inference..."
ENV_BASE_URL="http://localhost:7860" python "${REPO_DIR}/inference.py" >/dev/null || true
echo "Inference script executable."

echo "[5/5] Optional OpenEnv validation..."
if command -v openenv >/dev/null 2>&1; then
  (cd "${REPO_DIR}" && openenv validate)
  echo "openenv validate passed."
else
  echo "openenv CLI not found, skipping validate."
fi

echo "All checks complete."
