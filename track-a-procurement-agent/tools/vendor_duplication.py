"""Vendor duplication check tool for procurement pre-screening."""

from __future__ import annotations

from data.loader import load_policies, load_vendors


def check_vendor_duplication(
    vendor_id: str,
    category: str,
    requested_amount: float,
) -> dict[str, object]:
    """Evaluate vendor duplication conflicts and POL-001 deny eligibility.

    Args:
        vendor_id: Vendor identifier from the purchase request.
        category: Purchase category from the purchase request.
        requested_amount: Request total amount in USD.

    Returns:
        A standard tool payload with keys:
        - signal: approve, deny, or escalate
        - summary: Human-readable outcome summary
        - details: Structured context including input identifiers, threshold data,
          conflicting active vendor IDs, and conflict contract details
        - error: Optional error text when lookup or data loading fails

        POL-001 deny eligibility is triggered only when:
        - requested_amount > 25000
        - category is covered by POL-001 affected categories
        - conflicting active vendors exist
        - selected vendor is not an active contracted vendor in the category
    """
    try:
        vendors = load_vendors()
        policies = load_policies()
    except (FileNotFoundError, TypeError) as exc:
        return {
            "signal": "escalate",
            "summary": "Vendor or policy data unavailable; escalate for manual review.",
            "details": {
                "input_vendor_id": vendor_id,
                "category": category,
                "requested_amount": float(requested_amount),
                "pol_001_threshold": 25000.0,
                "category_in_pol_001_scope": False,
                "conflicting_vendor_ids": [],
                "conflicts": [],
            },
            "error": str(exc),
        }

    vendor_record = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor_record is None:
        return {
            "signal": "escalate",
            "summary": "Vendor not found in vendor records; escalate for manual review.",
            "details": {
                "input_vendor_id": vendor_id,
                "category": category,
                "requested_amount": float(requested_amount),
                "pol_001_threshold": 25000.0,
                "category_in_pol_001_scope": False,
                "conflicting_vendor_ids": [],
                "conflicts": [],
            },
            "error": f"Unknown vendor_id: {vendor_id}",
        }

    if vendor_record.get("category") != category:
        return {
            "signal": "escalate",
            "summary": "Vendor category mismatch; escalate for manual review.",
            "details": {
                "input_vendor_id": vendor_id,
                "category": category,
                "requested_amount": float(requested_amount),
                "pol_001_threshold": 25000.0,
                "category_in_pol_001_scope": False,
                "conflicting_vendor_ids": [],
                "conflicts": [],
            },
            "error": "Input category does not match vendor category.",
        }

    pol_001 = next((item for item in policies if item.get("policy_id") == "POL-001"), None)
    threshold = float(pol_001.get("threshold_amount", 25000.0)) if pol_001 else 25000.0
    affected_categories = pol_001.get("affected_categories", []) if pol_001 else []
    category_in_scope = category in affected_categories

    conflicts = []
    for item in vendors:
        if (
            item.get("vendor_id") != vendor_id
            and item.get("category") == category
            and item.get("contract_status") == "active"
        ):
            conflicts.append(
                {
                    "vendor_id": str(item.get("vendor_id", "")),
                    "vendor_name": str(item.get("name", "")),
                    "contract_id": str(item.get("contract_id", "")),
                    "contract_status": str(item.get("contract_status", "")),
                }
            )

    conflicting_vendor_ids = [entry["vendor_id"] for entry in conflicts]
    amount = float(requested_amount)
    selected_vendor_active = vendor_record.get("contract_status") == "active"
    deny_eligible = (
        amount > threshold
        and category_in_scope
        and len(conflicts) > 0
        and not selected_vendor_active
    )

    if deny_eligible:
        return {
            "signal": "deny",
            "summary": "POL-001 conflict: active contracted alternatives exist above threshold.",
            "details": {
                "input_vendor_id": vendor_id,
                "category": category,
                "requested_amount": round(amount, 2),
                "pol_001_threshold": threshold,
                "category_in_pol_001_scope": category_in_scope,
                "conflicting_vendor_ids": conflicting_vendor_ids,
                "conflicts": conflicts,
            },
        }

    return {
        "signal": "approve",
        "summary": "No deny-eligible vendor duplication conflict under POL-001.",
        "details": {
            "input_vendor_id": vendor_id,
            "category": category,
            "requested_amount": round(amount, 2),
            "pol_001_threshold": threshold,
            "category_in_pol_001_scope": category_in_scope,
            "conflicting_vendor_ids": conflicting_vendor_ids,
            "conflicts": conflicts,
        },
    }
