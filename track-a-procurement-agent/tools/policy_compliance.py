"""Policy compliance tool for evaluating purchase requests against all procurement rules."""

from __future__ import annotations

from typing import Any

from data import loader
from models import PurchaseRequest


def check_policy_compliance(request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against policies POL-001 through POL-008.

    Args:
        request: Purchase request payload to evaluate.

    Returns:
        A dictionary with:
        - violations: list of policy violations, each with policy_id, rule_description,
          and forced_decision (deny or escalate).
        - violation_count: number of violations.
        - highest_severity: one of none, deny, or escalate.
        - error: optional string when required data cannot be evaluated.
    """
    result: dict[str, object] = {
        "violations": [],
        "violation_count": 0,
        "highest_severity": "none",
    }

    try:
        policies = loader.load_policies()
        vendors = loader.load_vendors()
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        result["error"] = f"Policy evaluation data file not found: {exc}"
        result["error_type"] = "FileNotFoundError"
        result["highest_severity"] = "escalate"
        return result
    except KeyError as exc:
        result["error"] = f"Policy evaluation data missing expected key: {exc}"
        result["error_type"] = "KeyError"
        result["highest_severity"] = "escalate"
        return result
    except Exception as exc:
        result["error"] = f"Policy evaluation data unavailable: {exc}"
        result["error_type"] = type(exc).__name__
        result["highest_severity"] = "escalate"
        return result

    policy_map: dict[str, dict[str, Any]] = {
        str(policy.get("policy_id")): policy
        for policy in policies
        if isinstance(policy, dict) and policy.get("policy_id")
    }

    vendor = next(
        (
            item
            for item in vendors
            if isinstance(item, dict) and item.get("vendor_id") == request.vendor_id
        ),
        None,
    )
    if vendor is None:
        result["error"] = f"Vendor '{request.vendor_id}' not found in vendor data."
        result["highest_severity"] = "escalate"
        return result

    budget = next(
        (
            item
            for item in budgets
            if isinstance(item, dict) and item.get("cost_center_id") == request.cost_center_id
        ),
        None,
    )
    if budget is None:
        result["error"] = f"Cost center '{request.cost_center_id}' not found in budget data."
        result["highest_severity"] = "escalate"
        return result

    remaining_value = budget.get("remaining_budget", budget.get("remaining"))
    try:
        remaining_budget = float(remaining_value)
    except (TypeError, ValueError):
        result["error"] = f"Remaining budget unavailable for cost center '{request.cost_center_id}'."
        result["highest_severity"] = "escalate"
        return result

    violations: list[dict[str, str]] = []

    def add_violation(policy_id: str, forced_decision: str) -> None:
        policy = policy_map.get(policy_id, {})
        description = str(policy.get("description", "Policy rule violated."))
        violations.append(
            {
                "policy_id": policy_id,
                "rule_description": description,
                "forced_decision": forced_decision,
            }
        )

    # POL-001: amount > threshold, contracted category, requested vendor not active,
    # and at least one other active contracted vendor exists in category.
    pol_001 = policy_map.get("POL-001", {})
    pol_001_threshold = float(pol_001.get("threshold_amount", 25000.0))
    pol_001_categories = set(pol_001.get("affected_categories", []))
    if (
        request.total_amount > pol_001_threshold
        and request.category in pol_001_categories
        and vendor.get("contract_status") != "active"
    ):
        has_other_active = any(
            isinstance(item, dict)
            and item.get("vendor_id") != request.vendor_id
            and item.get("category") == request.category
            and item.get("contract_status") == "active"
            for item in vendors
        )
        if has_other_active:
            add_violation("POL-001", "deny")

    # POL-002: manager approval threshold (10,000 to 49,999.99) escalates for approval.
    pol_002 = policy_map.get("POL-002", {})
    pol_002_min = float(pol_002.get("threshold_amount", 10000.0))
    pol_002_max = float(pol_002.get("upper_threshold", 49999.99))
    if pol_002_min <= request.total_amount <= pol_002_max:
        add_violation("POL-002", "escalate")

    # POL-003: director approval threshold at 50,000 and above escalates.
    pol_003 = policy_map.get("POL-003", {})
    pol_003_min = float(pol_003.get("threshold_amount", 50000.0))
    if request.total_amount >= pol_003_min:
        add_violation("POL-003", "escalate")

    # POL-004: catering category is prohibited and denied regardless of amount.
    pol_004_categories = set(policy_map.get("POL-004", {}).get("affected_categories", []))
    if request.category in pol_004_categories:
        add_violation("POL-004", "deny")

    # POL-005: expired contract vendors are denied.
    if vendor.get("contract_status") == "expired":
        add_violation("POL-005", "deny")

    # POL-006: compliance-flagged vendors are escalated.
    if bool(vendor.get("compliance_flag")):
        add_violation("POL-006", "escalate")

    # POL-007: staffing engagements over 40 hours require contracted staffing vendor.
    if (
        request.category == "staffing"
        and request.quantity > 40
        and vendor.get("contract_status") != "active"
    ):
        add_violation("POL-007", "deny")

    # POL-008: requests exceeding remaining budget are denied.
    if request.total_amount > remaining_budget:
        add_violation("POL-008", "deny")

    highest = "none"
    if any(item["forced_decision"] == "escalate" for item in violations):
        highest = "escalate"
    elif any(item["forced_decision"] == "deny" for item in violations):
        highest = "deny"

    result["violations"] = violations
    result["violation_count"] = len(violations)
    result["highest_severity"] = highest
    return result
