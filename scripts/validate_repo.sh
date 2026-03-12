#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

RUN_BACKEND=1
RUN_FRONTEND=1
RUN_FRONTEND_BUILD=1

usage() {
  cat <<'EOF'
Usage: bash ./scripts/validate_repo.sh [options]

Options:
  --backend-only         Run only the lightweight backend test bundle.
  --frontend-only        Run only the frontend checks.
  --skip-frontend-build  Skip the production frontend build step.
  --help                 Show this help message.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --backend-only)
      RUN_FRONTEND=0
      ;;
    --frontend-only)
      RUN_BACKEND=0
      ;;
    --skip-frontend-build)
      RUN_FRONTEND_BUILD=0
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if [ "$RUN_BACKEND" -eq 0 ] && [ "$RUN_FRONTEND" -eq 0 ]; then
  echo "Nothing to run: both backend and frontend checks are disabled." >&2
  exit 1
fi

cd "$ROOT_DIR"

if [ "$RUN_BACKEND" -eq 1 ]; then
  echo "==> Running lightweight backend test bundle"
  bash ./scripts/test_backend_lite.sh
fi

if [ "$RUN_FRONTEND" -eq 1 ]; then
  echo "==> Running frontend tests"
  npm --prefix frontend test

  if [ "$RUN_FRONTEND_BUILD" -eq 1 ]; then
    echo "==> Running frontend production build"
    npm --prefix frontend run build
  fi
fi
