# Goals

Keep MiroFish shippable while continuously triaging upstream changes and improving OpenAI-compatible backend interoperability.

## North Stars

- Safe upstream fixes land quickly without destabilizing the fork.
- OpenAI-compatible and local LLM backends work without code edits outside configuration.

## Anti Stars

- Broad merges that mix unrelated upstream changes into one risky batch.
- Backend compatibility claims that are undocumented or unsupported by tests.

## Directives

### 1. Maintain Upstream Triage

Continuously ingest the upstream issue and pull-request backlog into beads-backed work so the fork has a current, execution-ready queue.

**Steer:** increase

### 2. Prefer Safe, Incremental Upstream Adoption

Cherry-pick or supersede the smallest safe upstream fixes first, especially around configuration, parsing, and compatibility behavior.

**Steer:** increase

### 3. Keep Backend Compatibility Explicit

Support both project-specific `LLM_*` settings and standard OpenAI-compatible environment variables, then document the supported setup paths.

**Steer:** increase

## Gates

| ID | Check | Weight | Description |
|----|-------|--------|-------------|
| frontend-build | `npm run build` | 4 | Frontend production build succeeds |
| backend-pytest | `cd backend && uv run pytest -q` | 5 | Backend regression tests pass |
