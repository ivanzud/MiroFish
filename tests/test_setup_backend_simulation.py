import unittest

from scripts.setup_backend_simulation import validate_environment


class ValidateEnvironmentTests(unittest.TestCase):
    def test_allows_python_312_without_rust(self):
        self.assertIsNone(validate_environment(version_info=(3, 12), rustc_available=False))

    def test_blocks_python_313_without_rust(self):
        error = validate_environment(version_info=(3, 13), rustc_available=False)
        self.assertIsNotNone(error)
        self.assertIn("Python 3.13", error)
        self.assertIn("Rust", error)

    def test_allows_python_313_with_rust(self):
        self.assertIsNone(validate_environment(version_info=(3, 13), rustc_available=True))


if __name__ == "__main__":
    unittest.main()
