"""
Shared API error handling helpers.
"""

from __future__ import annotations

import traceback
from typing import Optional

from flask import jsonify

from ..config import Config


def error_response(
    message: str,
    status_code: int = 500,
    *,
    include_traceback: Optional[bool] = None,
    original_error: Optional[Exception] = None,
):
    """Build a consistent JSON error response without leaking tracebacks by default."""
    payload = {
        "success": False,
        "error": message,
    }

    if include_traceback is None:
        include_traceback = Config.DEBUG

    if include_traceback and original_error is not None:
        payload["traceback"] = traceback.format_exc()

    return jsonify(payload), status_code


def log_error(logger, error: Exception, context: str = "") -> None:
    """Log the user-facing context plus the full traceback to server logs."""
    message = f"{context}: {error}" if context else str(error)
    logger.error(message)
    logger.debug(traceback.format_exc())


def handle_api_exception(logger, error: Exception, context: str = ""):
    """Log an exception and return the standard API error payload."""
    log_error(logger, error, context)
    return error_response(str(error), 500, original_error=error)
