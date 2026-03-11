#!/usr/bin/env python3
"""Print the backend config validation/summary without starting the server."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import Config


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
