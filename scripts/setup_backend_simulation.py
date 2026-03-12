#!/usr/bin/env python3
"""Install optional backend simulation dependencies with environment checks."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


SUPPORTED_MAX_PYTHON = (3, 12)


def python_version_label(version_info: tuple[int, int]) -> str:
    """Return a compact major.minor version string."""
    return f"{version_info[0]}.{version_info[1]}"


def validate_environment(
    version_info: tuple[int, int] | None = None,
    rustc_available: bool | None = None,
) -> str | None:
    """Return an actionable validation error, or None when installation can proceed."""
    version_info = version_info or (sys.version_info.major, sys.version_info.minor)

    if version_info <= SUPPORTED_MAX_PYTHON:
        return None

    if rustc_available is None:
        rustc_available = shutil.which("rustc") is not None

    if rustc_available:
        return None

    return (
        "Optional simulation dependencies are not supported out-of-the-box on "
        f"Python {python_version_label(version_info)} without Rust. "
        "The current camel-ai -> tiktoken dependency chain falls back to a source "
        "build on Python 3.13+. Use Python 3.11/3.12 for Step 3 / Step 5 simulation "
        "setup, or install a Rust toolchain and rerun this command."
    )


def main() -> int:
    error = validate_environment()
    if error:
        print(error, file=sys.stderr)
        return 1

    backend_dir = Path(__file__).resolve().parent.parent / "backend"
    result = subprocess.run(
        ["uv", "sync", "--extra", "simulation"],
        cwd=backend_dir,
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
