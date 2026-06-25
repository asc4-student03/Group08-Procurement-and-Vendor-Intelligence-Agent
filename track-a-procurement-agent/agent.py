"""Pydantic AI agent definition for procurement recommendations."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from pydantic import ValidationError
from pydantic_ai import Agent

from models import ProcurementRecommendation, PurchaseRequest
from tools.budget import check_budget
from tools.policy_compliance import check_policy_compliance
from tools.risk_assessment import assess_risk
from tools.vendor_duplication import check_vendor_duplication

load_dotenv()
_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

_SYSTEM_PROMPT = """
You are the FedEx Procurement Intelligence Agent.

For every request, call all four tools exactly once:
- check_budget(cost_center_id, requested_amount)
- check_vendor_duplication(vendor_id, category, requested_amount)
- check_policy_compliance(request)
- assess_risk(vendor_id)

Final decision priority is strict: escalate > deny > approve.

Decision policy:
- If any tool reports an error, final decision MUST be escalate.
- When a tool reports an error, rationale MUST explicitly include the tool name and
    the error type/message from the tool payload.
- If any tool indicates escalate and none report errors, final decision MUST be escalate.
- Else if any tool indicates deny, final decision MUST be deny.
- Else final decision MUST be approve.

Output contract:
- Return ProcurementRecommendation only.
- decision MUST be one of approve, deny, escalate.
- rationale MUST be non-empty and include concrete check evidence.
- Rationale MUST mention tool error context when any tool fails.

Rationale template requirements:
- Write rationale as 2 to 4 complete sentences. Do not use bullet points.
- Name the specific check(s) that drove the decision by tool name
    (check_budget, check_vendor_duplication, check_policy_compliance, assess_risk).
- Include concrete context such as relevant amounts, vendor name, and policy IDs.
- For escalate decisions, clearly state why manual review is required.
"""

agent: Agent[None, ProcurementRecommendation] = Agent(
    model=os.getenv("PROCUREMENT_AGENT_MODEL", "anthropic:claude-3-5-haiku-latest"),
    output_type=ProcurementRecommendation,
    system_prompt=_SYSTEM_PROMPT,
    tools=[check_budget, check_vendor_duplication, check_policy_compliance, assess_risk],
)


def _should_skip_model_call() -> bool:
    """Return True when execution should avoid external LLM calls.

    Tests must run fully offline under RAPID behavioral scope controls.
    This check also supports an explicit runtime override.
    """
    force_offline = os.getenv("PROCUREMENT_AGENT_FORCE_OFFLINE", "").strip().lower()
    if force_offline in {"1", "true", "yes", "on"}:
        return True
    return os.getenv("PYTEST_CURRENT_TEST") is not None


def _normalize_tool_error(error_value: object) -> str:
    """Convert tool error payloads into a consistent rationale fragment."""
    if isinstance(error_value, dict):
        error_type = str(error_value.get("type", "UnknownError"))
        message = str(error_value.get("message", ""))
        stage = str(error_value.get("stage", "unknown"))
        return f"{error_type} (stage={stage}): {message}"
    return str(error_value)


def _collect_tool_outputs(request: PurchaseRequest) -> dict[str, dict[str, Any]]:
    """Run all required tools once and return their outputs by tool name."""
    return {
        "check_budget": check_budget(request.cost_center_id, request.total_amount),
        "check_vendor_duplication": check_vendor_duplication(
            request.vendor_id,
            request.category,
            request.total_amount,
        ),
        "check_policy_compliance": check_policy_compliance(request),
        "assess_risk": assess_risk(request.vendor_id),
    }


def _fallback_decision(tool_outputs: dict[str, dict[str, Any]]) -> str:
    """Apply decision priority from tool outputs without relying on model generation."""
    has_tool_error = any(output.get("error") for output in tool_outputs.values())
    if has_tool_error:
        return "escalate"

    budget_signal = str(tool_outputs["check_budget"].get("signal", "approve"))
    duplication_signal = str(tool_outputs["check_vendor_duplication"].get("signal", "approve"))
    policy_signal = str(tool_outputs["check_policy_compliance"].get("signal", "approve"))
    risk_level = str(tool_outputs["assess_risk"].get("risk_level", "low"))

    if "escalate" in {budget_signal, duplication_signal, policy_signal} or risk_level == "critical":
        return "escalate"
    if "deny" in {budget_signal, duplication_signal, policy_signal}:
        return "deny"
    return "approve"


def _fallback_rationale(
    request: PurchaseRequest,
    tool_outputs: dict[str, dict[str, Any]],
    decision: str,
    model_error: Exception | None = None,
) -> str:
    """Build a 2-4 sentence rationale using concrete tool evidence."""
    vendor_display = request.vendor_name.replace(".", "")
    budget = tool_outputs["check_budget"]
    duplication = tool_outputs["check_vendor_duplication"]
    policy = tool_outputs["check_policy_compliance"]
    risk = tool_outputs["assess_risk"]

    failures: list[str] = []
    for tool_name, output in tool_outputs.items():
        if output.get("error"):
            failures.append(f"{tool_name} reported {_normalize_tool_error(output['error'])}")

    if failures:
        first_sentence = (
            f"I recommend escalate for {request.request_id} because tool data loading or "
            "validation errors were detected in the required checks."
        )
        second_sentence = (
            f"The request for {vendor_display} at ${request.total_amount:,.2f} in cost center "
            f"{request.cost_center_id} could not be fully validated after check_budget, "
            "check_vendor_duplication, check_policy_compliance, and assess_risk were executed."
        )
        third_sentence = (
            "Tool error details: " + "; ".join(failures) + "."
        )
        return " ".join([first_sentence, second_sentence, third_sentence])

    violation_ids = [
        item.get("policy_id", "")
        for item in policy.get("details", {}).get("violations", [])
        if isinstance(item, dict)
    ]
    violation_ids = [policy_id for policy_id in violation_ids if policy_id]
    violation_text = ", ".join(sorted(set(violation_ids))) if violation_ids else "none"

    budget_details = budget.get("details", {}) if isinstance(budget.get("details"), dict) else {}
    remaining_budget = float(budget_details.get("remaining_budget", 0.0))
    overage = float(budget_details.get("overage", 0.0))
    risk_level = str(risk.get("risk_level", "unknown"))

    first_sentence = (
        f"I recommend {decision} for {request.request_id} after reviewing check_budget, "
        "check_vendor_duplication, check_policy_compliance, and assess_risk."
    )
    second_sentence = (
        f"The request for {vendor_display} totals ${request.total_amount:,.2f} against "
        f"cost center {request.cost_center_id} with ${remaining_budget:,.2f} remaining, "
        f"and policy checks identified {violation_text} with risk level {risk_level}."
    )

    if decision == "approve":
        third_sentence = (
            "No deny or escalate signals were triggered by the checks, so the request can proceed "
            "within policy controls."
        )
    elif decision == "deny":
        third_sentence = (
            f"Denial is driven by policy and budget controls because the evaluated checks found a "
            f"blocking condition including an overage of ${overage:,.2f} or deny-level policy signal."
        )
    else:
        third_sentence = (
            "Escalation is required because at least one check returned escalation conditions that "
            "need manual procurement, legal, or leadership review before commitment."
        )

    if model_error is None:
        return " ".join([first_sentence, second_sentence, third_sentence])

    fourth_sentence = (
        "A model execution issue occurred, so this recommendation was produced using deterministic "
        f"tool outputs: {type(model_error).__name__}."
    )
    return " ".join([first_sentence, second_sentence, third_sentence, fourth_sentence])


def _preflight_tool_error_recommendation(
    request: PurchaseRequest,
    tool_outputs: dict[str, dict[str, Any]],
) -> ProcurementRecommendation | None:
    """Run tools once to detect typed errors and short-circuit with escalation."""
    if not any(output.get("error") for output in tool_outputs.values()):
        return None

    return ProcurementRecommendation(
        decision="escalate",
        rationale=_fallback_rationale(request, tool_outputs, decision="escalate"),
    )


def run_request_sync(request: PurchaseRequest) -> ProcurementRecommendation:
    """Run the agent for a validated purchase request and return typed output."""
    tool_outputs = _collect_tool_outputs(request)
    preflight = _preflight_tool_error_recommendation(request, tool_outputs)
    if preflight is not None:
        return preflight

    user_prompt = (
        "Evaluate this purchase request and produce a recommendation. "
        "Call all four tools before final decision.\n"
        f"Request JSON: {request.model_dump_json()}"
    )

    if _should_skip_model_call():
        fallback_decision = _fallback_decision(tool_outputs)
        return ProcurementRecommendation(
            decision=fallback_decision,
            rationale=_fallback_rationale(
                request,
                tool_outputs,
                decision=fallback_decision,
            ),
        )

    try:
        result = agent.run_sync(user_prompt)
        return result.output
    except Exception as exc:
        fallback_decision = _fallback_decision(tool_outputs)
        return ProcurementRecommendation(
            decision=fallback_decision,
            rationale=_fallback_rationale(
                request,
                tool_outputs,
                decision=fallback_decision,
                model_error=exc,
            ),
        )


async def run_request_async(request: PurchaseRequest) -> ProcurementRecommendation:
    """Asynchronously run the agent for a validated purchase request."""
    tool_outputs = _collect_tool_outputs(request)
    preflight = _preflight_tool_error_recommendation(request, tool_outputs)
    if preflight is not None:
        return preflight

    user_prompt = (
        "Evaluate this purchase request and produce a recommendation. "
        "Call all four tools before final decision.\n"
        f"Request JSON: {request.model_dump_json()}"
    )

    if _should_skip_model_call():
        fallback_decision = _fallback_decision(tool_outputs)
        return ProcurementRecommendation(
            decision=fallback_decision,
            rationale=_fallback_rationale(
                request,
                tool_outputs,
                decision=fallback_decision,
            ),
        )

    try:
        result = await agent.run(user_prompt)
        return result.output
    except Exception as exc:
        fallback_decision = _fallback_decision(tool_outputs)
        return ProcurementRecommendation(
            decision=fallback_decision,
            rationale=_fallback_rationale(
                request,
                tool_outputs,
                decision=fallback_decision,
                model_error=exc,
            ),
        )


def run_request_from_dict_sync(request_payload: dict[str, Any]) -> ProcurementRecommendation:
    """Validate dict input and return a safe recommendation on validation failures."""
    try:
        request = PurchaseRequest.model_validate(request_payload)
    except ValidationError as exc:
        return ProcurementRecommendation(
            decision="escalate",
            rationale=(
                "Escalated because purchase request input validation failed before tool checks. "
                f"Validation details: {exc}"
            ),
        )
    return run_request_sync(request)


async def run_request_from_dict_async(request_payload: dict[str, Any]) -> ProcurementRecommendation:
    """Async variant of dict-input request handling with validation fallback."""
    try:
        request = PurchaseRequest.model_validate(request_payload)
    except ValidationError as exc:
        return ProcurementRecommendation(
            decision="escalate",
            rationale=(
                "Escalated because purchase request input validation failed before tool checks. "
                f"Validation details: {exc}"
            ),
        )
    return await run_request_async(request)
