#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="666ghj/MiroFish"
FORK_REMOTE="${FORK_REMOTE:-origin}"
MIRROR_ISSUES_REPO="${MIRROR_ISSUES_REPO:-ivanzud/MiroFish}"
COVERAGE_MAP="${COVERAGE_MAP:-docs/upstream-coverage.json}"
LOCK_WAIT_SECONDS="${LOCK_WAIT_SECONDS:-5}"
EXTRA_ARGS=()

usage() {
  cat <<'EOF'
Usage: refresh_upstream_snapshots.sh [owner/repo] [options]

Refresh both the open-only and full upstream GitHub snapshots using repo defaults.

Options:
  --repo <owner/repo>            Override the upstream repository to inspect.
  --timeout <seconds>            Per-request timeout passed to sync_upstream_github.py.
  --max-workers <count>          Limit concurrent hydration workers.
  --stale-cache-hours <hours>    Allow reuse of recent snapshots on GitHub rate limits.
  --lock-wait-seconds <seconds>  Wait this long for the upstream-sync lock.
  --force-refresh, --no-cache    Disable stale-cache fallback for this run.
  --help                         Show this message.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --repo)
      if [[ $# -lt 2 ]]; then
        echo "error: --repo requires an owner/repo value" >&2
        exit 1
      fi
      REPO="$2"
      shift 2
      ;;
    --repo=*)
      REPO="${1#*=}"
      shift
      ;;
    --force-refresh|--no-cache)
      EXTRA_ARGS+=(--stale-cache-hours -1)
      shift
      ;;
    --timeout|--max-workers|--stale-cache-hours|--lock-wait-seconds)
      if [[ $# -lt 2 ]]; then
        echo "error: $1 requires a value" >&2
        exit 1
      fi
      EXTRA_ARGS+=("$1" "$2")
      shift 2
      ;;
    --timeout=*|--max-workers=*|--stale-cache-hours=*|--lock-wait-seconds=*)
      EXTRA_ARGS+=("$1")
      shift
      ;;
    -*)
      echo "error: unsupported option '$1'" >&2
      usage >&2
      exit 1
      ;;
    *)
      REPO="$1"
      shift
      ;;
  esac
done

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
    --lock-wait-seconds "${LOCK_WAIT_SECONDS}" \
    "${EXTRA_ARGS[@]}"
}

run_sync open docs/upstream-open-state.json docs/upstream-open-summary.md
run_sync all docs/upstream-all-state.json docs/upstream-all-summary.md
