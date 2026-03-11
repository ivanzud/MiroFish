#!/usr/bin/env python3
"""Fetch upstream GitHub issues and pull requests into a local summary."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"User-Agent": "mirofish-upstream-sync"})
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def github_api(path: str, params: dict[str, object]) -> object:
    query = urllib.parse.urlencode(params)
    return fetch_json(f"https://api.github.com{path}?{query}")


def compact_issue(issue: dict[str, object]) -> dict[str, object]:
    return {
        "number": issue["number"],
        "title": issue["title"],
        "url": issue["html_url"],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
        "labels": [label["name"] for label in issue.get("labels", [])],
        "author": issue.get("user", {}).get("login"),
    }


def compact_pr(pr: dict[str, object]) -> dict[str, object]:
    return {
        "number": pr["number"],
        "title": pr["title"],
        "url": pr["html_url"],
        "created_at": pr["created_at"],
        "updated_at": pr["updated_at"],
        "head": pr.get("head", {}).get("ref"),
        "base": pr.get("base", {}).get("ref"),
        "draft": pr.get("draft", False),
        "author": pr.get("user", {}).get("login"),
    }


def write_summary(path: Path, repo: str, issues: list[dict[str, object]], prs: list[dict[str, object]]) -> None:
    lines = [
        "# Upstream Triage Snapshot",
        "",
        f"- Repository: `{repo}`",
        f"- Captured: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Open issues: `{len(issues)}`",
        f"- Open pull requests: `{len(prs)}`",
        "",
        "## Recently Updated Issues",
        "",
    ]

    for issue in issues[:10]:
        labels = ", ".join(issue["labels"]) if issue["labels"] else "no labels"
        lines.append(f"- #{issue['number']} {issue['title']} ({labels})")

    lines.extend(["", "## Open Pull Requests", ""])
    for pr in prs[:10]:
        lines.append(f"- #{pr['number']} {pr['title']} (`{pr['head']}` -> `{pr['base']}`)")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="666ghj/MiroFish", help="owner/repo to inspect")
    parser.add_argument("--state", default="open", help="GitHub state filter")
    parser.add_argument("--limit", type=int, default=100, help="Maximum items to fetch per collection")
    parser.add_argument("--output", required=True, help="Path to write machine-readable JSON")
    parser.add_argument("--summary", required=True, help="Path to write markdown summary")
    args = parser.parse_args()

    owner, name = args.repo.split("/", 1)
    issue_items = github_api(
        f"/repos/{owner}/{name}/issues",
        {"state": args.state, "per_page": min(args.limit, 100)},
    )
    pr_items = github_api(
        f"/repos/{owner}/{name}/pulls",
        {"state": args.state, "per_page": min(args.limit, 100)},
    )

    issues = [compact_issue(item) for item in issue_items if "pull_request" not in item]
    prs = [compact_pr(item) for item in pr_items]
    payload = {
        "repo": args.repo,
        "state": args.state,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "issues": issues,
        "pull_requests": prs,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(Path(args.summary), args.repo, issues, prs)

    print(
        f"Captured {len(issues)} issues and {len(prs)} pull requests from {args.repo} "
        f"into {os.path.relpath(output_path)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
