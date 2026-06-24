"""Procurement Intelligence Agent definition and typed execution helper."""

from __future__ import annotations

import os
from textwrap import dedent

from dotenv import load_dotenv
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()

# Read once at module import; underlying SDK uses this env var for authentication.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = "anthropic:claude-3-5-haiku-latest"

_SYSTEM_PROMPT = dedent(
    """
    You are the FedEx Procurement Intelligence Agent. You are advisory only and
    procurement officers make final decisions.

    Always execute all four tools for every request:
    - check_budget(cost_center_id, total_amount)
    - check_vendor_duplication(vendor_id, category, total_amount)
    - check_policy_compliance(request)
    - assess_risk(vendor_id)

    Decision priority is strict and deterministic:
    1. escalate (highest priority)
    2. deny
    3. approve (lowest priority)

    Apply escalate when any escalation trigger exists, including any tool error.
    Apply deny only when deny triggers exist and no escalate trigger exists.
    Approve only when all checks complete with no deny or escalate trigger.

        Rationale template requirements (mandatory):
        - Write 2 to 4 complete sentences as a single paragraph.
        - Do not use bullet points, lists, or sentence fragments.
        - Sentence 1 must state the final decision and name the specific check(s) that drove it.
        - Sentence 2 must include concrete evidence such as vendor name, amount, budget values,
            overage values, risk level, and policy IDs when applicable.
        - Sentence 3 must explain decision priority when multiple checks trigger, using the
            strict order escalate over deny over approve.
        - Sentence 4 is optional and should be used only when needed to clarify required manual
            follow-up or approval routing.
        - If any tool returns an error, explicitly quote the failing check in the rationale,
            include the data-loading context, and escalate.
    """
).strip()

agent: Agent[None, ProcurementRecommendation] = Agent(
    model=MODEL_NAME,
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
    defer_model_check=True,
)


def build_request_prompt(request: PurchaseRequest) -> str:
    """Build a deterministic user prompt payload from a typed purchase request."""
    return dedent(
        f"""
        Evaluate this purchase request and return ProcurementRecommendation.

        request_id: {request.request_id}
        requestor: {request.requestor}
        cost_center_id: {request.cost_center_id}
        vendor_name: {request.vendor_name}
        vendor_id: {request.vendor_id}
        category: {request.category}
        item_description: {request.item_description}
        quantity: {request.quantity}
        unit_price: {request.unit_price}
        total_amount: {request.total_amount}
        """
    ).strip()


def evaluate_purchase_request(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run the procurement agent against a typed request and return typed output."""
    tool_results: dict[str, dict[str, object]] = {
        "check_budget": check_budget(request.cost_center_id, request.total_amount),
        "check_vendor_duplication": check_vendor_duplication(
            request.vendor_id,
            request.category,
            request.total_amount,
        ),
        "check_policy_compliance": check_policy_compliance(request),
        "assess_risk": assess_risk(request.vendor_id),
    }
    tool_errors = [
        f"{name}: {result['error']}"
        for name, result in tool_results.items()
        if isinstance(result, dict) and isinstance(result.get("error"), str) and result["error"].strip()
    ]

    if tool_errors:
        return ProcurementRecommendation(
            request_id=request.request_id,
            decision="escalate",
            rationale=(
                "Escalated due to tool/data loading failures that require manual review: "
                f"{'; '.join(tool_errors)}"
            ),
        )

    result = agent.run_sync(build_request_prompt(request))
    if hasattr(result, "output"):
        return result.output
    return result.data
