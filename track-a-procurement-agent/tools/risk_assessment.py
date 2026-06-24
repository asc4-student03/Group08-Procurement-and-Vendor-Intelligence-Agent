"""Risk assessment tool for vendor compliance and contract-status evaluation."""

from __future__ import annotations

from data import loader


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Return a structured risk profile for the requested vendor.

    Args:
        vendor_id: Vendor identifier to assess.

    Returns:
        Structured risk payload with risk level and optional error context.
    """
    try:
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor data unavailable; escalate for manual review.",
            "error": f"Vendor data file not found: {exc}",
            "error_type": "FileNotFoundError",
        }
    except KeyError as exc:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor data unavailable; escalate for manual review.",
            "error": f"Vendor data missing expected key: {exc}",
            "error_type": "KeyError",
        }
    except Exception as exc:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor data unavailable; escalate for manual review.",
            "error": f"Vendor data could not be loaded: {exc}",
            "error_type": type(exc).__name__,
        }

    vendor = next(
        (
            record
            for record in vendors
            if isinstance(record, dict) and record.get("vendor_id") == vendor_id
        ),
        None,
    )

    if vendor is None:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor not found; escalate for manual review.",
            "error": f"Vendor '{vendor_id}' not found in vendor data.",
        }

    vendor_name = str(vendor.get("name", "Unknown"))
    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "unknown"))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = "Vendor is compliance-flagged and requires legal/compliance escalation."
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired and requires contract remediation before approval."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no active contract and requires additional due diligence."
    else:
        risk_level = "low"
        risk_summary = "Vendor has an active contract and no compliance flag."

    return {
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }
