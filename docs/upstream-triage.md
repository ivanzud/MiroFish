# Upstream Triage

Last refreshed: `2026-03-11`

## Current focus

- Keep a reusable local snapshot of `666ghj/MiroFish` open issues and pull requests.
- Land small, low-risk upstream fixes before considering larger feature branches.
- Make backend compatibility with OpenAI-compatible providers explicit in code and docs.

## Safe PR candidates reviewed

- `#115` Use SPDX license string: safe metadata-only cherry-pick.
- `#122` Remove `response_format={"type":"json_object"}` from `chat_json()`: improves compatibility with LM Studio and Ollama-style backends.
- `#124` Robust JSON payload extraction: safe parsing hardening plus regression tests.
- `#127` Handle `None` response content: safe guard against provider edge cases.

## Practical mirror strategy for the fork

- Mirror the highest-signal upstream PR branches to the fork when they are under active review.
- Keep detailed execution tracking in local beads issues to avoid spamming the fork with every upstream item.
- Use `scripts/sync_upstream_github.py` to refresh a machine-readable snapshot and a concise markdown summary before each new evolve pass.
