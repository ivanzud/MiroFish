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
- `#103` Upgrade Docker image workflow for ARM64 builds: safe workflow-only cherry-pick adding `linux/arm64` image output and GitHub Actions cache configuration.
- `#125` Improve new-project network error diagnostics: safe single-file frontend error-message improvement.
- `#122` Remove `response_format={"type":"json_object"}` from `chat_json()`: improves compatibility with LM Studio and Ollama-style backends.
- `#124` Robust JSON payload extraction: safe parsing hardening plus regression tests.
- `#127` Handle `None` response content: safe guard against provider edge cases.
- `#129` Safe subset landed locally: configurable `LLM_MAX_TOKENS`, automatic retry after context-length failures, and report-agent message pruning to reduce overflow crashes.
- `#131` Safe subset landed locally: Zep graph creation, ontology setup, and batch uploads now retry only transient failures (429/timeout/5xx-style cases) with bounded backoff, plus targeted regression tests.
- `#130` Add `CONTRIBUTING.md`: safe docs-only cherry-pick.
- `#132` Add README architecture overview: safe docs-only cherry-pick.
- `#112` Add Korean README: safe docs-only cherry-pick; normalized cross-links with the other language READMEs while landing it locally.
- `#113` Add Japanese README: safe docs-only cherry-pick; normalized cross-links with the other language READMEs while landing it locally.
- `#73` Sanitize malformed ontology entity/edge items before fallback injection: prevents `_validate_and_process()` crashes on mixed-quality LLM JSON output.
- `#74` Replace bare `except:` clauses with `except Exception:` in JSON repair and simulation history formatting paths.
- `#15` Handle failed simulation status in `Step3Simulation`: stop polling and surface an error instead of leaving the UI stuck in a running state.
- `#84` Failed report generation can now be retried directly from `Step4Report`: the view polls the persisted report status, surfaces backend error text when generation fails, and offers a `force_regenerate` retry path instead of leaving the user stranded on a dead report page.
- `#105` Safe subset landed locally: API JSON error responses now use a shared helper that hides traceback details unless `DEBUG` is enabled, while still logging full tracebacks server-side; file-parser encoding fallbacks now emit debug logs instead of silently swallowing detector failures.
- `#126` Safe subset landed locally: backend config now exposes structured validation helpers and a non-sensitive config summary, while malformed numeric env vars no longer crash module import before validation can report them.
- OpenAI-compatible backend aliases now work in the standalone simulation runners too, so `OPENAI_API_KEY` / `OPENAI_BASE_URL` / `OPENAI_MODEL` can be used directly outside the Flask app path.
- Objective 7 verification status: backend config, standalone runners, and both READMEs now explicitly support direct OpenAI / Codex-compatible / OpenAI-compatible backends without requiring a project-specific raw-key-only setup.
- Backend config now also accepts `OPENAI_API_BASE_URL`, matching the environment variable exported by the standalone simulation runners and some OpenAI-compatible tooling, with regression coverage in the lightweight backend test path.
- `#114` Fix API base URL fallback is already superseded locally by the current frontend API client, which now falls back to the runtime origin and also supports `VITE_API_TIMEOUT`.

## Deferred for later review

- `#105` Remaining risky subset: default `DEBUG=False`, non-static `SECRET_KEY` generation, and stricter CORS defaults/configuration are still deferred because they can change local/dev or deployed behavior and need a compatibility review before landing.
- `#82` Dependency-only CVE patch is deferred for coordinated review because the open PR only edits `backend/requirements.txt`, while this repo also depends on `backend/pyproject.toml` and `backend/uv.lock`; landing it blindly would leave dependency state inconsistent.
- `#87` and `#86` GitHub Actions-only PRs are superseded locally by the current Docker workflow: their diffs would either partially duplicate already-landed upgrades or regress this branch by removing the ARM64/cache changes that came from `#103`.
- `#100` Relative frontend API base URL fallback is superseded locally by the current API client, which already falls back to the runtime origin and respects `VITE_API_BASE_URL`.
- `#72` Markdown-fence cleanup for JSON responses is superseded locally by the broader `_extract_json_payload()` handling in `backend/app/utils/llm_client.py`.
## Validation status

- `python3 -m unittest tests/test_sync_upstream_github.py` passes for the GitHub sync script pagination/state summary logic.
- `cd frontend && npm run build` passes after landing `#104` and the prior OpenAI-alias compatibility updates.
- `cd frontend && npm run build` passes after landing `#15`.
- `cd frontend && npm run build` passes after adding failed-report retry handling in `Step4Report` for upstream issue `#84`.
- `npm run test:backend:lite` now provides a repo-native lightweight backend validation path when full `uv` resolution is blocked by Rust/CUDA-heavy dependencies.
- `npm run test:backend:lite` passes with the `OPENAI_API_BASE_URL` regression test plus the new structured config-validation coverage included in the default lightweight backend suite.
- `./.tmp-test-venv/bin/pytest backend/tests/test_error_handler.py backend/tests/test_llm_client.py backend/tests/test_graph_builder.py backend/tests/test_ontology_generator.py -q` passes after landing the safe subset of `#105`.
- `./.tmp-test-venv/bin/pytest backend/tests/test_llm_client.py backend/tests/test_graph_builder.py -q` passes with targeted regression coverage for context-length handling and transient Zep retry behavior.
- `./.tmp-test-venv/bin/pytest backend/tests/test_ontology_generator.py backend/tests/test_llm_client.py backend/tests/test_graph_builder.py -q` passes after landing the ontology validation hardening and exception-scope cleanup.
- `python3 -m unittest tests/test_sync_upstream_github.py` and refreshed snapshots now show `32` open upstream issues, `34` open upstream PRs, and `13` closed upstream PRs in the full-history capture.
- `cd backend && uv run pytest -q` is currently blocked in this environment because dependency resolution reaches `tiktoken`, which attempts a source build and fails without a Rust compiler.

## Snapshot artifacts

- `docs/upstream-open-state.json` and `docs/upstream-open-summary.md` remain the fast open-work triage view.
- `docs/upstream-all-state.json` and `docs/upstream-all-summary.md` now capture the full upstream issue/PR state for historical triage and mirroring decisions.
- `scripts/sync_upstream_github.py` now supports paginated `--state all` refreshes and uses `GITHUB_TOKEN` / `GH_TOKEN` when available to avoid GitHub API rate-limit failures.

## Practical mirror strategy for the fork

- Mirror the highest-signal upstream PR branches to the fork when they are under active review.
- Keep detailed execution tracking in local beads issues to avoid spamming the fork with every upstream item.
- Use `scripts/sync_upstream_github.py` to refresh a machine-readable snapshot and a concise markdown summary before each new evolve pass.
