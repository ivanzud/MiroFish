#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK_DIR="${ROOT_DIR}/.githooks"

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  cat <<'EOF'
Usage: bash ./scripts/install_git_hooks.sh

Configures git core.hooksPath to use the repo-local .githooks directory.
This is opt-in and can be reverted with:
  git config --unset core.hooksPath
EOF
  exit 0
fi

if ! git -C "$ROOT_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  echo "This installer must be run inside a git repository." >&2
  exit 1
fi

chmod +x "${HOOK_DIR}/pre-commit" "${HOOK_DIR}/pre-push"
git -C "$ROOT_DIR" config core.hooksPath .githooks

echo "Installed repo-local git hooks from .githooks"
echo "pre-commit: backend lite tests + frontend tests"
echo "pre-push: full validation (backend lite tests + frontend tests + frontend build)"
