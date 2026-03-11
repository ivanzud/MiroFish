#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.tmp-test-venv"

if [ ! -d "${VENV_DIR}" ]; then
  python3 -m venv "${VENV_DIR}"
fi

# Keep the lightweight path limited to the dependencies needed by the fast unit tests.
"${VENV_DIR}/bin/pip" install -q \
  "flask>=3.0.0" \
  "flask-cors>=5.0.0" \
  "pytest>=8.0.0" \
  "openai>=1.0.0" \
  "python-dotenv>=1.0.0"

"${VENV_DIR}/bin/pytest" \
  "${ROOT_DIR}/backend/tests/test_app_routes.py" \
  "${ROOT_DIR}/backend/tests/test_config.py" \
  "${ROOT_DIR}/backend/tests/test_i18n.py" \
  "${ROOT_DIR}/backend/tests/test_llm_env.py" \
  "${ROOT_DIR}/backend/tests/test_llm_client.py" \
  "${ROOT_DIR}/backend/tests/test_graph_builder.py" \
  "${ROOT_DIR}/backend/tests/test_report_agent.py" \
  "${ROOT_DIR}/backend/tests/test_simulation_runner_actions.py" \
  "${ROOT_DIR}/backend/tests/test_openai_compat_services.py" \
  -q
