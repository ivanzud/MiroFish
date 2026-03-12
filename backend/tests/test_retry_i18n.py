from __future__ import annotations

from unittest.mock import Mock

import pytest
from flask import Flask

from app.utils import retry as retry_utils


def test_retry_with_backoff_logs_english_messages(monkeypatch):
    app = Flask(__name__)
    warning = Mock()
    error = Mock()

    monkeypatch.setattr(retry_utils.logger, "warning", warning)
    monkeypatch.setattr(retry_utils.logger, "error", error)
    monkeypatch.setattr(retry_utils.time, "sleep", lambda _: None)
    monkeypatch.setattr(retry_utils.random, "random", lambda: 0.0)

    attempts = {"count": 0}

    @retry_utils.retry_with_backoff(max_retries=1, initial_delay=1.0)
    def flaky():
        attempts["count"] += 1
        raise ValueError("boom")

    with app.test_request_context(headers={"X-Locale": "en"}):
        with pytest.raises(ValueError, match="boom"):
            flaky()

    warning.assert_called_once_with(
        "Function flaky failed on attempt 1: boom, retrying in 0.5s..."
    )
    error.assert_called_once_with(
        "Function flaky still failed after 1 retries: boom"
    )


@pytest.mark.asyncio
async def test_retry_with_backoff_async_logs_english_messages(monkeypatch):
    app = Flask(__name__)
    warning = Mock()
    error = Mock()
    sleep_calls: list[float] = []

    monkeypatch.setattr(retry_utils.logger, "warning", warning)
    monkeypatch.setattr(retry_utils.logger, "error", error)
    monkeypatch.setattr(retry_utils.random, "random", lambda: 0.0)

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    attempts = {"count": 0}

    @retry_utils.retry_with_backoff_async(max_retries=1, initial_delay=1.0)
    async def flaky_async():
        attempts["count"] += 1
        raise RuntimeError("async boom")

    with app.test_request_context(headers={"X-Locale": "en"}):
        monkeypatch.setattr("asyncio.sleep", fake_sleep)
        with pytest.raises(RuntimeError, match="async boom"):
            await flaky_async()

    assert sleep_calls == [0.5]
    warning.assert_called_once_with(
        "Async function flaky_async failed on attempt 1: async boom, retrying in 0.5s..."
    )
    error.assert_called_once_with(
        "Async function flaky_async still failed after 1 retries: async boom"
    )


def test_retryable_api_client_logs_english_messages(monkeypatch):
    app = Flask(__name__)
    warning = Mock()
    error = Mock()

    monkeypatch.setattr(retry_utils.logger, "warning", warning)
    monkeypatch.setattr(retry_utils.logger, "error", error)
    monkeypatch.setattr(retry_utils.time, "sleep", lambda _: None)
    monkeypatch.setattr(retry_utils.random, "random", lambda: 0.0)

    client = retry_utils.RetryableAPIClient(max_retries=1, initial_delay=1.0)

    attempts = {"count": 0}

    def flaky_call() -> None:
        attempts["count"] += 1
        raise LookupError("api boom")

    with app.test_request_context(headers={"X-Locale": "en"}):
        with pytest.raises(LookupError, match="api boom"):
            client.call_with_retry(flaky_call)

    warning.assert_called_once_with(
        "API call failed on attempt 1: api boom, retrying in 0.5s..."
    )
    error.assert_called_once_with(
        "API call still failed after 1 retries: api boom"
    )


def test_retryable_api_client_batch_logs_english_item_failures(monkeypatch):
    app = Flask(__name__)
    error = Mock()

    monkeypatch.setattr(retry_utils.logger, "error", error)

    client = retry_utils.RetryableAPIClient(max_retries=0)

    def process(item: int) -> int:
        if item == 2:
            raise ValueError("bad item")
        return item * 10

    with app.test_request_context(headers={"X-Locale": "en"}):
        results, failures = client.call_batch_with_retry([1, 2], process)

    assert results == [10]
    assert failures == [{"index": 1, "item": 2, "error": "bad item"}]
    assert error.call_args_list == [
        (( "API call still failed after 0 retries: bad item",), {}),
        (( "Failed to process item 2: bad item",), {}),
    ]
