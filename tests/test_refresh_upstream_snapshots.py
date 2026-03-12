import json
import os
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


class RefreshUpstreamSnapshotsTests(unittest.TestCase):
    def _write_fake_sync_script(self, path: Path) -> None:
        path.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                import json
                import os
                import sys

                log_path = os.environ["SYNC_LOG_PATH"]
                with open(log_path, "a", encoding="utf-8") as handle:
                    handle.write(json.dumps(sys.argv[1:]) + "\\n")
                """
            ),
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IEXEC)

    def _run_wrapper(self, *args: str) -> list[list[str]]:
        wrapper_source = (
            Path(__file__).resolve().parents[1] / "scripts" / "refresh_upstream_snapshots.sh"
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            scripts_dir = tmp_path / "scripts"
            docs_dir = tmp_path / "docs"
            scripts_dir.mkdir()
            docs_dir.mkdir()

            wrapper_copy = scripts_dir / "refresh_upstream_snapshots.sh"
            shutil.copy2(wrapper_source, wrapper_copy)

            fake_sync = scripts_dir / "sync_upstream_github.py"
            self._write_fake_sync_script(fake_sync)

            log_path = tmp_path / "sync-log.jsonl"
            env = os.environ.copy()
            env["SYNC_LOG_PATH"] = str(log_path)

            subprocess.run(
                ["bash", str(wrapper_copy), *args],
                cwd=tmp_path,
                env=env,
                check=True,
            )

            return [
                json.loads(line)
                for line in log_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

    def test_force_refresh_keeps_default_repo_and_disables_stale_cache(self):
        calls = self._run_wrapper("--force-refresh")

        self.assertEqual(len(calls), 2)
        for call in calls:
            self.assertIn("--repo", call)
            self.assertEqual(call[call.index("--repo") + 1], "666ghj/MiroFish")
            self.assertIn("--stale-cache-hours", call)
            self.assertEqual(call[call.index("--stale-cache-hours") + 1], "-1")

    def test_positional_repo_and_timeout_are_forwarded(self):
        calls = self._run_wrapper("example/MiroFish", "--timeout", "22")

        self.assertEqual(len(calls), 2)
        for call in calls:
            self.assertEqual(call[call.index("--repo") + 1], "example/MiroFish")
            self.assertEqual(call[call.index("--timeout") + 1], "22")

    def test_fork_mirror_overrides_are_forwarded(self):
        calls = self._run_wrapper(
            "--fork-remote",
            "upstream-fork",
            "--mirror-issues-repo",
            "example/fork",
        )

        self.assertEqual(len(calls), 2)
        for call in calls:
            self.assertEqual(call[call.index("--fork-remote") + 1], "upstream-fork")
            self.assertEqual(call[call.index("--mirror-issues-repo") + 1], "example/fork")


if __name__ == "__main__":
    unittest.main()
