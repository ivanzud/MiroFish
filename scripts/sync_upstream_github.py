#!/usr/bin/env python3
"""Fetch upstream GitHub issues and pull requests into local summaries."""

from __future__ import annotations

import argparse
import contextlib
import concurrent.futures
import errno
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BODY_EXCERPT_LIMIT = 400
COMMENT_EXCERPT_LIMIT = 240
RECENT_COMMENT_LIMIT = 3
GH_API_MAX_ATTEMPTS = 3
DEFAULT_API_TIMEOUT = int(os.environ.get("MIROFISH_GITHUB_SYNC_TIMEOUT", "30"))
REQUEST_TIMEOUT = DEFAULT_API_TIMEOUT
DEFAULT_STALE_CACHE_HOURS = int(os.environ.get("MIROFISH_GITHUB_SYNC_STALE_HOURS", "24"))
DEFAULT_MAX_WORKERS = int(os.environ.get("MIROFISH_GITHUB_SYNC_MAX_WORKERS", "8"))
DEFAULT_REPO = "666ghj/MiroFish"
GH_CLI_USABLE: bool | None = None
GH_CLI_DISABLED_REASON: str | None = None


def has_github_token() -> bool:
    return bool(os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))


def can_use_gh_cli() -> bool:
    global GH_CLI_USABLE

    if GH_CLI_DISABLED_REASON:
        return False
    if GH_CLI_USABLE is not None:
        return GH_CLI_USABLE

    if shutil.which("gh") is None:
        GH_CLI_USABLE = False
        return False

    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        GH_CLI_USABLE = False
        return False

    GH_CLI_USABLE = result.returncode == 0
    return GH_CLI_USABLE


def disable_gh_cli(reason: str) -> None:
    global GH_CLI_DISABLED_REASON, GH_CLI_USABLE
    GH_CLI_DISABLED_REASON = reason
    GH_CLI_USABLE = False


def _is_retryable_gh_error(message: str) -> bool:
    lowered = message.lower()
    markers = (
        "timeout",
        "timed out",
        "connection reset",
        "tls",
        "eof",
        "502",
        "503",
        "504",
        "secondary rate limit",
    )
    return any(marker in lowered for marker in markers)


def fetch_json_via_gh(url: str) -> object:
    parsed = urllib.parse.urlparse(url)
    endpoint = parsed.path
    if parsed.query:
        endpoint = f"{endpoint}?{parsed.query}"

    last_error: RuntimeError | None = None
    for attempt in range(1, GH_API_MAX_ATTEMPTS + 1):
        try:
            result = subprocess.run(
                ["gh", "api", endpoint],
                check=True,
                capture_output=True,
                text=True,
                timeout=REQUEST_TIMEOUT,
            )
            return json.loads(result.stdout)
        except subprocess.TimeoutExpired as exc:
            last_error = RuntimeError(
                f"gh api timed out for {endpoint} after {REQUEST_TIMEOUT}s"
            )
            if attempt >= GH_API_MAX_ATTEMPTS:
                raise last_error from exc
            time.sleep(attempt)
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or exc.stdout or "").strip() or f"exit status {exc.returncode}"
            last_error = RuntimeError(f"gh api failed for {endpoint}: {details}")
            if attempt >= GH_API_MAX_ATTEMPTS or not _is_retryable_gh_error(details):
                raise last_error from exc
            time.sleep(attempt)

    assert last_error is not None
    raise last_error


def _fetch_json_via_http(url: str) -> object:
    headers = {"User-Agent": "mirofish-upstream-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return json.load(response)
    except TimeoutError as exc:
        raise RuntimeError(
            f"GitHub API request timed out after {REQUEST_TIMEOUT}s for {url}"
        ) from exc
    except HTTPError as exc:
        if exc.code == 403 and "rate limit" in str(exc).lower():
            raise RuntimeError(
                "GitHub API rate limit exceeded. Set GITHUB_TOKEN or GH_TOKEN, or log into gh before running sync."
            ) from exc
        raise


def fetch_json(url: str) -> object:
    if not has_github_token() and can_use_gh_cli():
        try:
            return fetch_json_via_gh(url)
        except RuntimeError as exc:
            if "rate limit" in str(exc).lower():
                disable_gh_cli("GitHub CLI rate limited")
            print(
                f"warning: {exc}; falling back to direct GitHub HTTP request",
                file=sys.stderr,
            )

    return _fetch_json_via_http(url)


def github_api(path: str, params: dict[str, object]) -> object:
    url = f"https://api.github.com{path}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"
    return fetch_json(url)


def github_api_paginated(path: str, params: dict[str, object], limit: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    page = 1
    per_page = min(limit, 100)

    while len(items) < limit:
        payload = github_api(path, {**params, "per_page": per_page, "page": page})
        if not isinstance(payload, list):
            raise ValueError(f"Expected list payload from GitHub API for {path}, got {type(payload)!r}")
        if not payload:
            break

        items.extend(payload)
        if len(payload) < per_page:
            break

        page += 1

    return items[:limit]


def normalize_excerpt(text: str | None, limit: int) -> str:
    if not text:
        return ""

    collapsed = re.sub(r"\s+", " ", text).strip()
    if len(collapsed) <= limit:
        return collapsed

    return collapsed[: max(0, limit - 1)].rstrip() + "…"


def fetch_recent_comments(comments_url: str | None, limit: int = RECENT_COMMENT_LIMIT) -> list[dict[str, Any]]:
    if not comments_url or limit <= 0:
        return []

    payload = fetch_json(
        f"{comments_url}?{urllib.parse.urlencode({'per_page': limit, 'sort': 'updated', 'direction': 'desc'})}"
    )
    if not isinstance(payload, list):
        raise ValueError(f"Expected list payload when fetching comments from {comments_url}, got {type(payload)!r}")

    comments: list[dict[str, Any]] = []
    for item in payload[:limit]:
        comments.append(
            {
                "author": item.get("user", {}).get("login"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "url": item.get("html_url"),
                "body_excerpt": normalize_excerpt(item.get("body"), COMMENT_EXCERPT_LIMIT),
            }
        )
    return comments


def hydrate_pull_requests(
    owner: str,
    name: str,
    pull_requests: list[dict[str, Any]],
    max_workers: int,
) -> list[dict[str, Any]]:
    def hydrate_one(pull_request: dict[str, Any]) -> dict[str, Any]:
        number = pull_request.get("number")
        if number is None:
            raise ValueError("Pull request payload missing number")
        details = github_api(f"/repos/{owner}/{name}/pulls/{number}", {})
        if not isinstance(details, dict):
            raise ValueError(f"Expected pull request details dict for #{number}, got {type(details)!r}")
        return details

    return parallel_ordered_map(
        pull_requests,
        hydrate_one,
        max_workers=max_workers,
    )


def parallel_ordered_map(
    items: list[Any],
    func,
    *,
    max_workers: int,
) -> list[Any]:
    if not items:
        return []

    resolved_max_workers = max(1, min(max_workers, len(items)))
    if resolved_max_workers == 1:
        return [func(item) for item in items]

    results: list[Any] = [None] * len(items)
    with concurrent.futures.ThreadPoolExecutor(max_workers=resolved_max_workers) as executor:
        future_to_index = {
            executor.submit(func, item): index for index, item in enumerate(items)
        }
        try:
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                results[index] = future.result()
        except Exception:
            for future in future_to_index:
                future.cancel()
            raise
    return results


def list_mirrored_pull_request_numbers(remote: str) -> set[int]:
    try:
        result = subprocess.run(
            [
                "git",
                "for-each-ref",
                "--format=%(refname:short)",
                f"refs/remotes/{remote}/mirror/upstream-pr-*",
                "refs/heads/mirror/upstream-pr-*",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"Unable to inspect mirrored pull request refs for remote {remote!r}") from exc

    mirrored: set[int] = set()
    for line in result.stdout.splitlines():
        match = re.search(r"mirror/upstream-pr-(\d+)$", line.strip())
        if match:
            mirrored.add(int(match.group(1)))
    return mirrored


def load_local_coverage_entries(path: Path | None, key: str) -> dict[int, dict[str, object]]:
    if path is None or not path.exists():
        return {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    entries = payload.get(key, []) if isinstance(payload, dict) else []
    if not isinstance(entries, list):
        return {}

    coverage_map: dict[int, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        number = entry.get("number")
        if isinstance(number, int):
            coverage_map[number] = entry
    return coverage_map


def load_local_issue_coverage(path: Path | None) -> dict[int, dict[str, object]]:
    return load_local_coverage_entries(path, "issues")


def load_local_pr_coverage(path: Path | None) -> dict[int, dict[str, object]]:
    return load_local_coverage_entries(path, "pull_requests")


def compact_issue(
    issue: dict[str, object],
    coverage_map: dict[int, dict[str, object]] | None = None,
) -> dict[str, object]:
    comment_count = int(issue.get("comments") or 0)
    compacted = {
        "number": issue["number"],
        "title": issue["title"],
        "url": issue["html_url"],
        "state": issue["state"],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
        "closed_at": issue.get("closed_at"),
        "labels": [label["name"] for label in issue.get("labels", [])],
        "author": issue.get("user", {}).get("login"),
        "body_excerpt": normalize_excerpt(issue.get("body"), BODY_EXCERPT_LIMIT),
        "comment_count": comment_count,
        "recent_comments": fetch_recent_comments(issue.get("comments_url")) if comment_count else [],
    }
    local_coverage = (coverage_map or {}).get(int(issue["number"]))
    if local_coverage:
        compacted["local_coverage"] = local_coverage
    return compacted


def compact_issues(
    issue_items: list[dict[str, object]],
    max_workers: int,
    coverage_map: dict[int, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    return parallel_ordered_map(
        issue_items,
        lambda item: compact_issue(item, coverage_map),
        max_workers=max_workers,
    )


def compact_pr(
    pr: dict[str, object],
    mirrored_pr_numbers: set[int] | None = None,
    fork_remote: str | None = None,
    coverage_map: dict[int, dict[str, object]] | None = None,
) -> dict[str, object]:
    number = int(pr["number"])
    head = pr.get("head") or {}
    base = pr.get("base") or {}
    head_repo = head.get("repo") or {}
    base_repo = base.get("repo") or {}
    fork_mirrored = False
    fork_mirror_ref = None
    if mirrored_pr_numbers is not None and fork_remote is not None:
        fork_mirrored = number in mirrored_pr_numbers
        fork_mirror_ref = f"{fork_remote}/mirror/upstream-pr-{number}"
    comment_count = int(pr.get("comments") or 0)
    review_comment_count = int(pr.get("review_comments") or 0)

    compacted = {
        "number": number,
        "title": pr["title"],
        "url": pr["html_url"],
        "state": pr["state"],
        "created_at": pr["created_at"],
        "updated_at": pr["updated_at"],
        "closed_at": pr.get("closed_at"),
        "merged_at": pr.get("merged_at"),
        "head": head.get("ref"),
        "head_sha": head.get("sha"),
        "head_repo": head_repo.get("full_name"),
        "head_clone_url": head_repo.get("clone_url"),
        "base": base.get("ref"),
        "base_repo": base_repo.get("full_name"),
        "draft": pr.get("draft", False),
        "mergeable_state": pr.get("mergeable_state"),
        "labels": [label["name"] for label in pr.get("labels", [])],
        "author": pr.get("user", {}).get("login"),
        "body_excerpt": normalize_excerpt(pr.get("body"), BODY_EXCERPT_LIMIT),
        "comment_count": comment_count,
        "review_comment_count": review_comment_count,
        "recent_comments": fetch_recent_comments(pr.get("comments_url")) if comment_count else [],
        "fork_mirrored": fork_mirrored,
        "fork_mirror_ref": fork_mirror_ref,
    }
    local_coverage = (coverage_map or {}).get(number)
    if local_coverage:
        compacted["local_coverage"] = local_coverage
    return compacted


def compact_pull_requests(
    pr_items: list[dict[str, object]],
    mirrored_pr_numbers: set[int] | None,
    fork_remote: str | None,
    max_workers: int,
    coverage_map: dict[int, dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    return parallel_ordered_map(
        pr_items,
        lambda item: compact_pr(item, mirrored_pr_numbers, fork_remote, coverage_map),
        max_workers=max_workers,
    )


def summarize_counts(items: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        state = str(item.get("state", "unknown"))
        counts[state] = counts.get(state, 0) + 1
    return counts


def write_summary(
    path: Path,
    repo: str,
    state: str,
    issues: list[dict[str, object]],
    prs: list[dict[str, object]],
    fork_remote: str | None = None,
    captured_at: str | None = None,
    coverage_map_path: str | None = None,
) -> None:
    issue_counts = summarize_counts(issues)
    pr_counts = summarize_counts(prs)
    mirrored_count = sum(1 for pr in prs if pr.get("fork_mirrored"))
    lines = [
        "# Upstream Triage Snapshot",
        "",
        f"- Repository: `{repo}`",
        f"- State filter: `{state}`",
        f"- Captured: `{captured_at or datetime.now(timezone.utc).isoformat()}`",
        f"- Issues: `{len(issues)}` total (`open={issue_counts.get('open', 0)}`, `closed={issue_counts.get('closed', 0)}`)",
        f"- Pull requests: `{len(prs)}` total (`open={pr_counts.get('open', 0)}`, `closed={pr_counts.get('closed', 0)}`)",
    ]
    if fork_remote:
        lines.append(f"- Mirrored in `{fork_remote}`: `{mirrored_count}` of `{len(prs)}` PR refs")
    if coverage_map_path:
        lines.append(f"- Local issue coverage map: `{coverage_map_path}`")
    lines.extend(["", "## Recently Updated Issues", ""])

    for issue in issues[:10]:
        labels = ", ".join(issue["labels"]) if issue["labels"] else "no labels"
        lines.append(f"- #{issue['number']} [{issue['state']}] {issue['title']} ({labels})")
        local_coverage = issue.get("local_coverage") or {}
        if local_coverage:
            status = local_coverage.get("status") or "covered"
            summary = local_coverage.get("summary") or "covered locally on this branch"
            lines.append(f"  - local coverage [{status}]: {summary}")
        if issue.get("body_excerpt"):
            lines.append(f"  - {issue['body_excerpt']}")
        if issue.get("recent_comments"):
            latest_comment = issue["recent_comments"][0]
            author = latest_comment.get("author") or "unknown"
            excerpt = latest_comment.get("body_excerpt") or "(no comment body)"
            lines.append(f"  - latest comment by `{author}`: {excerpt}")

    lines.extend(["", "## Recently Updated Pull Requests", ""])
    for pr in prs[:10]:
        suffix = " merged" if pr.get("merged_at") else ""
        mergeable_state = pr.get("mergeable_state") or "unknown"
        mirror_suffix = ""
        if fork_remote:
            mirror_suffix = ", mirrored=yes" if pr.get("fork_mirrored") else ", mirrored=no"
        lines.append(
            f"- #{pr['number']} [{pr['state']}{suffix}, mergeable={mergeable_state}{mirror_suffix}] "
            f"{pr['title']} (`{pr['head']}` -> `{pr['base']}`)"
        )
        local_coverage = pr.get("local_coverage") or {}
        if local_coverage:
            status = local_coverage.get("status") or "covered"
            summary = local_coverage.get("summary") or "covered locally on this branch"
            lines.append(f"  - local coverage [{status}]: {summary}")
        if pr.get("body_excerpt"):
            lines.append(f"  - {pr['body_excerpt']}")
        if pr.get("recent_comments"):
            latest_comment = pr["recent_comments"][0]
            author = latest_comment.get("author") or "unknown"
            excerpt = latest_comment.get("body_excerpt") or "(no comment body)"
            lines.append(f"  - latest comment by `{author}`: {excerpt}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def attach_local_coverage(
    items: list[dict[str, Any]],
    coverage_map: dict[int, dict[str, object]] | None,
) -> list[dict[str, Any]]:
    attached: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        number = item.get("number")
        if not isinstance(number, int):
            attached.append(item)
            continue
        enriched = dict(item)
        local_coverage = (coverage_map or {}).get(number)
        if local_coverage:
            enriched["local_coverage"] = local_coverage
        attached.append(enriched)
    return attached


def load_cached_snapshot(path: Path, repo: str, state: str) -> dict[str, Any] | None:
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    if not isinstance(payload, dict):
        return None
    if payload.get("repo") != repo or payload.get("state") != state:
        return None

    return payload


def snapshot_is_fresh(payload: dict[str, Any], stale_after_hours: int) -> bool:
    captured_at = payload.get("captured_at") or payload.get("generated_at")
    if not captured_at or stale_after_hours < 0:
        return False

    try:
        captured = datetime.fromisoformat(str(captured_at).replace("Z", "+00:00"))
    except ValueError:
        return False

    age_seconds = (datetime.now(timezone.utc) - captured.astimezone(timezone.utc)).total_seconds()
    return age_seconds <= stale_after_hours * 3600


def try_reuse_cached_snapshot(
    cached_payload: dict[str, Any] | None,
    *,
    repo: str,
    state: str,
    output_path: Path,
    summary_path: Path,
    exc: RuntimeError,
    stale_cache_hours: int,
    issue_coverage_map: dict[int, dict[str, object]] | None = None,
    pr_coverage_map: dict[int, dict[str, object]] | None = None,
    coverage_map_path: str | None = None,
) -> bool:
    rate_limited = "rate limit" in str(exc).lower()
    if not rate_limited or not cached_payload or not snapshot_is_fresh(cached_payload, stale_cache_hours):
        return False

    issues = cached_payload.get("issues") or []
    prs = cached_payload.get("pull_requests") or []
    captured_at = cached_payload.get("captured_at") or cached_payload.get("generated_at")
    if not isinstance(issues, list) or not isinstance(prs, list):
        return False
    issues = attach_local_coverage(issues, issue_coverage_map)
    prs = attach_local_coverage(prs, pr_coverage_map)
    refreshed_payload = dict(cached_payload)
    refreshed_payload["issues"] = issues
    refreshed_payload["pull_requests"] = prs
    refreshed_payload["coverage_map_path"] = coverage_map_path
    output_path.write_text(json.dumps(refreshed_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_summary(
        summary_path,
        repo,
        state,
        issues,
        prs,
        cached_payload.get("fork_remote"),
        captured_at=captured_at,
        coverage_map_path=coverage_map_path or cached_payload.get("coverage_map_path"),
    )
    print(
        f"warning: {exc}; reusing fresh cached snapshot from "
        f"{cached_payload.get('_cache_path', 'cache')} (captured_at={captured_at})",
        file=sys.stderr,
    )
    print(
        f"Reused cached snapshot with {len(issues)} issues and {len(prs)} pull requests "
        f"from {repo} into {os.path.relpath(cached_payload.get('_cache_path', summary_path))}"
    )
    return True


def lock_path_for(output_path: Path, repo: str) -> Path:
    repo_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", repo)
    repo_root = output_path.resolve().parents[1]
    return repo_root / ".agents" / "upstream-sync-locks" / f"{repo_slug}.lock"


@contextlib.contextmanager
def repo_lock(output_path: Path, repo: str):
    lock_path = lock_path_for(output_path, repo)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w", encoding="utf-8") as lock_file:
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                raise RuntimeError(
                    f"Another sync_upstream_github.py run is already refreshing {repo}. "
                    "Wait for it to finish and rerun sequentially."
                ) from exc
            raise
        lock_file.write(str(os.getpid()))
        lock_file.flush()
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "repo_arg",
        nargs="?",
        help="Legacy positional owner/repo alias retained for backward compatibility",
    )
    parser.add_argument(
        "--repo",
        default=argparse.SUPPRESS,
        help="owner/repo to inspect",
    )
    parser.add_argument("--state", default="open", help="GitHub state filter (open, closed, or all)")
    parser.add_argument("--limit", type=int, default=500, help="Maximum items to fetch per collection")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_API_TIMEOUT,
        help="Timeout in seconds for each gh/http request",
    )
    parser.add_argument(
        "--output",
        "--json-out",
        dest="output",
        required=True,
        help="Path to write machine-readable JSON",
    )
    parser.add_argument(
        "--summary",
        "--md-out",
        dest="summary",
        required=True,
        help="Path to write markdown summary",
    )
    parser.add_argument(
        "--fork-remote",
        default=None,
        help="Optional git remote name used to annotate whether upstream PR refs are mirrored into the fork",
    )
    parser.add_argument(
        "--stale-cache-hours",
        type=int,
        default=DEFAULT_STALE_CACHE_HOURS,
        help=(
            "If refresh hits a GitHub rate limit, reuse an existing snapshot captured within this many hours "
            "instead of failing. Set to -1 to disable stale cache fallback."
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=DEFAULT_MAX_WORKERS,
        help=(
            "Maximum concurrent GitHub hydration workers for per-item PR detail/comment fetches. "
            "Lower this if GitHub starts rate limiting aggressively."
        ),
    )
    parser.add_argument(
        "--coverage-map",
        default="docs/upstream-coverage.json",
        help=(
            "Optional machine-readable JSON file describing upstream issues already covered locally. "
            "Defaults to docs/upstream-coverage.json when present."
        ),
    )
    return parser


def resolve_repo_argument(args: argparse.Namespace, parser: argparse.ArgumentParser) -> str:
    positional_repo = getattr(args, "repo_arg", None)
    default_repo = DEFAULT_REPO
    explicit_repo = getattr(args, "repo", None)
    option_repo = explicit_repo or default_repo

    if positional_repo:
        if explicit_repo is not None and positional_repo != option_repo:
            parser.error(
                f"conflicting repo values: positional {positional_repo!r} does not match --repo {option_repo!r}"
            )
        return positional_repo

    return option_repo


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.repo = resolve_repo_argument(args, parser)
    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = max(1, args.timeout)
    max_workers = max(1, args.max_workers)

    output_path = Path(args.output)
    summary_path = Path(args.summary)
    coverage_map_path = Path(args.coverage_map) if args.coverage_map else None
    issue_coverage_map = load_local_issue_coverage(coverage_map_path)
    pr_coverage_map = load_local_pr_coverage(coverage_map_path)
    cached_payload = load_cached_snapshot(output_path, args.repo, args.state)
    if cached_payload is not None:
        cached_payload["_cache_path"] = str(output_path)
    owner, name = args.repo.split("/", 1)

    with repo_lock(output_path, args.repo):
        try:
            issue_items = github_api_paginated(
                f"/repos/{owner}/{name}/issues",
                {"state": args.state, "sort": "updated", "direction": "desc"},
                args.limit,
            )
            pr_items = github_api_paginated(
                f"/repos/{owner}/{name}/pulls",
                {"state": args.state, "sort": "updated", "direction": "desc"},
                args.limit,
            )
        except RuntimeError as exc:
            if try_reuse_cached_snapshot(
                cached_payload,
                repo=args.repo,
                state=args.state,
                output_path=output_path,
                summary_path=summary_path,
                exc=exc,
                stale_cache_hours=args.stale_cache_hours,
                issue_coverage_map=issue_coverage_map,
                pr_coverage_map=pr_coverage_map,
                coverage_map_path=str(coverage_map_path) if coverage_map_path and coverage_map_path.exists() else None,
            ):
                return 0
            raise

        try:
            issues = compact_issues(
                [item for item in issue_items if "pull_request" not in item],
                max_workers=max_workers,
                coverage_map=issue_coverage_map,
            )
            pr_details = hydrate_pull_requests(owner, name, pr_items, max_workers=max_workers)
            mirrored_pr_numbers = (
                list_mirrored_pull_request_numbers(args.fork_remote) if args.fork_remote else None
            )
            prs = compact_pull_requests(
                pr_details,
                mirrored_pr_numbers,
                args.fork_remote,
                max_workers=max_workers,
                coverage_map=pr_coverage_map,
            )
        except RuntimeError as exc:
            if try_reuse_cached_snapshot(
                cached_payload,
                repo=args.repo,
                state=args.state,
                output_path=output_path,
                summary_path=summary_path,
                exc=exc,
                stale_cache_hours=args.stale_cache_hours,
                issue_coverage_map=issue_coverage_map,
                pr_coverage_map=pr_coverage_map,
                coverage_map_path=str(coverage_map_path) if coverage_map_path and coverage_map_path.exists() else None,
            ):
                return 0
            raise
        captured_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "repo": args.repo,
            "state": args.state,
            "captured_at": captured_at,
            "generated_at": captured_at,
            "coverage_map_path": str(coverage_map_path) if coverage_map_path and coverage_map_path.exists() else None,
            "counts": {
                "issues": summarize_counts(issues),
                "pull_requests": summarize_counts(prs),
            },
            "issues": issues,
            "pull_requests": prs,
        }
        if args.fork_remote:
            mirrored_total = sum(1 for pr in prs if pr["fork_mirrored"])
            payload["fork_remote"] = args.fork_remote
            payload["counts"]["mirrored_pull_requests"] = {
                "mirrored": mirrored_total,
                "not_mirrored": len(prs) - mirrored_total,
            }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_summary(
            summary_path,
            args.repo,
            args.state,
            issues,
            prs,
            args.fork_remote,
            captured_at=captured_at,
            coverage_map_path=str(coverage_map_path) if coverage_map_path and coverage_map_path.exists() else None,
        )

    print(
        f"Captured {len(issues)} issues and {len(prs)} pull requests from {args.repo} "
        f"into {os.path.relpath(output_path)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
