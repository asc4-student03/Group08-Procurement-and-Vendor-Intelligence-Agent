"""Agent-level error handling tests."""

from __future__ import annotations

from agent import agent as procurement_agent
from agent import run_request_sync
from data import loader
from models import PurchaseRequest


def test_agent_escalates_on_budget_data_load_failure(monkeypatch) -> None:
    """Missing budget data should produce escalate with explicit failure rationale."""

    def _raise_file_not_found() -> list[dict[str, object]]:
        raise FileNotFoundError("mock_data/budgets.json is missing")

    llm_called = {"value": False}

    def _unexpected_model_call(_: str) -> object:
        llm_called["value"] = True
        raise AssertionError("LLM should not be called when preflight tool errors exist")

    monkeypatch.setattr(loader, "load_budgets", _raise_file_not_found)
    monkeypatch.setattr(procurement_agent, "run_sync", _unexpected_model_call)

    request = PurchaseRequest(
        request_id="REQ-ERR-001",
        requestor="qa@fedex.com",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Error handling validation purchase",
        quantity=1,
        unit_price=100.0,
        total_amount=100.0,
    )

    recommendation = run_request_sync(request)

    assert recommendation.decision == "escalate"
    assert recommendation.rationale.strip()
    assert "data loading" in recommendation.rationale.lower()
    assert "check_budget" in recommendation.rationale
    assert "FileNotFoundError" in recommendation.rationale
    assert llm_called["value"] is False
