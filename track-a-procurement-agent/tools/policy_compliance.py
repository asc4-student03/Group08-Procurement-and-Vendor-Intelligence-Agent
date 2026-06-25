"""Policy compliance tool for evaluating purchase requests against POL-001..POL-008."""

from __future__ import annotations

from models import PurchaseRequest
from data import loader


def _typed_error(error: Exception, stage: str) -> dict[str, str]:
    """Build a consistent typed error payload for tool responses."""
    return {
        "type": type(error).__name__,
        "message": str(error),
        "stage": stage,
    }


def check_policy_compliance(request: PurchaseRequest) -> dict[str, object]:
    """Evaluate a purchase request against all eight procurement policies.

    The tool checks POL-001 through POL-008 in one pass and returns every
    violated policy. Each violation includes the policy ID, a rule description,
    and a forced decision constrained to deny or escalate.

    Args:
        request: Validated purchase request model.

    Returns:
        Structured result with:
        - signal: approve, deny, or escalate
        - summary: Short compliance summary
        - details: violation metadata including all violations and policy IDs checked
        - error: Optional error message when source data cannot be loaded
    """
    try:
        policies = loader.load_policies()
        vendors = loader.load_vendors()
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return {
            "signal": "escalate",
            "summary": "Policy data file missing; escalate for manual review.",
            "details": {
                "violations": [],
                "evaluated_policy_ids": [],
                "violation_count": 0,
            },
            "error": _typed_error(exc, "data_load"),
        }
    except KeyError as exc:
        return {
            "signal": "escalate",
            "summary": "Policy data missing required fields; escalate for manual review.",
            "details": {
                "violations": [],
                "evaluated_policy_ids": [],
                "violation_count": 0,
            },
            "error": _typed_error(exc, "data_shape"),
        }
    except Exception as exc:
        return {
            "signal": "escalate",
            "summary": "Unexpected policy compliance failure; escalate for manual review.",
            "details": {
                "violations": [],
                "evaluated_policy_ids": [],
                "violation_count": 0,
            },
            "error": _typed_error(exc, "unexpected"),
        }

    vendor = next((v for v in vendors if v.get("vendor_id") == request.vendor_id), None)
    budget = next(
        (b for b in budgets if b.get("cost_center_id") == request.cost_center_id),
        None,
    )

    policy_by_id = {str(item.get("policy_id", "")): item for item in policies}
    evaluated_policy_ids = [f"POL-{idx:03d}" for idx in range(1, 9)]

    violations: list[dict[str, str]] = []

    # POL-001: Single-source restriction
    pol_001 = policy_by_id.get("POL-001", {})
    pol_001_threshold = float(pol_001.get("threshold_amount", 25000.0))
    pol_001_categories = set(pol_001.get("affected_categories", []))
    active_vendors_in_category = [
        item
        for item in vendors
        if item.get("category") == request.category
        and item.get("contract_status") == "active"
    ]
    selected_vendor_active = vendor is not None and vendor.get("contract_status") == "active"
    if (
        request.total_amount > pol_001_threshold
        and request.category in pol_001_categories
        and active_vendors_in_category
        and not selected_vendor_active
    ):
        violations.append(
            {
                "policy_id": "POL-001",
                "violated_rule": (
                    "Amount exceeds single-source threshold and selected vendor is not an "
                    "active contracted vendor in this category."
                ),
                "forced_decision": "deny",
            }
        )

    # POL-002: Manager approval threshold
    # This is a process checkpoint, not a deny/escalate violation trigger.
    # Requests in this range may still be approved when no blocking violations exist.
    pol_002_low = float(policy_by_id.get("POL-002", {}).get("threshold_amount", 10000.0))
    pol_002_high = float(policy_by_id.get("POL-002", {}).get("upper_threshold", 49999.99))
    _pol_002_requires_manager_approval = pol_002_low <= request.total_amount <= pol_002_high

    # POL-003: Director approval threshold
    pol_003_threshold = float(policy_by_id.get("POL-003", {}).get("threshold_amount", 50000.0))
    if request.total_amount >= pol_003_threshold:
        violations.append(
            {
                "policy_id": "POL-003",
                "violated_rule": (
                    "Amount meets or exceeds director approval threshold and requires "
                    "director-level review."
                ),
                "forced_decision": "escalate",
            }
        )

    # POL-004: Prohibited category catering
    if request.category == "catering":
        violations.append(
            {
                "policy_id": "POL-004",
                "violated_rule": (
                    "Catering purchases are prohibited under current spend reduction policy."
                ),
                "forced_decision": "deny",
            }
        )

    # POL-005: Expired contract vendor
    if vendor is not None and vendor.get("contract_status") == "expired":
        violations.append(
            {
                "policy_id": "POL-005",
                "violated_rule": "Vendor contract is expired and purchases cannot proceed.",
                "forced_decision": "deny",
            }
        )

    # POL-006: Compliance-flagged vendor hold
    if vendor is not None and bool(vendor.get("compliance_flag")):
        violations.append(
            {
                "policy_id": "POL-006",
                "violated_rule": (
                    "Vendor has an active compliance flag and requires Legal/Compliance "
                    "escalation."
                ),
                "forced_decision": "escalate",
            }
        )

    # POL-007: Staffing single-source over 40 hours
    if (
        request.category == "staffing"
        and request.quantity > 40
        and (vendor is None or vendor.get("contract_status") != "active")
    ):
        violations.append(
            {
                "policy_id": "POL-007",
                "violated_rule": (
                    "Staffing engagements above 40 hours require an active enterprise "
                    "staffing contract."
                ),
                "forced_decision": "deny",
            }
        )

    # POL-008: Budget overage prohibition
    remaining = float(budget.get("remaining", 0.0)) if budget is not None else 0.0
    if budget is None or request.total_amount > remaining:
        violations.append(
            {
                "policy_id": "POL-008",
                "violated_rule": (
                    "Request would exceed remaining quarterly budget for the cost center."
                ),
                "forced_decision": "deny",
            }
        )

    forced_decisions = {entry["forced_decision"] for entry in violations}
    if "escalate" in forced_decisions:
        signal = "escalate"
        summary = "Policy violations detected; escalation required."
    elif "deny" in forced_decisions:
        signal = "deny"
        summary = "Policy violations detected; request must be denied."
    else:
        signal = "approve"
        summary = "No policy violations detected."

    return {
        "signal": signal,
        "summary": summary,
        "details": {
            "violations": violations,
            "evaluated_policy_ids": evaluated_policy_ids,
            "violation_count": len(violations),
        },
    }
