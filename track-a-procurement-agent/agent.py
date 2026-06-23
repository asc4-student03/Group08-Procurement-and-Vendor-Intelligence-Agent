"""Pydantic AI wiring for the procurement intelligence agent."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()

_SYSTEM_PROMPT = """
You are a procurement pre-screening agent.

For each request, call all four tools:
- check_budget(cost_center_id, requested_amount)
- check_vendor_duplication(vendor_id, category, requested_amount)
- check_policy_compliance(request)
- assess_risk(vendor_id, category, requested_amount, cost_center_id)

Final decision priority is strict: escalate > deny > approve.
Always return a ProcurementRecommendation with decision in {approve, deny, escalate}
and a non-empty rationale that references the decisive checks.
If any tool returns an error, escalate and include the error context in rationale.
"""

agent: Agent[None, ProcurementRecommendation] = Agent(
    model=os.getenv("PROCUREMENT_AGENT_MODEL", "anthropic:claude-3-5-haiku-latest"),
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)


def run_request_sync(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run the Pydantic AI agent for a validated purchase request."""
    result = agent.run_sync(request.model_dump_json())
    return result.data


def run_request_local(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run a deterministic local evaluation using all four tools.

    This fallback is useful for manual validation when model API credentials
    are unavailable. It preserves the same output schema and decision
    precedence as the agent prompt.
    """
    budget_result = check_budget(request.cost_center_id, request.total_amount)
    vendor_result = check_vendor_duplication(
        request.vendor_id,
        request.category,
        request.total_amount,
    )
    policy_result = check_policy_compliance(request)
    risk_result = assess_risk(
        request.vendor_id,
        request.category,
        request.total_amount,
        request.cost_center_id,
    )

    tool_results = {
        "budget": budget_result,
        "vendor_duplication": vendor_result,
        "policy_compliance": policy_result,
        "risk_assessment": risk_result,
    }

    has_error = any("error" in result for result in tool_results.values())
    signals = {str(result.get("signal", "approve")) for result in tool_results.values()}

    if has_error or "escalate" in signals:
        decision = "escalate"
    elif "deny" in signals:
        decision = "deny"
    else:
        decision = "approve"

    rationale_parts = [
        f"budget={budget_result.get('signal', 'unknown')} ({budget_result.get('summary', '')})",
        "vendor_duplication="
        f"{vendor_result.get('signal', 'unknown')} ({vendor_result.get('summary', '')})",
        "policy_compliance="
        f"{policy_result.get('signal', 'unknown')} ({policy_result.get('summary', '')})",
        f"risk={risk_result.get('signal', 'unknown')} ({risk_result.get('summary', '')})",
    ]
    if has_error:
        errors = [
            f"{name}: {result['error']}"
            for name, result in tool_results.items()
            if "error" in result
        ]
        rationale_parts.append("errors=" + "; ".join(errors))

    rationale = " | ".join(rationale_parts)

    return ProcurementRecommendation(decision=decision, rationale=rationale)
