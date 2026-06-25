from __future__ import annotations

from unittest.mock import patch

from agent import run_request_sync
from models import PurchaseRequest


def _base_request(**overrides: object) -> PurchaseRequest:
    payload: dict[str, object] = {
        "request_id": "REQ-ERR-BASE",
        "requestor": "qa@fedex.com",
        "cost_center_id": "CC-001",
        "vendor_name": "BlueSky Cloud Solutions",
        "vendor_id": "V-002",
        "category": "software_licenses",
        "item_description": "Error path validation request",
        "quantity": 1,
        "unit_price": 100.0,
        "total_amount": 100.0,
    }
    payload.update(overrides)
    return PurchaseRequest(**payload)


def test_agent_returns_recommendation_when_budget_loader_raises_runtime_error() -> None:
    request = _base_request(request_id="REQ-ERR-001")

    with patch("data.loader.load_budgets", side_effect=RuntimeError("budget backend unavailable")):
        recommendation = run_request_sync(request)

    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert "runtimeerror" in recommendation.rationale.lower()
    assert "check_budget" in recommendation.rationale


def test_agent_escalates_for_unknown_vendor_with_failure_rationale() -> None:
    request = _base_request(
        request_id="REQ-ERR-002",
        vendor_name="Unknown Vendor",
        vendor_id="V-999",
    )

    recommendation = run_request_sync(request)

    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert "unknown vendor" in recommendation.rationale.lower()
