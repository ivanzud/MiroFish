#!/usr/bin/env python3
"""Print the backend config validation/summary without starting the server."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BACKEND_DIR / "app"
SCRIPT_APP_PACKAGE = "_mirofish_script_app"


def load_config_class():
    """Load app.config without executing app/__init__.py and its Flask imports."""
    package = sys.modules.get(SCRIPT_APP_PACKAGE)
    if package is None:
        package = types.ModuleType(SCRIPT_APP_PACKAGE)
        package.__path__ = [str(APP_DIR)]
        sys.modules[SCRIPT_APP_PACKAGE] = package

    config_module_name = f"{SCRIPT_APP_PACKAGE}.config"
    config_module = sys.modules.get(config_module_name)
    if config_module is None:
        spec = importlib.util.spec_from_file_location(config_module_name, APP_DIR / "config.py")
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load config module from {APP_DIR / 'config.py'}")
        config_module = importlib.util.module_from_spec(spec)
        sys.modules[config_module_name] = config_module
        spec.loader.exec_module(config_module)

    return config_module.Config


Config = load_config_class()


def build_payload(locale: str) -> dict[str, object]:
    validation = Config.validate_comprehensive(locale=locale)
    return {
        "success": validation.is_valid,
        "data": {
            "validation": validation.to_dict(),
            "summary": Config.get_config_summary(),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the backend config-status payload as JSON.",
    )
    parser.add_argument(
        "--locale",
        choices=("zh", "en"),
        default="zh",
        help="Validation message locale.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact single-line JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload(args.locale)
    json.dump(
        payload,
        sys.stdout,
        ensure_ascii=False,
        indent=None if args.compact else 2,
        sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0 if payload["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
