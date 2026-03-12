import unittest
import io
import json
import tempfile
import threading
import time
from contextlib import nullcontext
from pathlib import Path
from unittest.mock import patch
import importlib.util
import subprocess
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
    def setUp(self):
        sync_upstream_github.GH_CLI_USABLE = None
        sync_upstream_github.GH_CLI_DISABLED_REASON = None

    def test_load_local_issue_coverage_reads_machine_readable_map(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            coverage_path = Path(tmpdir) / "coverage.json"
            coverage_path.write_text(
                json.dumps(
                    {
                        "issues": [
                            {"number": 133, "status": "covered", "summary": "Root endpoint returns backend status"},
                            {"number": 139, "status": "covered", "summary": "Zep auth errors are sanitized"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            coverage = sync_upstream_github.load_local_issue_coverage(coverage_path)

        self.assertEqual(sorted(coverage), [133, 139])
        self.assertEqual(coverage[139]["status"], "covered")

    def test_compact_issue_includes_local_coverage_when_available(self):
        issue = {
            "number": 139,
            "title": "Graph build task failed",
            "html_url": "https://example.test/issues/139",
            "state": "open",
            "created_at": "2026-03-10T00:00:00Z",
            "updated_at": "2026-03-11T00:00:00Z",
            "labels": [],
            "user": {"login": "alice"},
            "body": "provider traceback",
            "comments": 0,
        }

        compacted = sync_upstream_github.compact_issue(
            issue,
            {139: {"number": 139, "status": "covered", "summary": "Auth failures are sanitized"}},
        )

        self.assertEqual(compacted["local_coverage"]["status"], "covered")
        self.assertEqual(compacted["local_coverage"]["summary"], "Auth failures are sanitized")
        self.assertEqual(compacted["local_status"], "covered")
        self.assertEqual(compacted["local_summary"], "Auth failures are sanitized")
        self.assertEqual(compacted["triage_status"], "covered")
        self.assertEqual(compacted["summary"], "Auth failures are sanitized")
        self.assertEqual(compacted["coverage_status"], "covered")
        self.assertEqual(compacted["coverage_summary"], "Auth failures are sanitized")

    def test_compact_issue_promotes_body_excerpt_when_untracked(self):
        issue = {
            "number": 140,
            "title": "General commentary",
            "html_url": "https://example.test/issues/140",
            "state": "open",
            "created_at": "2026-03-10T00:00:00Z",
            "updated_at": "2026-03-11T00:00:00Z",
            "labels": [],
            "user": {"login": "alice"},
            "body": "This is the upstream body excerpt.",
            "comments": 0,
        }

        compacted = sync_upstream_github.compact_issue(issue, {})

        self.assertEqual(compacted["triage_status"], "untracked")
        self.assertEqual(compacted["summary"], "This is the upstream body excerpt.")

    def test_build_mirror_issue_body_includes_markers_and_local_coverage(self):
        body = sync_upstream_github.build_mirror_issue_body(
            "666ghj/MiroFish",
            {
                "number": 145,
                "title": "Duplicate entity nodes",
                "url": "https://example.test/issues/145",
                "state": "open",
                "updated_at": "2026-03-11T15:00:00Z",
                "labels": ["bug"],
                "author": "alice",
                "body_excerpt": "Graph contains duplicate entities",
                "recent_comments": [
                    {
                        "author": "bob",
                        "created_at": "2026-03-11T15:01:00Z",
                        "body_excerpt": "I can reproduce this too.",
                    }
                ],
                "local_coverage": {
                    "status": "tracked",
                    "summary": "Tracked in beads for repo-native follow-up",
                    "local_refs": [".beads/issues.jsonl", "docs/upstream-triage.md"],
                },
            },
        )

        self.assertIn("<!-- mirofish-upstream-repo:666ghj/MiroFish -->", body)
        self.assertIn("<!-- mirofish-upstream-issue:145 -->", body)
        self.assertIn("Tracked in beads for repo-native follow-up", body)
        self.assertIn("`bob` at `2026-03-11T15:01:00Z`", body)

    def test_extract_upstream_issue_marker_reads_repo_and_number(self):
        marker = sync_upstream_github.extract_upstream_issue_marker(
            "<!-- mirofish-upstream-repo:666ghj/MiroFish -->\n"
            "<!-- mirofish-upstream-issue:145 -->\n"
        )

        self.assertEqual(marker, ("666ghj/MiroFish", 145))

    def test_attach_fork_issue_mirror_metadata_marks_mirrored_entries(self):
        attached = sync_upstream_github.attach_fork_issue_mirror_metadata(
            [{"number": 145, "title": "Duplicate entity nodes"}],
            {145: {"number": 12, "url": "https://example.test/issues/12"}},
        )

        self.assertTrue(attached[0]["fork_issue_mirrored"])
        self.assertEqual(attached[0]["fork_issue_number"], 12)
        self.assertEqual(attached[0]["fork_issue_url"], "https://example.test/issues/12")

    def test_load_local_pr_coverage_reads_machine_readable_map(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            coverage_path = Path(tmpdir) / "coverage.json"
            coverage_path.write_text(
                json.dumps(
                    {
                        "pull_requests": [
                            {"number": 125, "status": "landed", "summary": "Diagnostics landed locally"},
                            {"number": 118, "status": "not_safe", "summary": "Needs a backend abstraction redesign"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            coverage = sync_upstream_github.load_local_pr_coverage(coverage_path)

        self.assertEqual(sorted(coverage), [118, 125])
        self.assertEqual(coverage[125]["status"], "landed")

    def test_compact_pr_includes_local_coverage_when_available(self):
        pr = {
            "number": 125,
            "title": "Improve diagnostics",
            "html_url": "https://example.test/pull/125",
            "state": "open",
            "created_at": "2026-03-10T00:00:00Z",
            "updated_at": "2026-03-11T00:00:00Z",
            "head": {"ref": "fix/issue-121", "sha": "abc123", "repo": {"full_name": "fork/repo", "clone_url": "https://example.test/fork/repo.git"}},
            "base": {"ref": "main", "repo": {"full_name": "666ghj/MiroFish"}},
            "draft": False,
            "mergeable_state": "clean",
            "labels": [],
            "user": {"login": "alice"},
            "body": "PR body",
            "comments": 0,
            "review_comments": 0,
        }

        compacted = sync_upstream_github.compact_pr(
            pr,
            mirrored_pr_numbers={125},
            fork_remote="origin",
            coverage_map={125: {"number": 125, "status": "landed", "summary": "Diagnostics landed locally"}},
        )

        self.assertEqual(compacted["local_coverage"]["status"], "landed")
        self.assertEqual(compacted["local_status"], "landed")
        self.assertEqual(compacted["local_summary"], "Diagnostics landed locally")
        self.assertEqual(compacted["triage_status"], "landed")
        self.assertEqual(compacted["summary"], "Diagnostics landed locally")
        self.assertEqual(compacted["coverage_status"], "landed")
        self.assertEqual(compacted["coverage_summary"], "Diagnostics landed locally")
        self.assertEqual(compacted["head_ref_name"], "fix/issue-121")
        self.assertEqual(compacted["base_ref_name"], "main")
        self.assertTrue(compacted["mirrored_to_origin"])
        self.assertEqual(compacted["mirror_ref"], "origin/mirror/upstream-pr-125")
        self.assertEqual(compacted["fork_mirror_ref"], "origin/mirror/upstream-pr-125")

    def test_attach_local_coverage_promotes_status_fields(self):
        attached = sync_upstream_github.attach_local_coverage(
            [{"number": 145, "title": "Duplicate entity nodes"}],
            {145: {"number": 145, "status": "tracked", "summary": "Tracked in beads"}},
        )

        self.assertEqual(attached[0]["local_status"], "tracked")
        self.assertEqual(attached[0]["local_summary"], "Tracked in beads")
        self.assertEqual(attached[0]["triage_status"], "tracked")
        self.assertEqual(attached[0]["summary"], "Tracked in beads")
        self.assertEqual(attached[0]["coverage_status"], "tracked")
        self.assertEqual(attached[0]["coverage_summary"], "Tracked in beads")

    def test_write_summary_includes_local_coverage_notes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.md"
            sync_upstream_github.write_summary(
                summary_path,
                "666ghj/MiroFish",
                "open",
                [
                    {
                        "number": 133,
                        "title": "Backend access confusion",
                        "state": "open",
                        "labels": ["question"],
                        "body_excerpt": "Backend root returned 404",
                        "recent_comments": [],
                        "local_coverage": {
                            "number": 133,
                            "status": "covered",
                            "summary": "Root and health endpoints now return backend status JSON",
                        },
                    }
                ],
                [],
                coverage_map_path="docs/upstream-coverage.json",
                captured_at="2026-03-11T09:00:00+00:00",
            )

            summary = summary_path.read_text(encoding="utf-8")

        self.assertIn("Local issue coverage map: `docs/upstream-coverage.json`", summary)
        self.assertIn("local coverage [covered]: Root and health endpoints now return backend status JSON", summary)

    def test_write_summary_includes_mirrored_issue_count(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.md"
            sync_upstream_github.write_summary(
                summary_path,
                "666ghj/MiroFish",
                "open",
                [
                    {
                        "number": 145,
                        "title": "Duplicate entity nodes",
                        "state": "open",
                        "labels": [],
                        "body_excerpt": "Body",
                        "recent_comments": [],
                        "fork_issue_mirrored": True,
                        "fork_issue_number": 12,
                    }
                ],
                [],
                mirror_issues_repo="ivanzud/MiroFish",
                captured_at="2026-03-11T09:00:00+00:00",
            )

            summary = summary_path.read_text(encoding="utf-8")

        self.assertIn("Mirrored in `ivanzud/MiroFish`: `1` of `1` issues", summary)
        self.assertIn("[open, mirror=#12]", summary)

    def test_write_summary_includes_pull_request_local_coverage_notes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = Path(tmpdir) / "summary.md"
            sync_upstream_github.write_summary(
                summary_path,
                "666ghj/MiroFish",
                "open",
                [],
                [
                    {
                        "number": 125,
                        "title": "Improve diagnostics",
                        "state": "open",
                        "head": "fix/issue-121",
                        "base": "main",
                        "mergeable_state": "clean",
                        "fork_mirrored": True,
                        "body_excerpt": "PR body",
                        "recent_comments": [],
                        "local_coverage": {
                            "number": 125,
                            "status": "landed",
                            "summary": "Diagnostics landed locally",
                        },
                    }
                ],
                fork_remote="origin",
                coverage_map_path="docs/upstream-coverage.json",
                captured_at="2026-03-11T09:00:00+00:00",
            )

            summary = summary_path.read_text(encoding="utf-8")

        self.assertIn("local coverage [landed]: Diagnostics landed locally", summary)

    def test_build_parser_accepts_legacy_output_flag_names(self):
        args = sync_upstream_github.build_parser().parse_args(
            [
                "--repo",
                "666ghj/MiroFish",
                "--json-out",
                "docs/upstream-open-state.json",
                "--md-out",
                "docs/upstream-open-summary.md",
            ]
        )

        self.assertEqual(args.output, "docs/upstream-open-state.json")
        self.assertEqual(args.summary, "docs/upstream-open-summary.md")

    def test_build_parser_accepts_max_workers_flag(self):
        args = sync_upstream_github.build_parser().parse_args(
            [
                "--output",
                "docs/upstream-open-state.json",
                "--summary",
                "docs/upstream-open-summary.md",
                "--max-workers",
                "4",
            ]
        )

        self.assertEqual(args.max_workers, 4)

    def test_build_parser_defaults_lock_wait_seconds_to_five(self):
        args = sync_upstream_github.build_parser().parse_args(
            [
                "--output",
                "docs/upstream-open-state.json",
                "--summary",
                "docs/upstream-open-summary.md",
            ]
        )

        self.assertEqual(args.lock_wait_seconds, 5.0)

    def test_build_parser_accepts_legacy_positional_repo_argument(self):
        parser = sync_upstream_github.build_parser()
        args = parser.parse_args(
            [
                "666ghj/MiroFish",
                "--output",
                "docs/upstream-open-state.json",
                "--summary",
                "docs/upstream-open-summary.md",
            ]
        )

        resolved_repo = sync_upstream_github.resolve_repo_argument(args, parser)

        self.assertEqual(resolved_repo, "666ghj/MiroFish")

    def test_resolve_repo_argument_rejects_conflicting_repo_values(self):
        parser = sync_upstream_github.build_parser()
        args = parser.parse_args(
            [
                "fork/MiroFish",
                "--repo",
                "666ghj/MiroFish",
                "--output",
                "docs/upstream-open-state.json",
                "--summary",
                "docs/upstream-open-summary.md",
            ]
        )

        with self.assertRaises(SystemExit):
            sync_upstream_github.resolve_repo_argument(args, parser)

    def test_snapshot_is_fresh_accepts_recent_capture(self):
        payload = {"captured_at": "2026-03-11T08:30:00+00:00"}

        with patch.object(sync_upstream_github, "datetime") as mocked_datetime:
            mocked_datetime.now.return_value = __import__("datetime").datetime(2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc)
            mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
            self.assertTrue(sync_upstream_github.snapshot_is_fresh(payload, 24))

    def test_snapshot_is_fresh_rejects_old_capture(self):
        payload = {"captured_at": "2026-03-09T08:30:00+00:00"}

        with patch.object(sync_upstream_github, "datetime") as mocked_datetime:
            mocked_datetime.now.return_value = __import__("datetime").datetime(2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc)
            mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
            self.assertFalse(sync_upstream_github.snapshot_is_fresh(payload, 24))

    def test_snapshot_is_fresh_accepts_legacy_generated_at(self):
        payload = {"generated_at": "2026-03-11T08:30:00+00:00"}

        with patch.object(sync_upstream_github, "datetime") as mocked_datetime:
            mocked_datetime.now.return_value = __import__("datetime").datetime(2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc)
            mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
            self.assertTrue(sync_upstream_github.snapshot_is_fresh(payload, 24))

    def test_normalize_excerpt_collapses_whitespace_and_truncates(self):
        excerpt = sync_upstream_github.normalize_excerpt(" line 1\n\nline\t2  " * 20, limit=30)

        self.assertEqual(excerpt, "line 1 line 2 line 1 line 2 l…")

    def test_fetch_recent_comments_returns_compact_preview(self):
        with patch.object(
            sync_upstream_github,
            "fetch_json",
            return_value=[
                {
                    "user": {"login": "alice"},
                    "created_at": "2026-01-02T00:00:00Z",
                    "updated_at": "2026-01-03T00:00:00Z",
                    "html_url": "https://example.test/comment/1",
                    "body": "First line\nSecond line",
                }
            ],
        ) as mocked:
            comments = sync_upstream_github.fetch_recent_comments("https://api.github.com/repos/test/repo/issues/10/comments")

        self.assertEqual(
            comments,
            [
                {
                    "author": "alice",
                    "created_at": "2026-01-02T00:00:00Z",
                    "updated_at": "2026-01-03T00:00:00Z",
                    "url": "https://example.test/comment/1",
                    "body_excerpt": "First line Second line",
                }
            ],
        )
        mocked.assert_called_once()
        self.assertIn("per_page=3", mocked.call_args.args[0])

    def test_fetch_json_disables_gh_cli_after_rate_limit(self):
        with patch.object(sync_upstream_github, "has_github_token", return_value=False), patch.object(
            sync_upstream_github,
            "can_use_gh_cli",
            side_effect=lambda: not sync_upstream_github.GH_CLI_DISABLED_REASON,
        ), patch.object(
            sync_upstream_github,
            "fetch_json_via_gh",
            side_effect=RuntimeError("gh api failed: rate limit exceeded"),
        ) as gh_fetch, patch.object(
            sync_upstream_github,
            "_fetch_json_via_http",
            side_effect=[{"source": "http-1"}, {"source": "http-2"}],
        ) as http_fetch:
            first = sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues")
            second = sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/pulls")

        self.assertEqual(first["source"], "http-1")
        self.assertEqual(second["source"], "http-2")
        self.assertEqual(gh_fetch.call_count, 1)
        self.assertEqual(http_fetch.call_count, 2)
        self.assertEqual(sync_upstream_github.GH_CLI_DISABLED_REASON, "GitHub CLI rate limited")

    def test_list_mirrored_pull_request_numbers_reads_remote_and_local_refs(self):
        with patch.object(
            sync_upstream_github.subprocess,
            "run",
            return_value=type(
                "Completed",
                (),
                {"stdout": "origin/mirror/upstream-pr-101\nmirror/upstream-pr-102\norigin/main\n"},
            )(),
        ) as mocked:
            mirrored = sync_upstream_github.list_mirrored_pull_request_numbers("origin")

        self.assertEqual(mirrored, {101, 102})
        self.assertEqual(
            mocked.call_args.args[0],
            [
                "git",
                "for-each-ref",
                "--format=%(refname:short)",
                "refs/remotes/origin/mirror/upstream-pr-*",
                "refs/heads/mirror/upstream-pr-*",
            ],
        )

    def test_mirror_pull_request_refs_fetches_and_pushes_missing_pr_heads(self):
        pull_requests = [
            {"number": 155},
            {"number": 151},
        ]

        with patch.object(sync_upstream_github, "run_git_command", return_value="") as mocked:
            mirrored = sync_upstream_github.mirror_pull_request_refs(
                "666ghj/MiroFish",
                "origin",
                pull_requests,
                mirrored_pr_numbers={151},
            )

        self.assertEqual(mirrored, {151, 155})
        self.assertEqual(
            mocked.call_args_list[0].args[0],
            [
                "git",
                "fetch",
                "--force",
                "https://github.com/666ghj/MiroFish.git",
                "pull/155/head:refs/remotes/upstream-sync/pr-155",
            ],
        )
        self.assertEqual(
            mocked.call_args_list[1].args[0],
            [
                "git",
                "push",
                "origin",
                "refs/remotes/upstream-sync/pr-155:refs/heads/mirror/upstream-pr-155",
            ],
        )
        self.assertEqual(len(mocked.call_args_list), 2)

    def test_mirror_pull_request_refs_warns_and_continues_when_push_fails(self):
        pull_requests = [{"number": 155}, {"number": 156}]

        with (
            patch.object(
                sync_upstream_github,
                "run_git_command",
                side_effect=[
                    "",
                    RuntimeError("push failed"),
                    "",
                    "",
                ],
            ),
            patch("sys.stderr", new_callable=io.StringIO) as stderr,
        ):
            mirrored = sync_upstream_github.mirror_pull_request_refs(
                "666ghj/MiroFish",
                "origin",
                pull_requests,
            )

        self.assertEqual(mirrored, {156})
        self.assertIn("unable to mirror upstream PR #155", stderr.getvalue())

    def test_fetch_json_prefers_authenticated_gh_cli_when_no_token(self):
        with (
            patch.object(sync_upstream_github, "has_github_token", return_value=False),
            patch.object(sync_upstream_github, "can_use_gh_cli", return_value=True),
            patch.object(sync_upstream_github, "fetch_json_via_gh", return_value={"ok": True}) as mocked,
        ):
            payload = sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues?state=open")

        self.assertEqual(payload, {"ok": True})
        mocked.assert_called_once_with("https://api.github.com/repos/test/repo/issues?state=open")

    def test_fetch_json_falls_back_to_http_when_gh_cli_request_fails(self):
        with (
            patch.object(sync_upstream_github, "has_github_token", return_value=False),
            patch.object(sync_upstream_github, "can_use_gh_cli", return_value=True),
            patch.object(sync_upstream_github, "fetch_json_via_gh", side_effect=RuntimeError("boom")),
            patch.object(sync_upstream_github, "_fetch_json_via_http", return_value={"ok": True}) as mocked_http,
        ):
            payload = sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues?state=open")

        self.assertEqual(payload, {"ok": True})
        mocked_http.assert_called_once_with("https://api.github.com/repos/test/repo/issues?state=open")

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

    def test_fetch_json_http_retry_recovers_from_transient_500(self):
        transient_error = HTTPError(
            url="https://api.github.com/repos/test/repo/issues",
            code=500,
            msg="Internal Server Error",
            hdrs=None,
            fp=None,
        )
        payload = io.BytesIO(b'{"ok": true}')

        with (
            patch.object(sync_upstream_github, "has_github_token", return_value=True),
            patch("urllib.request.urlopen", side_effect=[transient_error, nullcontext(payload)]),
            patch.object(sync_upstream_github.time, "sleep") as mocked_sleep,
        ):
            result = sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues")

        self.assertEqual(result, {"ok": True})
        mocked_sleep.assert_called_once_with(1)

    def test_fetch_json_http_retry_raises_runtime_error_after_repeated_5xx(self):
        transient_error = HTTPError(
            url="https://api.github.com/repos/test/repo/issues",
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=None,
        )

        with (
            patch.object(sync_upstream_github, "has_github_token", return_value=True),
            patch("urllib.request.urlopen", side_effect=[transient_error] * sync_upstream_github.GH_API_MAX_ATTEMPTS),
            patch.object(sync_upstream_github.time, "sleep") as mocked_sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "HTTP 503"):
                sync_upstream_github.fetch_json("https://api.github.com/repos/test/repo/issues")

        self.assertEqual(mocked_sleep.call_count, sync_upstream_github.GH_API_MAX_ATTEMPTS - 1)

    def test_list_fork_issue_mirrors_filters_by_marker(self):
        listed = json.dumps(
            [
                {
                    "number": 12,
                    "title": "[Upstream #145] Duplicate entity nodes",
                    "body": "<!-- mirofish-upstream-repo:666ghj/MiroFish -->\n<!-- mirofish-upstream-issue:145 -->\n",
                    "url": "https://example.test/issues/12",
                    "state": "OPEN",
                },
                {
                    "number": 13,
                    "title": "Local issue",
                    "body": "No marker",
                    "url": "https://example.test/issues/13",
                    "state": "OPEN",
                },
            ]
        )
        with patch.object(sync_upstream_github, "run_gh_command", return_value=listed):
            mirrors = sync_upstream_github.list_fork_issue_mirrors("ivanzud/MiroFish", "666ghj/MiroFish")

        self.assertEqual(sorted(mirrors), [145])
        self.assertEqual(mirrors[145]["number"], 12)

    def test_sync_fork_issue_mirror_closes_closed_upstream_issue(self):
        issue = {
            "number": 145,
            "title": "Duplicate entity nodes",
            "url": "https://example.test/issues/145",
            "state": "closed",
            "updated_at": "2026-03-11T15:00:00Z",
            "labels": [],
            "author": "alice",
            "body_excerpt": "Body",
            "recent_comments": [],
        }
        current = {
            "number": 8,
            "title": "[Upstream #145] Duplicate entity nodes",
            "body": sync_upstream_github.build_mirror_issue_body(
                "666ghj/MiroFish",
                {**issue, "state": "open"},
            ),
            "state": "OPEN",
        }

        with patch.object(sync_upstream_github, "run_gh_command") as mocked_run:
            sync_upstream_github.sync_fork_issue_mirror(
                "ivanzud/MiroFish",
                "666ghj/MiroFish",
                issue,
                current,
            )

        self.assertEqual(mocked_run.call_args_list[0].args[0][:4], ["issue", "edit", "-R", "ivanzud/MiroFish"])
        self.assertEqual(
            mocked_run.call_args_list[1].args[0],
            ["issue", "close", "-R", "ivanzud/MiroFish", "8", "--reason", "completed"],
        )

    def test_sync_fork_issue_mirror_closes_new_closed_issue_after_create(self):
        issue = {
            "number": 145,
            "title": "Duplicate entity nodes",
            "url": "https://example.test/issues/145",
            "state": "closed",
            "updated_at": "2026-03-11T15:00:00Z",
            "labels": [],
            "author": "alice",
            "body_excerpt": "Body",
            "recent_comments": [],
        }

        with patch.object(
            sync_upstream_github,
            "run_gh_command",
            side_effect=["https://github.com/ivanzud/MiroFish/issues/88\n", ""],
        ) as mocked_run:
            sync_upstream_github.sync_fork_issue_mirror(
                "ivanzud/MiroFish",
                "666ghj/MiroFish",
                issue,
                None,
            )

        self.assertEqual(mocked_run.call_args_list[0].args[0][:4], ["issue", "create", "-R", "ivanzud/MiroFish"])
        self.assertEqual(
            mocked_run.call_args_list[1].args[0],
            ["issue", "close", "-R", "ivanzud/MiroFish", "88", "--reason", "completed"],
        )

    def test_sync_fork_issue_mirror_reopens_when_upstream_reopens(self):
        issue = {
            "number": 145,
            "title": "Duplicate entity nodes",
            "url": "https://example.test/issues/145",
            "state": "open",
            "updated_at": "2026-03-11T15:00:00Z",
            "labels": [],
            "author": "alice",
            "body_excerpt": "Body",
            "recent_comments": [],
        }
        current = {
            "number": 8,
            "title": "[Upstream #145] Duplicate entity nodes",
            "body": sync_upstream_github.build_mirror_issue_body(
                "666ghj/MiroFish",
                {**issue, "state": "closed"},
            ),
            "state": "CLOSED",
        }

        with patch.object(sync_upstream_github, "run_gh_command") as mocked_run:
            sync_upstream_github.sync_fork_issue_mirror(
                "ivanzud/MiroFish",
                "666ghj/MiroFish",
                issue,
                current,
            )

        self.assertEqual(mocked_run.call_args_list[0].args[0][:4], ["issue", "edit", "-R", "ivanzud/MiroFish"])
        self.assertEqual(
            mocked_run.call_args_list[1].args[0],
            ["issue", "reopen", "-R", "ivanzud/MiroFish", "8"],
        )

    def test_mirror_issues_to_fork_creates_and_updates_issue_mirrors(self):
        issues = [
            {
                "number": 145,
                "title": "Duplicate entity nodes",
                "url": "https://example.test/issues/145",
                "state": "open",
                "updated_at": "2026-03-11T15:00:00Z",
                "labels": [],
                "author": "alice",
                "body_excerpt": "Body",
                "recent_comments": [],
            },
            {
                "number": 133,
                "title": "Backend root confusion",
                "url": "https://example.test/issues/133",
                "state": "open",
                "updated_at": "2026-03-11T15:00:00Z",
                "labels": [],
                "author": "bob",
                "body_excerpt": "Body",
                "recent_comments": [],
            },
        ]
        existing_before = {
            133: {
                "number": 7,
                "title": "[Upstream #133] stale title",
                "body": "stale body",
                "url": "https://example.test/issues/7",
                "state": "OPEN",
            }
        }
        existing_after = {
            133: {
                "number": 7,
                "title": "[Upstream #133] Backend root confusion",
                "body": sync_upstream_github.build_mirror_issue_body("666ghj/MiroFish", issues[1]),
                "url": "https://example.test/issues/7",
                "state": "OPEN",
            },
            145: {
                "number": 8,
                "title": "[Upstream #145] Duplicate entity nodes",
                "body": sync_upstream_github.build_mirror_issue_body("666ghj/MiroFish", issues[0]),
                "url": "https://example.test/issues/8",
                "state": "OPEN",
            },
        }

        with patch.object(
            sync_upstream_github,
            "list_fork_issue_mirrors",
            side_effect=[existing_before, existing_after],
        ), patch.object(sync_upstream_github, "run_gh_command") as mocked_run:
            mirrored = sync_upstream_github.mirror_issues_to_fork(
                "ivanzud/MiroFish",
                "666ghj/MiroFish",
                issues,
            )

        create_call = mocked_run.call_args_list[0]
        edit_call = mocked_run.call_args_list[1]
        self.assertIn("issue", create_call.args[0])
        self.assertIn("create", create_call.args[0])
        self.assertIn("[Upstream #145] Duplicate entity nodes", create_call.args[0])
        self.assertIn("issue", edit_call.args[0])
        self.assertIn("edit", edit_call.args[0])
        self.assertEqual(mirrored[0]["fork_issue_number"], 8)
        self.assertEqual(mirrored[1]["fork_issue_number"], 7)

    def test_main_reuses_recent_cached_snapshot_on_rate_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            summary_path = Path(tmpdir) / "summary.md"
            coverage_path = Path(tmpdir) / "coverage.json"
            cached_payload = {
                "repo": "666ghj/MiroFish",
                "state": "open",
                "captured_at": "2026-03-11T08:30:00+00:00",
                "fork_remote": "origin",
                "mirror_issues_repo": "ivanzud/MiroFish",
                "issues": [
                    {
                        "number": 1,
                        "title": "Issue",
                        "url": "https://example.test/issues/1",
                        "state": "open",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-11T00:00:00Z",
                        "closed_at": None,
                        "labels": [],
                        "author": "alice",
                        "body_excerpt": "Issue body",
                        "comment_count": 0,
                        "recent_comments": [],
                        "fork_issue_mirrored": True,
                        "fork_issue_number": 99,
                        "fork_issue_url": "https://example.test/issues/99",
                    }
                ],
                "pull_requests": [
                    {
                        "number": 2,
                        "title": "PR",
                        "url": "https://example.test/pull/2",
                        "state": "open",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-11T00:00:00Z",
                        "closed_at": None,
                        "merged_at": None,
                        "head": "feature",
                        "head_sha": "abc123",
                        "head_repo": "fork/repo",
                        "head_clone_url": "https://example.test/fork/repo.git",
                        "base": "main",
                        "base_repo": "666ghj/MiroFish",
                        "draft": False,
                        "mergeable_state": "clean",
                        "labels": [],
                        "author": "bob",
                        "body_excerpt": "PR body",
                        "comment_count": 0,
                        "review_comment_count": 0,
                        "recent_comments": [],
                        "fork_mirrored": True,
                        "fork_mirror_ref": "origin/mirror/upstream-pr-2",
                    }
                ],
            }
            output_path.write_text(json.dumps(cached_payload), encoding="utf-8")
            coverage_path.write_text(
                json.dumps(
                    {
                        "issues": [
                            {"number": 1, "status": "covered", "summary": "Issue handled locally"}
                        ],
                        "pull_requests": [
                            {"number": 2, "status": "landed", "summary": "PR landed locally"}
                        ],
                    }
                ),
                encoding="utf-8",
            )

            stderr = io.StringIO()
            stdout = io.StringIO()
            rate_limit_error = RuntimeError("GitHub API rate limit exceeded. Set GITHUB_TOKEN or GH_TOKEN.")

            with (
                patch.object(
                    sync_upstream_github,
                    "build_parser",
                    return_value=sync_upstream_github.build_parser(),
                ),
                patch.object(
                    sync_upstream_github.sys,
                    "argv",
                    [
                        "sync_upstream_github.py",
                        "--repo",
                        "666ghj/MiroFish",
                        "--state",
                        "open",
                        "--output",
                        str(output_path),
                        "--summary",
                        str(summary_path),
                        "--fork-remote",
                        "origin",
                        "--mirror-issues-repo",
                        "ivanzud/MiroFish",
                        "--coverage-map",
                        str(coverage_path),
                    ],
                ),
                patch.object(sync_upstream_github, "github_api_paginated", side_effect=rate_limit_error),
                patch("sys.stderr", stderr),
                patch("sys.stdout", stdout),
                patch.object(sync_upstream_github, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = __import__("datetime").datetime(2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc)
                mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
                result = sync_upstream_github.main()

            self.assertEqual(result, 0)
            self.assertTrue(summary_path.exists())
            self.assertIn("reusing fresh cached snapshot", stderr.getvalue())
            self.assertIn("Reused cached snapshot", stdout.getvalue())
            summary_text = summary_path.read_text(encoding="utf-8")
            self.assertIn("2026-03-11T08:30:00+00:00", summary_text)
            self.assertIn("local coverage [landed]: PR landed locally", summary_text)
            self.assertIn("Mirrored in `ivanzud/MiroFish`: `1` of `1` issues", summary_text)
            refreshed_payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(refreshed_payload["mirror_issues_repo"], "ivanzud/MiroFish")
            self.assertEqual(refreshed_payload["pull_requests"][0]["local_coverage"]["status"], "landed")

    def test_main_writes_backward_compatible_generated_at_field(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            summary_path = Path(tmpdir) / "summary.md"
            pr_payload = {
                "number": 2,
                "title": "PR",
                "html_url": "https://example.test/pull/2",
                "state": "open",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-11T00:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "head": {
                    "ref": "feature",
                    "sha": "abc123",
                    "repo": {
                        "full_name": "fork/repo",
                        "clone_url": "https://example.test/fork/repo.git",
                    },
                },
                "base": {
                    "ref": "main",
                    "repo": {"full_name": "666ghj/MiroFish"},
                },
                "draft": False,
                "mergeable_state": "clean",
                "labels": [],
                "user": {"login": "bob"},
                "body": "PR body",
                "comments": 0,
                "review_comments": 0,
            }

            with (
                patch.object(
                    sync_upstream_github.sys,
                    "argv",
                    [
                        "sync_upstream_github.py",
                        "--repo",
                        "666ghj/MiroFish",
                        "--state",
                        "open",
                        "--output",
                        str(output_path),
                        "--summary",
                        str(summary_path),
                    ],
                ),
                patch.object(
                    sync_upstream_github,
                    "github_api_paginated",
                    side_effect=[
                        [
                            {
                                "number": 1,
                                "title": "Issue",
                                "html_url": "https://example.test/issues/1",
                                "state": "open",
                                "created_at": "2026-03-10T00:00:00Z",
                                "updated_at": "2026-03-11T00:00:00Z",
                                "closed_at": None,
                                "labels": [],
                                "user": {"login": "alice"},
                                "body": "Issue body",
                                "comments": 0,
                            }
                        ],
                        [pr_payload],
                    ],
                ),
                patch.object(sync_upstream_github, "hydrate_pull_requests", return_value=[pr_payload]),
                patch.object(sync_upstream_github, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = __import__("datetime").datetime(2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc)
                mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
                result = sync_upstream_github.main()

            self.assertEqual(result, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["captured_at"], "2026-03-11T09:00:00+00:00")
            self.assertEqual(payload["generated_at"], "2026-03-11T09:00:00+00:00")
            self.assertIn("2026-03-11T09:00:00+00:00", summary_path.read_text(encoding="utf-8"))

    def test_main_accepts_legacy_positional_repo_argument(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            summary_path = Path(tmpdir) / "summary.md"
            pr_payload = {
                "number": 2,
                "title": "PR",
                "html_url": "https://example.test/pull/2",
                "state": "open",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-11T00:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "head": {
                    "ref": "feature",
                    "sha": "abc123",
                    "repo": {
                        "full_name": "fork/repo",
                        "clone_url": "https://example.test/fork/repo.git",
                    },
                },
                "base": {
                    "ref": "main",
                    "repo": {"full_name": "666ghj/MiroFish"},
                },
                "draft": False,
                "mergeable_state": "clean",
                "labels": [],
                "user": {"login": "bob"},
                "body": "PR body",
                "comments": 0,
                "review_comments": 0,
            }

            with (
                patch.object(
                    sync_upstream_github.sys,
                    "argv",
                    [
                        "sync_upstream_github.py",
                        "666ghj/MiroFish",
                        "--state",
                        "open",
                        "--output",
                        str(output_path),
                        "--summary",
                        str(summary_path),
                    ],
                ),
                patch.object(
                    sync_upstream_github,
                    "github_api_paginated",
                    side_effect=[
                        [
                            {
                                "number": 1,
                                "title": "Issue",
                                "html_url": "https://example.test/issues/1",
                                "state": "open",
                                "created_at": "2026-03-10T00:00:00Z",
                                "updated_at": "2026-03-11T00:00:00Z",
                                "closed_at": None,
                                "labels": [],
                                "user": {"login": "alice"},
                                "body": "Issue body",
                                "comments": 0,
                            }
                        ],
                        [pr_payload],
                    ],
                ),
                patch.object(sync_upstream_github, "hydrate_pull_requests", return_value=[pr_payload]),
                patch.object(sync_upstream_github, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = __import__("datetime").datetime(
                    2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc
                )
                mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
                result = sync_upstream_github.main()

            self.assertEqual(result, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["repo"], "666ghj/MiroFish")

    def test_main_mirrors_missing_pr_refs_before_compaction(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            summary_path = Path(tmpdir) / "summary.md"
            pr_payload = {
                "number": 155,
                "title": "PR",
                "html_url": "https://example.test/pull/155",
                "state": "open",
                "created_at": "2026-03-10T00:00:00Z",
                "updated_at": "2026-03-11T00:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "head": {
                    "ref": "feature",
                    "sha": "abc123",
                    "repo": {
                        "full_name": "fork/repo",
                        "clone_url": "https://example.test/fork/repo.git",
                    },
                },
                "base": {
                    "ref": "main",
                    "repo": {"full_name": "666ghj/MiroFish"},
                },
                "draft": False,
                "mergeable_state": "clean",
                "labels": [],
                "user": {"login": "bob"},
                "body": "PR body",
                "comments": 0,
                "review_comments": 0,
            }

            with (
                patch.object(
                    sync_upstream_github.sys,
                    "argv",
                    [
                        "sync_upstream_github.py",
                        "--repo",
                        "666ghj/MiroFish",
                        "--state",
                        "open",
                        "--output",
                        str(output_path),
                        "--summary",
                        str(summary_path),
                        "--fork-remote",
                        "origin",
                    ],
                ),
                patch.object(
                    sync_upstream_github,
                    "github_api_paginated",
                    side_effect=[
                        [
                            {
                                "number": 1,
                                "title": "Issue",
                                "html_url": "https://example.test/issues/1",
                                "state": "open",
                                "created_at": "2026-03-10T00:00:00Z",
                                "updated_at": "2026-03-11T00:00:00Z",
                                "closed_at": None,
                                "labels": [],
                                "user": {"login": "alice"},
                                "body": "Issue body",
                                "comments": 0,
                            }
                        ],
                        [pr_payload],
                    ],
                ),
                patch.object(sync_upstream_github, "hydrate_pull_requests", return_value=[pr_payload]),
                patch.object(sync_upstream_github, "list_mirrored_pull_request_numbers", return_value=set()),
                patch.object(sync_upstream_github, "mirror_pull_request_refs", return_value={155}) as mirrored,
                patch.object(sync_upstream_github, "compact_pull_requests", return_value=[]) as compacted,
                patch.object(sync_upstream_github, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = __import__("datetime").datetime(
                    2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc
                )
                mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
                result = sync_upstream_github.main()

        self.assertEqual(result, 0)
        mirrored.assert_called_once_with("666ghj/MiroFish", "origin", [pr_payload], set())
        compacted_args = compacted.call_args
        self.assertEqual(compacted_args.args[0], [pr_payload])
        self.assertEqual(compacted_args.args[1], {155})
        self.assertEqual(compacted_args.args[2], "origin")
        self.assertEqual(
            compacted_args.kwargs["max_workers"],
            sync_upstream_github.DEFAULT_MAX_WORKERS,
        )
        self.assertIsInstance(compacted_args.kwargs["coverage_map"], dict)

    def test_main_reuses_recent_cached_snapshot_when_pr_hydration_rate_limited(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            summary_path = Path(tmpdir) / "summary.md"
            cached_payload = {
                "repo": "666ghj/MiroFish",
                "state": "open",
                "captured_at": "2026-03-11T08:30:00+00:00",
                "fork_remote": "origin",
                "issues": [
                    {
                        "number": 1,
                        "title": "Issue",
                        "url": "https://example.test/issues/1",
                        "state": "open",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-11T00:00:00Z",
                        "closed_at": None,
                        "labels": [],
                        "author": "alice",
                        "body_excerpt": "Issue body",
                        "comment_count": 0,
                        "recent_comments": [],
                    }
                ],
                "pull_requests": [
                    {
                        "number": 2,
                        "title": "PR",
                        "url": "https://example.test/pull/2",
                        "state": "open",
                        "created_at": "2026-03-10T00:00:00Z",
                        "updated_at": "2026-03-11T00:00:00Z",
                        "closed_at": None,
                        "merged_at": None,
                        "head": "feature",
                        "head_sha": "abc123",
                        "head_repo": "fork/repo",
                        "head_clone_url": "https://example.test/fork/repo.git",
                        "base": "main",
                        "base_repo": "666ghj/MiroFish",
                        "draft": False,
                        "mergeable_state": "clean",
                        "labels": [],
                        "author": "bob",
                        "body_excerpt": "PR body",
                        "comment_count": 0,
                        "review_comment_count": 0,
                        "recent_comments": [],
                        "fork_mirrored": True,
                        "fork_mirror_ref": "origin/mirror/upstream-pr-2",
                    }
                ],
            }
            output_path.write_text(json.dumps(cached_payload), encoding="utf-8")

            stderr = io.StringIO()
            stdout = io.StringIO()
            rate_limit_error = RuntimeError("GitHub API rate limit exceeded while hydrating pull request details.")

            with (
                patch.object(
                    sync_upstream_github.sys,
                    "argv",
                    [
                        "sync_upstream_github.py",
                        "--repo",
                        "666ghj/MiroFish",
                        "--state",
                        "open",
                        "--output",
                        str(output_path),
                        "--summary",
                        str(summary_path),
                        "--fork-remote",
                        "origin",
                    ],
                ),
                patch.object(
                    sync_upstream_github,
                    "github_api_paginated",
                    side_effect=[
                        [
                            {
                                "number": 1,
                                "title": "Issue title",
                                "html_url": "https://example.test/issues/1",
                                "state": "open",
                                "created_at": "2026-03-10T00:00:00Z",
                                "updated_at": "2026-03-11T00:00:00Z",
                                "closed_at": None,
                                "labels": [],
                                "user": {"login": "alice"},
                                "body": "Issue body",
                                "comments": 0,
                            }
                        ],
                        [
                            {
                                "number": 2,
                                "title": "PR title",
                                "html_url": "https://example.test/pull/2",
                                "state": "open",
                                "created_at": "2026-03-10T00:00:00Z",
                                "updated_at": "2026-03-11T00:00:00Z",
                                "closed_at": None,
                                "merged_at": None,
                                "head": {"ref": "feature"},
                                "base": {"ref": "main"},
                                "comments": 0,
                                "review_comments": 0,
                            }
                        ],
                    ],
                ),
                patch.object(
                    sync_upstream_github,
                    "compact_issues",
                    return_value=cached_payload["issues"],
                ),
                patch.object(
                    sync_upstream_github,
                    "hydrate_pull_requests",
                    side_effect=rate_limit_error,
                ),
                patch("sys.stderr", stderr),
                patch("sys.stdout", stdout),
                patch.object(sync_upstream_github, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = __import__("datetime").datetime(
                    2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc
                )
                mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
                result = sync_upstream_github.main()

            self.assertEqual(result, 0)
            self.assertTrue(summary_path.exists())
            self.assertIn("reusing fresh cached snapshot", stderr.getvalue())
            self.assertIn("Reused cached snapshot", stdout.getvalue())
            self.assertIn("captured_at=2026-03-11T08:30:00+00:00", stderr.getvalue())

    def test_repo_lock_rejects_overlapping_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            with sync_upstream_github.repo_lock(output_path, "666ghj/MiroFish"):
                with self.assertRaisesRegex(RuntimeError, "already refreshing 666ghj/MiroFish"):
                    with sync_upstream_github.repo_lock(output_path, "666ghj/MiroFish"):
                        pass

    def test_repo_lock_waits_for_overlapping_run_when_timeout_allows(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            release_lock = threading.Event()
            acquired_lock = threading.Event()

            def hold_lock() -> None:
                with sync_upstream_github.repo_lock(output_path, "666ghj/MiroFish"):
                    acquired_lock.set()
                    release_lock.wait(timeout=1)

            worker = threading.Thread(target=hold_lock)
            worker.start()
            self.assertTrue(acquired_lock.wait(timeout=1))

            started = time.monotonic()
            try:
                release_lock.set()
                with sync_upstream_github.repo_lock(
                    output_path,
                    "666ghj/MiroFish",
                    wait_timeout=0.5,
                    poll_interval=0.01,
                ):
                    pass
            finally:
                worker.join(timeout=1)

            self.assertGreaterEqual(time.monotonic() - started, 0.0)

    def test_repo_lock_wait_timeout_mentions_lock_wait_flag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            with sync_upstream_github.repo_lock(output_path, "666ghj/MiroFish"):
                with self.assertRaisesRegex(RuntimeError, "--lock-wait-seconds"):
                    with sync_upstream_github.repo_lock(
                        output_path,
                        "666ghj/MiroFish",
                        wait_timeout=0.02,
                        poll_interval=0.01,
                    ):
                        pass

    def test_main_raises_on_rate_limit_when_cache_is_stale(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "state.json"
            output_path.write_text(
                json.dumps(
                    {
                        "repo": "666ghj/MiroFish",
                        "state": "open",
                        "captured_at": "2026-03-01T08:30:00+00:00",
                        "issues": [],
                        "pull_requests": [],
                    }
                ),
                encoding="utf-8",
            )

            rate_limit_error = RuntimeError("GitHub API rate limit exceeded. Set GITHUB_TOKEN or GH_TOKEN.")
            with (
                patch.object(
                    sync_upstream_github.sys,
                    "argv",
                    [
                        "sync_upstream_github.py",
                        "--repo",
                        "666ghj/MiroFish",
                        "--state",
                        "open",
                        "--output",
                        str(output_path),
                        "--summary",
                        str(Path(tmpdir) / "summary.md"),
                    ],
                ),
                patch.object(sync_upstream_github, "github_api_paginated", side_effect=rate_limit_error),
                patch.object(sync_upstream_github, "datetime") as mocked_datetime,
            ):
                mocked_datetime.now.return_value = __import__("datetime").datetime(2026, 3, 11, 9, 0, tzinfo=__import__("datetime").timezone.utc)
                mocked_datetime.fromisoformat = __import__("datetime").datetime.fromisoformat
                with self.assertRaisesRegex(RuntimeError, "rate limit exceeded"):
                    sync_upstream_github.main()

    def test_fetch_json_via_gh_retries_transient_failures(self):
        transient = subprocess.CalledProcessError(
            1,
            ["gh", "api", "/repos/test/repo/pulls/101"],
            stderr="HTTP 502 from GitHub",
        )
        success = type("Completed", (), {"stdout": '{"ok": true}'})()

        with (
            patch.object(sync_upstream_github.subprocess, "run", side_effect=[transient, success]) as mocked,
            patch.object(sync_upstream_github.time, "sleep") as mocked_sleep,
        ):
            payload = sync_upstream_github.fetch_json_via_gh("https://api.github.com/repos/test/repo/pulls/101")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(mocked.call_count, 2)
        mocked_sleep.assert_called_once_with(1)
        self.assertEqual(mocked.call_args.kwargs["timeout"], sync_upstream_github.REQUEST_TIMEOUT)

    def test_fetch_json_via_gh_sets_subprocess_timeout(self):
        success = type("Completed", (), {"stdout": '{"ok": true}'})()

        with patch.object(sync_upstream_github.subprocess, "run", return_value=success) as mocked:
            payload = sync_upstream_github.fetch_json_via_gh("https://api.github.com/repos/test/repo/pulls/101")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(mocked.call_args.kwargs["timeout"], sync_upstream_github.REQUEST_TIMEOUT)

    def test_fetch_json_via_http_sets_request_timeout(self):
        response = type("Response", (), {"__enter__": lambda self: self, "__exit__": lambda *args: None, "read": lambda self: b'{"ok": true}'})()

        with patch("urllib.request.urlopen", return_value=response) as mocked:
            payload = sync_upstream_github._fetch_json_via_http("https://api.github.com/repos/test/repo/issues")

        self.assertEqual(payload, {"ok": True})
        self.assertEqual(mocked.call_args.kwargs["timeout"], sync_upstream_github.REQUEST_TIMEOUT)

    def test_fetch_json_via_http_wraps_timeout(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("timed out")):
            with self.assertRaisesRegex(RuntimeError, "timed out after"):
                sync_upstream_github._fetch_json_via_http("https://api.github.com/repos/test/repo/issues")

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

    def test_parallel_ordered_map_preserves_input_order(self):
        items = [1, 2, 3, 4]

        results = sync_upstream_github.parallel_ordered_map(
            items,
            lambda item: {"item": item, "square": item * item},
            max_workers=3,
        )

        self.assertEqual(
            results,
            [
                {"item": 1, "square": 1},
                {"item": 2, "square": 4},
                {"item": 3, "square": 9},
                {"item": 4, "square": 16},
            ],
        )

    def test_hydrate_pull_requests_fetches_detail_payloads(self):
        with patch.object(
            sync_upstream_github,
            "github_api",
            side_effect=[
                {"number": 101, "mergeable_state": "clean"},
                {"number": 102, "mergeable_state": "dirty"},
            ],
        ) as mocked:
            payload = sync_upstream_github.hydrate_pull_requests(
                "test-owner",
                "test-repo",
                [{"number": 101}, {"number": 102}],
                max_workers=2,
            )

        self.assertEqual(
            payload,
            [
                {"number": 101, "mergeable_state": "clean"},
                {"number": 102, "mergeable_state": "dirty"},
            ],
        )
        self.assertEqual(mocked.call_args_list[0].args, ("/repos/test-owner/test-repo/pulls/101", {}))
        self.assertEqual(mocked.call_args_list[1].args, ("/repos/test-owner/test-repo/pulls/102", {}))

    def test_compact_helpers_delegate_parallel_work_with_requested_worker_cap(self):
        issue_items = [{"number": 1}, {"number": 2}]
        pr_items = [{"number": 101}, {"number": 102}]

        with (
            patch.object(
                sync_upstream_github,
                "parallel_ordered_map",
                side_effect=[
                    [{"number": 1, "kind": "issue"}, {"number": 2, "kind": "issue"}],
                    [{"number": 101, "kind": "pr"}, {"number": 102, "kind": "pr"}],
                    [{"number": 101, "title": "PR 101"}, {"number": 102, "title": "PR 102"}],
                ],
            ) as mocked_parallel,
            patch.object(sync_upstream_github, "compact_pr", side_effect=lambda item, mirrored, remote: item),
        ):
            issues = sync_upstream_github.compact_issues(issue_items, max_workers=5)
            hydrated = sync_upstream_github.hydrate_pull_requests(
                "test-owner",
                "test-repo",
                pr_items,
                max_workers=4,
            )
            prs = sync_upstream_github.compact_pull_requests(
                hydrated,
                mirrored_pr_numbers={101},
                fork_remote="origin",
                max_workers=3,
            )

        self.assertEqual(issues, [{"number": 1, "kind": "issue"}, {"number": 2, "kind": "issue"}])
        self.assertEqual(hydrated, [{"number": 101, "kind": "pr"}, {"number": 102, "kind": "pr"}])
        self.assertEqual(prs, [{"number": 101, "title": "PR 101"}, {"number": 102, "title": "PR 102"}])
        self.assertEqual(mocked_parallel.call_args_list[0].kwargs["max_workers"], 5)
        self.assertEqual(mocked_parallel.call_args_list[1].kwargs["max_workers"], 4)
        self.assertEqual(mocked_parallel.call_args_list[2].kwargs["max_workers"], 3)

    def test_compact_records_include_state_fields(self):
        with patch.object(
            sync_upstream_github,
            "fetch_recent_comments",
            side_effect=[
                [{"author": "carol", "body_excerpt": "issue comment"}],
                [{"author": "dave", "body_excerpt": "pr comment"}],
            ],
        ):
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
                    "body": "Issue body",
                    "comments": 1,
                    "comments_url": "https://api.github.com/repos/test/repo/issues/10/comments",
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
                    "head": {
                        "ref": "feature",
                        "sha": "abc123",
                        "repo": {
                            "full_name": "contrib/test-repo",
                            "clone_url": "https://github.com/contrib/test-repo.git",
                        },
                    },
                    "base": {
                        "ref": "main",
                        "repo": {"full_name": "test-owner/test-repo"},
                    },
                    "draft": False,
                    "mergeable_state": "clean",
                    "labels": [{"name": "enhancement"}],
                    "user": {"login": "bob"},
                    "body": "PR body",
                    "comments": 1,
                    "comments_url": "https://api.github.com/repos/test/repo/issues/11/comments",
                    "review_comments": 2,
                },
                mirrored_pr_numbers={11},
                fork_remote="origin",
            )

        self.assertEqual(issue["state"], "closed")
        self.assertEqual(issue["closed_at"], "2026-01-03T00:00:00Z")
        self.assertEqual(issue["body_excerpt"], "Issue body")
        self.assertEqual(issue["comment_count"], 1)
        self.assertEqual(issue["recent_comments"], [{"author": "carol", "body_excerpt": "issue comment"}])
        self.assertEqual(pr["state"], "closed")
        self.assertEqual(pr["merged_at"], "2026-01-03T00:00:01Z")
        self.assertEqual(pr["head"], "feature")
        self.assertEqual(pr["head_sha"], "abc123")
        self.assertEqual(pr["head_repo"], "contrib/test-repo")
        self.assertEqual(pr["head_clone_url"], "https://github.com/contrib/test-repo.git")
        self.assertEqual(pr["base"], "main")
        self.assertEqual(pr["base_repo"], "test-owner/test-repo")
        self.assertEqual(pr["mergeable_state"], "clean")
        self.assertEqual(pr["labels"], ["enhancement"])
        self.assertEqual(pr["body_excerpt"], "PR body")
        self.assertEqual(pr["comment_count"], 1)
        self.assertEqual(pr["review_comment_count"], 2)
        self.assertEqual(pr["recent_comments"], [{"author": "dave", "body_excerpt": "pr comment"}])
        self.assertTrue(pr["fork_mirrored"])
        self.assertEqual(pr["fork_mirror_ref"], "origin/mirror/upstream-pr-11")


if __name__ == "__main__":
    unittest.main()
