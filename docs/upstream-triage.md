# Upstream Triage

Last refreshed: `2026-03-11`

## Current focus

- Keep reusable local snapshots of `666ghj/MiroFish` open and full issue/PR state.
- Land small, low-risk upstream fixes before considering larger feature branches.
- Keep OpenAI-compatible backend support verified in both code paths and docs while reviewing the remaining open PR queue.

## Landed on this branch

- `#81` Configurable frontend API timeout: low-risk support for slow local/OpenAI-compatible backends such as Ollama.
- `#104` Make Vite dev proxy target configurable with `VITE_API_BASE_URL`: removes another hardcoded localhost assumption for custom backend hosts and ports.
- `#115` Use SPDX license string: safe metadata-only cherry-pick.
- `#116` Upgrade GitHub Actions: safe workflow-only dependency bump.
- `#125` Improve new-project network error diagnostics: safe single-file frontend error-message improvement.
- `#122` Remove `response_format={"type":"json_object"}` from `chat_json()`: improves compatibility with LM Studio and Ollama-style backends.
- `#124` Robust JSON payload extraction: safe parsing hardening plus regression tests.
- `#127` Handle `None` response content: safe guard against provider edge cases.
- `#129` Safe subset landed locally: configurable `LLM_MAX_TOKENS`, automatic retry after context-length failures, and report-agent message pruning to reduce overflow crashes.
- `#131` Safe subset landed locally: Zep graph creation, ontology setup, and batch uploads now retry only transient failures (429/timeout/5xx-style cases) with bounded backoff, plus targeted regression tests.
- `#130` Add `CONTRIBUTING.md`: safe docs-only cherry-pick.
- `#132` Add README architecture overview: safe docs-only cherry-pick.
- `#73` Sanitize malformed ontology entity/edge items before fallback injection: prevents `_validate_and_process()` crashes on mixed-quality LLM JSON output.
- `#74` Replace bare `except:` clauses with `except Exception:` in JSON repair and simulation history formatting paths.
- OpenAI-compatible backend aliases now work in the standalone simulation runners too, so `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` can be used directly outside the Flask app path.
- Objective 7 verification status: backend config, standalone runners, and both READMEs now explicitly support direct OpenAI / Codex-compatible / OpenAI-compatible backends without requiring a project-specific raw-key-only setup.

## Deferred for later review

- `#105` Security and error-handling sweep: high-value, but touches multiple API surfaces and config defaults, so it needs a dedicated pass instead of bundling into a low-risk cherry-pick cycle.
## Validation status

- `python3 -m unittest tests/test_sync_upstream_github.py` passes for the GitHub sync script pagination/state summary logic.
- `cd frontend && npm run build` passes after landing `#104` and the prior OpenAI-alias compatibility updates.
- `npm run test:backend:lite` now provides a repo-native lightweight backend validation path when full `uv` resolution is blocked by Rust/CUDA-heavy dependencies.
- `./.tmp-test-venv/bin/pytest backend/tests/test_llm_client.py backend/tests/test_graph_builder.py -q` passes with targeted regression coverage for context-length handling and transient Zep retry behavior.
- `./.tmp-test-venv/bin/pytest backend/tests/test_ontology_generator.py backend/tests/test_llm_client.py backend/tests/test_graph_builder.py -q` passes after landing the ontology validation hardening and exception-scope cleanup.
- `cd backend && uv run pytest -q` is currently blocked in this environment because dependency resolution reaches `tiktoken`, which attempts a source build and fails without a Rust compiler.

## Snapshot artifacts

- `docs/upstream-open-state.json` and `docs/upstream-open-summary.md` remain the fast open-work triage view.
- `docs/upstream-all-state.json` and `docs/upstream-all-summary.md` now capture the full upstream issue/PR state for historical triage and mirroring decisions.
- `scripts/sync_upstream_github.py` now supports paginated `--state all` refreshes and uses `GITHUB_TOKEN` / `GH_TOKEN` when available to avoid GitHub API rate-limit failures.

## Practical mirror strategy for the fork

- Mirror the highest-signal upstream PR branches to the fork when they are under active review.
- Keep detailed execution tracking in local beads issues to avoid spamming the fork with every upstream item.
- Use `scripts/sync_upstream_github.py` to refresh a machine-readable snapshot and a concise markdown summary before each new evolve pass.
