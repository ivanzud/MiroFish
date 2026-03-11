import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SimulationCliHelpTests(unittest.TestCase):
    def _run_help(self, relative_path: str) -> subprocess.CompletedProcess[str]:
        script_path = ROOT / relative_path
        env = os.environ.copy()
        env["MIROFISH_LOCALE"] = "en"
        return subprocess.run(
            [sys.executable, str(script_path), "--help"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_reddit_help_is_available_without_optional_runtime_dependencies(self):
        result = self._run_help("backend/scripts/run_reddit_simulation.py")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OASIS Reddit simulation", result.stdout)
        self.assertIn("Path to the configuration file", result.stdout)
        self.assertNotIn("missing dependency", result.stdout.lower())
        self.assertNotIn("Simulation process exited", result.stdout)

    def test_twitter_help_is_available_without_optional_runtime_dependencies(self):
        result = self._run_help("backend/scripts/run_twitter_simulation.py")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OASIS Twitter simulation", result.stdout)
        self.assertIn("Maximum simulation rounds", result.stdout)
        self.assertNotIn("missing dependency", result.stdout.lower())
        self.assertNotIn("Simulation process exited", result.stdout)

    def test_parallel_help_is_available_without_optional_runtime_dependencies(self):
        result = self._run_help("backend/scripts/run_parallel_simulation.py")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OASIS dual-platform parallel simulation", result.stdout)
        self.assertIn("Run only the Reddit simulation", result.stdout)
        self.assertNotIn("missing dependency", result.stdout.lower())
        self.assertNotIn("Simulation process exited", result.stdout)


if __name__ == "__main__":
    unittest.main()
