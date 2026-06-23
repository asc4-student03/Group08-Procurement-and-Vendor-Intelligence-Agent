"""Risk assessment tool for procurement request pre-screening."""

from __future__ import annotations

from data.loader import load_vendors


def assess_risk(
    vendor_id: str,
    category: str,
    requested_amount: float,
    cost_center_id: str,
) -> dict[str, object]:
    """Assess vendor risk and return a standard tool payload.

    Args:
        vendor_id: Vendor identifier from the purchase request.
        category: Purchase category from the purchase request.
        requested_amount: Request total amount in USD.
        cost_center_id: Cost center identifier from the purchase request.

    Returns:
        A standard tool payload:
        {
          "signal": "approve|deny|escalate",
          "summary": str,
          "details": {
            "vendor_id": str,
            "category": str,
            "requested_amount": float,
            "cost_center_id": str,
            "contract_status": str,
            "compliance_flag": bool,
            "risk_level": "low|medium|high|critical"
          }
        }
        If data lookup fails, includes an additional "error" key.
    """
    try:
        vendors = load_vendors()
    except (FileNotFoundError, TypeError) as exc:
        return {
            "signal": "escalate",
            "summary": "Vendor risk data unavailable; escalate for manual review.",
            "details": {
                "vendor_id": vendor_id,
                "category": category,
                "requested_amount": float(requested_amount),
                "cost_center_id": cost_center_id,
                "contract_status": "unknown",
                "compliance_flag": False,
                "risk_level": "critical",
            },
            "error": str(exc),
        }

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return {
            "signal": "escalate",
            "summary": "Vendor not found in records; escalate for manual review.",
            "details": {
                "vendor_id": vendor_id,
                "category": category,
                "requested_amount": float(requested_amount),
                "cost_center_id": cost_center_id,
                "contract_status": "unknown",
                "compliance_flag": False,
                "risk_level": "critical",
            },
            "error": f"Unknown vendor_id: {vendor_id}",
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "none"))

    if compliance_flag:
        risk_level = "critical"
        signal = "escalate"
        summary = "Vendor has active compliance flag; escalation required."
    elif contract_status == "expired":
        risk_level = "high"
        signal = "deny"
        summary = "Vendor contract is expired and presents high procurement risk."
    elif contract_status == "none":
        risk_level = "medium"
        signal = "approve"
        summary = "Vendor has no active contract; medium risk profile."
    else:
        risk_level = "low"
        signal = "approve"
        summary = "Vendor has active contract and no compliance flags."

    return {
        "signal": signal,
        "summary": summary,
        "details": {
            "vendor_id": vendor_id,
            "category": category,
            "requested_amount": float(requested_amount),
            "cost_center_id": cost_center_id,
            "contract_status": contract_status,
            "compliance_flag": compliance_flag,
            "risk_level": risk_level,
        },
    }
