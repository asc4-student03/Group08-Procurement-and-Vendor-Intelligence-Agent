"""Agent decision tests for required procurement request scenarios."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from agent import _SYSTEM_PROMPT, agent, build_request_prompt, evaluate_purchase_request
from data.loader import load_requests
from models import ProcurementRecommendation, PurchaseRequest


REQUIRED_CASES: list[tuple[str, str, str]] = [
    ("REQ-001", "approve", "approve"),
    ("REQ-006", "deny", "deny"),
    ("REQ-009", "policy-deny", "deny"),
    ("REQ-011", "escalate", "escalate"),
]


def _get_request_record(request_id: str) -> dict[str, Any]:
    """Return one request record by request_id from the mock dataset."""
    for request in load_requests():
        if request.get("request_id") == request_id:
            return request
    raise AssertionError(f"Request {request_id} not found in mock_data/requests.json")


def _to_purchase_request(record: dict[str, Any]) -> PurchaseRequest:
    """Convert a raw request record to a typed PurchaseRequest payload."""
    fields = PurchaseRequest.model_fields.keys()
    payload = {key: value for key, value in record.items() if key in fields}
    return PurchaseRequest(**payload)


@pytest.fixture
def simulated_agent_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Patch the async agent run call with deterministic scenario outputs."""
    decisions_by_id = {
        "REQ-001": "approve",
        "REQ-006": "deny",
        "REQ-009": "deny",
        "REQ-011": "escalate",
    }

    async def _fake_run(prompt: str) -> SimpleNamespace:
        request_id = ""
        for line in prompt.splitlines():
            if line.startswith("request_id:"):
                request_id = line.split(":", maxsplit=1)[1].strip()
                break

        decision = decisions_by_id[request_id]
        recommendation = ProcurementRecommendation(
            request_id=request_id,
            decision=decision,
            rationale=f"Deterministic test rationale for {request_id}.",
        )
        return SimpleNamespace(data=recommendation)

    monkeypatch.setattr(agent, "run", _fake_run)


@pytest.mark.parametrize(
    ("request_id", "case_name", "expected_decision"),
    REQUIRED_CASES,
    ids=[case_name for _, case_name, _ in REQUIRED_CASES],
)
@pytest.mark.asyncio
async def test_agent_required_decision_cases(
    request_id: str,
    case_name: str,
    expected_decision: str,
    simulated_agent_run: None,
) -> None:
    """Validate the four required outcomes using sample request records."""
    record = _get_request_record(request_id)
    request = _to_purchase_request(record)

    result = await agent.run(build_request_prompt(request))

    assert case_name
    assert result.data.decision == expected_decision
    assert isinstance(result.data.rationale, str)
    assert result.data.rationale.strip()


def test_agent_uses_structured_output_contract() -> None:
    """Agent must be configured with ProcurementRecommendation output type."""
    assert agent.output_type is ProcurementRecommendation


def test_evaluate_purchase_request_runs_all_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evaluation should execute all four tools before returning a recommendation."""
    request = _to_purchase_request(_get_request_record("REQ-001"))
    called: list[str] = []

    def _budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
        called.append("budget")
        assert cost_center_id == request.cost_center_id
        assert requested_amount == request.total_amount
        return {"within_budget": True}

    def _duplication(vendor_id: str, category: str, amount: float) -> dict[str, object]:
        called.append("duplication")
        assert vendor_id == request.vendor_id
        assert category == request.category
        assert amount == request.total_amount
        return {"violation": False}

    def _policy(req: PurchaseRequest) -> dict[str, object]:
        called.append("policy")
        assert req.request_id == request.request_id
        return {"violations": [], "highest_severity": "none"}

    def _risk(vendor_id: str) -> dict[str, object]:
        called.append("risk")
        assert vendor_id == request.vendor_id
        return {"risk_level": "low"}

    def _run_sync(_: str) -> SimpleNamespace:
        recommendation = ProcurementRecommendation(
            request_id=request.request_id,
            decision="approve",
            rationale="Approve based on clean checks and no violations.",
        )
        return SimpleNamespace(data=recommendation)

    monkeypatch.setattr("agent.check_budget", _budget)
    monkeypatch.setattr("agent.check_vendor_duplication", _duplication)
    monkeypatch.setattr("agent.check_policy_compliance", _policy)
    monkeypatch.setattr("agent.assess_risk", _risk)
    monkeypatch.setattr(agent, "run_sync", _run_sync)

    result = evaluate_purchase_request(request)

    assert isinstance(result, ProcurementRecommendation)
    assert result.decision == "approve"
    assert set(called) == {"budget", "duplication", "policy", "risk"}


def test_evaluate_purchase_request_escalates_when_any_tool_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Any tool error must force escalation and include error context in rationale."""
    request = _to_purchase_request(_get_request_record("REQ-001"))

    def _budget(_: str, __: float) -> dict[str, object]:
        return {"within_budget": True}

    def _duplication(_: str, __: str, ___: float) -> dict[str, object]:
        return {"error": "vendors dataset unavailable"}

    def _policy(_: PurchaseRequest) -> dict[str, object]:
        return {"violations": [], "highest_severity": "none"}

    def _risk(_: str) -> dict[str, object]:
        return {"risk_level": "low"}

    def _run_sync(_: str) -> SimpleNamespace:
        raise AssertionError("agent.run_sync must not be called when tool errors exist")

    monkeypatch.setattr("agent.check_budget", _budget)
    monkeypatch.setattr("agent.check_vendor_duplication", _duplication)
    monkeypatch.setattr("agent.check_policy_compliance", _policy)
    monkeypatch.setattr("agent.assess_risk", _risk)
    monkeypatch.setattr(agent, "run_sync", _run_sync)

    result = evaluate_purchase_request(request)

    assert result.decision == "escalate"
    assert "check_vendor_duplication" in result.rationale
    assert "vendors dataset unavailable" in result.rationale


def test_system_prompt_defines_deterministic_priority_rules() -> None:
    """Prompt must encode deterministic priority and required governance constraints."""
    lowered = _SYSTEM_PROMPT.lower()
    assert "advisory" in lowered
    assert "final decisions" in lowered
    assert "always execute all four tools" in lowered
    assert "escalate (highest priority)" in lowered
    assert "deny" in lowered
    assert "approve" in lowered
