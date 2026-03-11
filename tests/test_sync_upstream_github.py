import unittest
from pathlib import Path
from unittest.mock import patch
import importlib.util
from urllib.error import HTTPError


def load_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "sync_upstream_github.py"
    spec = importlib.util.spec_from_file_location("sync_upstream_github", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sync_upstream_github = load_module()


class SyncUpstreamGithubTests(unittest.TestCase):
    def test_fetch_json_prefers_authenticated_gh_cli_when_no_token(self):
        with (
            patch.object(sync_upstream_github, "has_github_token", return_value=False),
            patch.object(sync_upstream_github, "can_use_gh_cli", return_value=True),
            patch.object(sync_upstream_github, "fetch_json_via_gh", return_value={"ok": True}) as mocked,
        ):
            payload = sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues?state=open")

        self.assertEqual(payload, {"ok": True})
        mocked.assert_called_once_with("https://api.github.com/repos/test/repo/issues?state=open")

    def test_fetch_json_rate_limit_error_mentions_gh_cli_fallback(self):
        rate_limited = HTTPError(
            url="https://api.github.com/repos/test/repo/issues",
            code=403,
            msg="rate limit exceeded",
            hdrs=None,
            fp=None,
        )

        with (
            patch.object(sync_upstream_github, "has_github_token", return_value=True),
            patch("urllib.request.urlopen", side_effect=rate_limited),
        ):
            with self.assertRaisesRegex(RuntimeError, "log into gh"):
                sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues")

    def test_github_api_paginated_collects_multiple_pages(self):
        responses = [
            [{"number": n} for n in range(1, 101)],
            [{"number": n} for n in range(101, 106)],
        ]

        with patch.object(sync_upstream_github, "github_api", side_effect=responses) as mocked:
            items = sync_upstream_github.github_api_paginated("/repos/test/repo/issues", {"state": "all"}, limit=105)

        self.assertEqual(items[0], {"number": 1})
        self.assertEqual(items[-1], {"number": 105})
        self.assertEqual(len(items), 105)
        self.assertEqual(mocked.call_count, 2)
        self.assertEqual(mocked.call_args_list[0].args[1]["page"], 1)
        self.assertEqual(mocked.call_args_list[1].args[1]["page"], 2)

    def test_compact_records_include_state_fields(self):
        issue = sync_upstream_github.compact_issue(
            {
                "number": 10,
                "title": "Issue title",
                "html_url": "https://example.test/issues/10",
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "closed_at": "2026-01-03T00:00:00Z",
                "labels": [{"name": "bug"}],
                "user": {"login": "alice"},
            }
        )
        pr = sync_upstream_github.compact_pr(
            {
                "number": 11,
                "title": "PR title",
                "html_url": "https://example.test/pull/11",
                "state": "closed",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-02T00:00:00Z",
                "closed_at": "2026-01-03T00:00:00Z",
                "merged_at": "2026-01-03T00:00:01Z",
                "head": {"ref": "feature"},
                "base": {"ref": "main"},
                "draft": False,
                "user": {"login": "bob"},
            }
        )

        self.assertEqual(issue["state"], "closed")
        self.assertEqual(issue["closed_at"], "2026-01-03T00:00:00Z")
        self.assertEqual(pr["state"], "closed")
        self.assertEqual(pr["merged_at"], "2026-01-03T00:00:01Z")


if __name__ == "__main__":
    unittest.main()
