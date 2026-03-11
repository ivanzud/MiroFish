# Upstream Triage

Last refreshed: `2026-03-11`

## Current focus

- Keep a reusable local snapshot of `666ghj/MiroFish` open issues and pull requests.
- Land small, low-risk upstream fixes before considering larger feature branches.
- Make backend compatibility with OpenAI-compatible providers explicit in code and docs.

## Landed on this branch

- `#81` Configurable frontend API timeout: low-risk support for slow local/OpenAI-compatible backends such as Ollama.
- `#115` Use SPDX license string: safe metadata-only cherry-pick.
- `#116` Upgrade GitHub Actions: safe workflow-only dependency bump.
- `#125` Improve new-project network error diagnostics: safe single-file frontend error-message improvement.
- `#122` Remove `response_format={"type":"json_object"}` from `chat_json()`: improves compatibility with LM Studio and Ollama-style backends.
- `#124` Robust JSON payload extraction: safe parsing hardening plus regression tests.
- `#127` Handle `None` response content: safe guard against provider edge cases.

## Deferred for later review

- `#131` Zep retry mechanism: relevant to rate-limit and transient-connectivity issues, but broader behavioral change than the already-landed fixes and should be validated with targeted backend tests first.
- `#105` Security and error-handling sweep: high-value, but touches multiple API surfaces and config defaults, so it needs a dedicated pass instead of bundling into a low-risk cherry-pick cycle.
- `#129` Report-agent token overflow handling: promising, but it touches report-generation flow and should be evaluated with reproducible fixtures before merging.

## Validation status

- `cd frontend && npm run build` passes after landing `#125`.
- `cd backend && uv run pytest -q` is currently blocked in this environment because dependency resolution reaches `tiktoken`, which attempts a source build and fails without a Rust compiler.
- Follow-up is tracked in local beads issue `mirofish-ba6` to establish a lighter backend validation path.

## Practical mirror strategy for the fork

- Mirror the highest-signal upstream PR branches to the fork when they are under active review.
- Keep detailed execution tracking in local beads issues to avoid spamming the fork with every upstream item.
- Use `scripts/sync_upstream_github.py` to refresh a machine-readable snapshot and a concise markdown summary before each new evolve pass.
