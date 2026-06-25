from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from agent import run_request_async
from data.loader import load_requests
from models import PurchaseRequest


def _request_record_by_id(request_id: str) -> dict[str, Any]:
    record = next(
        (item for item in load_requests() if item.get("request_id") == request_id),
        None,
    )
    if record is None:
        raise AssertionError(f"Request not found in mock_data/requests.json: {request_id}")
    return record


def _request_by_id(request_id: str) -> PurchaseRequest:
    return PurchaseRequest(**_request_record_by_id(request_id))


async def _run_agent(request: PurchaseRequest) -> SimpleNamespace:
    recommendation = await run_request_async(request)
    return SimpleNamespace(data=recommendation)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_id", ["REQ-006", "REQ-007", "REQ-008", "REQ-009"])
async def test_deny_requests_match_expected_outcome(request_id: str) -> None:
    record = _request_record_by_id(request_id)
    request = PurchaseRequest(**record)
    result = await _run_agent(request)

    assert result.data.decision == str(record["expected_outcome"])
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
@pytest.mark.parametrize("request_id", ["REQ-010", "REQ-011"])
async def test_escalate_requests_match_expected_outcome(request_id: str) -> None:
    record = _request_record_by_id(request_id)
    request = PurchaseRequest(**record)
    result = await _run_agent(request)

    assert result.data.decision == str(record["expected_outcome"])
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
@pytest.mark.parametrize("request_id", ["REQ-001", "REQ-002", "REQ-003"])
async def test_approve_requests_match_expected_outcome(request_id: str) -> None:
    record = _request_record_by_id(request_id)
    request = PurchaseRequest(**record)
    result = await _run_agent(request)

    assert result.data.decision == str(record["expected_outcome"])
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
