"""Risk assessment tool for vendor profile evaluation."""

from __future__ import annotations

from data import loader


def _typed_error(error: Exception, stage: str) -> dict[str, str]:
    """Build a consistent typed error payload for tool responses."""
    return {
        "type": type(error).__name__,
        "message": str(error),
        "stage": stage,
    }


def assess_risk(vendor_id: str) -> dict[str, object]:
    """Return vendor compliance and contract-based risk profile.

    Args:
        vendor_id: Vendor identifier from the purchase request.

    Returns:
        A structured profile with keys:
        - vendor_id
        - vendor_name
        - compliance_flag
        - contract_status
        - risk_level (low|medium|high|critical)
        - risk_summary
        - error (optional)
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
            "risk_summary": "Vendor data file missing; escalate for manual review.",
            "error": _typed_error(exc, "data_load"),
        }
    except KeyError as exc:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor data missing required fields; escalate for manual review.",
            "error": _typed_error(exc, "data_shape"),
        }
    except Exception as exc:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Unexpected risk assessment failure; escalate for manual review.",
            "error": _typed_error(exc, "unexpected"),
        }

    vendor = next((item for item in vendors if item.get("vendor_id") == vendor_id), None)
    if vendor is None:
        return {
            "vendor_id": vendor_id,
            "vendor_name": "Unknown",
            "compliance_flag": False,
            "contract_status": "unknown",
            "risk_level": "critical",
            "risk_summary": "Vendor not found in records; escalate for manual review.",
            "error": {
                "type": "ReferenceDataError",
                "message": f"Unknown vendor_id: {vendor_id}",
                "stage": "lookup",
            },
        }

    compliance_flag = bool(vendor.get("compliance_flag", False))
    contract_status = str(vendor.get("contract_status", "unknown"))

    if compliance_flag:
        risk_level = "critical"
        risk_summary = "Vendor has active compliance flag; escalation required."
    elif contract_status == "expired":
        risk_level = "high"
        risk_summary = "Vendor contract is expired and presents high procurement risk."
    elif contract_status == "none":
        risk_level = "medium"
        risk_summary = "Vendor has no active contract; medium risk profile."
    else:
        risk_level = "low"
        risk_summary = "Vendor has active contract and no compliance flags."

    return {
        "vendor_id": vendor_id,
        "vendor_name": str(vendor.get("name", "Unknown")),
        "compliance_flag": compliance_flag,
        "contract_status": contract_status,
        "risk_level": risk_level,
        "risk_summary": risk_summary,
    }
