#!/usr/bin/env python3
"""Fetch upstream GitHub issues and pull requests into local summaries."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def fetch_json(url: str) -> object:
    headers = {"User-Agent": "mirofish-upstream-sync"}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except HTTPError as exc:
        if exc.code == 403 and "rate limit" in str(exc).lower():
            raise RuntimeError(
                "GitHub API rate limit exceeded. Set GITHUB_TOKEN or GH_TOKEN before running sync."
            ) from exc
        raise


def github_api(path: str, params: dict[str, object]) -> object:
    query = urllib.parse.urlencode(params)
    return fetch_json(f"https://api.github.com{path}?{query}")


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


def compact_issue(issue: dict[str, object]) -> dict[str, object]:
    return {
        "number": issue["number"],
        "title": issue["title"],
        "url": issue["html_url"],
        "state": issue["state"],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
        "closed_at": issue.get("closed_at"),
        "labels": [label["name"] for label in issue.get("labels", [])],
        "author": issue.get("user", {}).get("login"),
    }


def compact_pr(pr: dict[str, object]) -> dict[str, object]:
    return {
        "number": pr["number"],
        "title": pr["title"],
        "url": pr["html_url"],
        "state": pr["state"],
        "created_at": pr["created_at"],
        "updated_at": pr["updated_at"],
        "closed_at": pr.get("closed_at"),
        "merged_at": pr.get("merged_at"),
        "head": pr.get("head", {}).get("ref"),
        "base": pr.get("base", {}).get("ref"),
        "draft": pr.get("draft", False),
        "author": pr.get("user", {}).get("login"),
    }


def summarize_counts(items: list[dict[str, object]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        state = str(item.get("state", "unknown"))
        counts[state] = counts.get(state, 0) + 1
    return counts


def write_summary(path: Path, repo: str, state: str, issues: list[dict[str, object]], prs: list[dict[str, object]]) -> None:
    issue_counts = summarize_counts(issues)
    pr_counts = summarize_counts(prs)
    lines = [
        "# Upstream Triage Snapshot",
        "",
        f"- Repository: `{repo}`",
        f"- State filter: `{state}`",
        f"- Captured: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Issues: `{len(issues)}` total (`open={issue_counts.get('open', 0)}`, `closed={issue_counts.get('closed', 0)}`)",
        f"- Pull requests: `{len(prs)}` total (`open={pr_counts.get('open', 0)}`, `closed={pr_counts.get('closed', 0)}`)",
        "",
        "## Recently Updated Issues",
        "",
    ]

    for issue in issues[:10]:
        labels = ", ".join(issue["labels"]) if issue["labels"] else "no labels"
        lines.append(f"- #{issue['number']} [{issue['state']}] {issue['title']} ({labels})")

    lines.extend(["", "## Recently Updated Pull Requests", ""])
    for pr in prs[:10]:
        suffix = " merged" if pr.get("merged_at") else ""
        lines.append(f"- #{pr['number']} [{pr['state']}{suffix}] {pr['title']} (`{pr['head']}` -> `{pr['base']}`)")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="666ghj/MiroFish", help="owner/repo to inspect")
    parser.add_argument("--state", default="open", help="GitHub state filter (open, closed, or all)")
    parser.add_argument("--limit", type=int, default=500, help="Maximum items to fetch per collection")
    parser.add_argument("--output", required=True, help="Path to write machine-readable JSON")
    parser.add_argument("--summary", required=True, help="Path to write markdown summary")
    args = parser.parse_args()

    owner, name = args.repo.split("/", 1)
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

    issues = [compact_issue(item) for item in issue_items if "pull_request" not in item]
    prs = [compact_pr(item) for item in pr_items]
    payload = {
        "repo": args.repo,
        "state": args.state,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "issues": summarize_counts(issues),
            "pull_requests": summarize_counts(prs),
        },
        "issues": issues,
        "pull_requests": prs,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(Path(args.summary), args.repo, args.state, issues, prs)

    print(
        f"Captured {len(issues)} issues and {len(prs)} pull requests from {args.repo} "
        f"into {os.path.relpath(output_path)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
