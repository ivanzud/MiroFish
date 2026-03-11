#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${1:-666ghj/MiroFish}"
FORK_REMOTE="${FORK_REMOTE:-origin}"
MIRROR_ISSUES_REPO="${MIRROR_ISSUES_REPO:-ivanzud/MiroFish}"
COVERAGE_MAP="${COVERAGE_MAP:-docs/upstream-coverage.json}"
LOCK_WAIT_SECONDS="${LOCK_WAIT_SECONDS:-5}"

cd "${ROOT_DIR}"

run_sync() {
  local state="$1"
  local output="$2"
  local summary="$3"

  python3 "${ROOT_DIR}/scripts/sync_upstream_github.py" \
    --repo "${REPO}" \
    --state "${state}" \
    --output "${output}" \
    --summary "${summary}" \
    --fork-remote "${FORK_REMOTE}" \
    --mirror-issues-repo "${MIRROR_ISSUES_REPO}" \
    --coverage-map "${COVERAGE_MAP}" \
    --lock-wait-seconds "${LOCK_WAIT_SECONDS}"
}

run_sync open docs/upstream-open-state.json docs/upstream-open-summary.md
run_sync all docs/upstream-all-state.json docs/upstream-all-summary.md
