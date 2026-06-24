from __future__ import annotations

from agent import run_request_from_dict_sync
from agent import run_request_sync
from agent import agent as procurement_agent
from models import PurchaseRequest


def _valid_request() -> PurchaseRequest:
    return PurchaseRequest(
        request_id="REQ-TEST-001",
        requestor="qa@fedex.com",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Validation request",
        quantity=1,
        unit_price=100.0,
        total_amount=100.0,
    )


def test_invalid_input_returns_escalate_with_validation_context() -> None:
    recommendation = run_request_from_dict_sync(
        {
            "request_id": "REQ-BAD-001",
            "requestor": "qa@fedex.com",
            "cost_center_id": "CC-001",
            "vendor_name": "BlueSky Cloud Solutions",
            "vendor_id": "V-002",
            "category": "software_licenses",
            "item_description": "Bad payload",
            "quantity": 1,
            "unit_price": 10.0,
            "total_amount": 999.0,
        }
    )

    assert recommendation.decision == "escalate"
    assert "validation failed" in recommendation.rationale.lower()


def test_precedence_escalate_over_deny(monkeypatch) -> None:
    request = _valid_request()

    def _fake_collect(_request: PurchaseRequest) -> dict[str, dict[str, object]]:
        return {
            "check_budget": {"signal": "deny", "summary": "budget deny", "details": {}},
            "check_vendor_duplication": {
                "signal": "approve",
                "summary": "ok",
                "details": {},
            },
            "check_policy_compliance": {
                "signal": "escalate",
                "summary": "policy escalate",
                "details": {"violations": []},
            },
            "assess_risk": {
                "vendor_id": "V-002",
                "vendor_name": "BlueSky Cloud Solutions",
                "compliance_flag": False,
                "contract_status": "active",
                "risk_level": "low",
                "risk_summary": "ok",
            },
        }

    def _raise_model_error(_: str) -> object:
        raise RuntimeError("model unavailable")

    monkeypatch.setattr("agent._collect_tool_outputs", _fake_collect)
    monkeypatch.setattr(procurement_agent, "run_sync", _raise_model_error)

    recommendation = run_request_sync(request)

    assert recommendation.decision == "escalate"


def test_decision_enum_never_ambiguous(monkeypatch) -> None:
    request = _valid_request()

    def _raise_model_error(_: str) -> object:
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(procurement_agent, "run_sync", _raise_model_error)
    recommendation = run_request_sync(request)

    assert recommendation.decision in {"approve", "deny", "escalate"}


def test_all_tools_fail_returns_escalate(monkeypatch) -> None:
    request = _valid_request()

    def _fail_collect(_request: PurchaseRequest) -> dict[str, dict[str, object]]:
        return {
            "check_budget": {
                "signal": "escalate",
                "summary": "fail",
                "details": {},
                "error": {"type": "FileNotFoundError", "message": "missing", "stage": "data_load"},
            },
            "check_vendor_duplication": {
                "signal": "escalate",
                "summary": "fail",
                "details": {},
                "error": {"type": "Exception", "message": "bad", "stage": "unexpected"},
            },
            "check_policy_compliance": {
                "signal": "escalate",
                "summary": "fail",
                "details": {"violations": []},
                "error": {"type": "Exception", "message": "bad", "stage": "unexpected"},
            },
            "assess_risk": {
                "vendor_id": "V-002",
                "vendor_name": "BlueSky Cloud Solutions",
                "compliance_flag": False,
                "contract_status": "unknown",
                "risk_level": "critical",
                "risk_summary": "fail",
                "error": {"type": "Exception", "message": "bad", "stage": "unexpected"},
            },
        }

    def _unexpected(_: str) -> object:
        raise AssertionError("Model should not be called when all tools fail")

    monkeypatch.setattr("agent._collect_tool_outputs", _fail_collect)
    monkeypatch.setattr(procurement_agent, "run_sync", _unexpected)

    recommendation = run_request_sync(request)

    assert recommendation.decision == "escalate"
    assert "tool error" in recommendation.rationale.lower()
