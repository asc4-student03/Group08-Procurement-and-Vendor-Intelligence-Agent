from __future__ import annotations

from types import SimpleNamespace

import pytest

from agent import run_request_async
from data.loader import load_requests
from models import PurchaseRequest


EXPECTED_DECISIONS = {
    "REQ-001": "approve",
    "REQ-006": "deny",
    "REQ-009": "deny",
    "REQ-011": "escalate",
}


def _request_by_id(request_id: str) -> PurchaseRequest:
    record = next(
        (item for item in load_requests() if item.get("request_id") == request_id),
        None,
    )
    if record is None:
        raise AssertionError(f"Request not found in mock_data/requests.json: {request_id}")
    return PurchaseRequest(**record)


async def _run_agent(request: PurchaseRequest) -> SimpleNamespace:
    recommendation = await run_request_async(request)
    return SimpleNamespace(data=recommendation)


@pytest.mark.asyncio
async def test_req_001_approve() -> None:
    request = _request_by_id("REQ-001")
    result = await _run_agent(request)

    assert result.data.decision == EXPECTED_DECISIONS["REQ-001"]
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_req_006_budget_overage_deny() -> None:
    request = _request_by_id("REQ-006")
    result = await _run_agent(request)

    assert result.data.decision == EXPECTED_DECISIONS["REQ-006"]
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_req_009_policy_deny() -> None:
    request = _request_by_id("REQ-009")
    result = await _run_agent(request)

    assert result.data.decision == EXPECTED_DECISIONS["REQ-009"]
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


@pytest.mark.asyncio
async def test_req_011_escalate() -> None:
    request = _request_by_id("REQ-011")
    result = await _run_agent(request)

    assert result.data.decision == EXPECTED_DECISIONS["REQ-011"]
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()
