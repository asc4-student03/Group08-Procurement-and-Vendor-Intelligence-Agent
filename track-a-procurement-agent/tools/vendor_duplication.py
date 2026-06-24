"""Vendor duplication tool for enforcing POL-001 single-source threshold checks."""

from __future__ import annotations

from typing import Any

from data import loader


POL_001_THRESHOLD = 25_000.0


def check_vendor_duplication(vendor_id: str, category: str, amount: float) -> dict[str, object]:
    """Check for active contracted vendor conflicts in the same category.

    This tool enforces the POL-001 threshold rule: duplication checks only trigger
    when the request amount is greater than $25,000 in a contracted category.

    Args:
        vendor_id: Vendor identifier from the purchase request.
        category: Requested procurement category.
        amount: Total request amount in USD.

    Returns:
        A dictionary containing:
        - violation (bool): Whether a POL-001 conflict exists.
        - vendor_id (str): Echo of the requested vendor ID.
        - category (str): Echo of the requested category.
        - amount (float): Echo of the requested amount.
        - conflicting_vendor_ids (list[str]): Active conflicting vendor IDs.
        - conflicting_contracts (list[dict[str, object]]): Active conflicting contract details.
        - reason (str): Human-readable outcome summary.
        - error (str, optional): Present when vendor data cannot be evaluated.
    """
    request_amount = float(amount)
    result: dict[str, object] = {
        "violation": False,
        "vendor_id": vendor_id,
        "category": category,
        "amount": request_amount,
        "conflicting_vendor_ids": [],
        "conflicting_vendor_names": [],
        "conflicting_contracts": [],
        "reason": "",
    }

    try:
        vendors = loader.load_vendors()
    except FileNotFoundError as exc:
        result["reason"] = "Vendor duplication could not be evaluated."
        result["error"] = f"Vendor data file not found: {exc}"
        result["error_type"] = "FileNotFoundError"
        return result
    except KeyError as exc:
        result["reason"] = "Vendor duplication could not be evaluated."
        result["error"] = f"Vendor data missing expected key: {exc}"
        result["error_type"] = "KeyError"
        return result
    except Exception as exc:
        result["reason"] = "Vendor duplication could not be evaluated."
        result["error"] = f"Vendor data unavailable: {exc}"
        result["error_type"] = type(exc).__name__
        return result

    if request_amount <= POL_001_THRESHOLD:
        result["reason"] = (
            "POL-001 threshold not triggered: amount must exceed 25000.0 for duplication checks."
        )
        return result

    requested_vendor = next(
        (
            vendor
            for vendor in vendors
            if isinstance(vendor, dict)
            and vendor.get("vendor_id") == vendor_id
            and vendor.get("category") == category
        ),
        None,
    )

    if requested_vendor is None:
        result["reason"] = "Requested vendor was not found in the specified category."
        result["error"] = f"Vendor '{vendor_id}' not found for category '{category}'."
        return result

    if requested_vendor.get("contract_status") == "active":
        result["reason"] = "Requested vendor already has an active contract in this category."
        return result

    conflicting_contracts: list[dict[str, object]] = []
    for vendor in vendors:
        if not isinstance(vendor, dict):
            continue
        if vendor.get("vendor_id") == vendor_id:
            continue
        if vendor.get("category") != category:
            continue
        if vendor.get("contract_status") != "active":
            continue

        conflicting_contracts.append(
            {
                "vendor_id": str(vendor.get("vendor_id", "")),
                "vendor_name": str(vendor.get("name", "")),
                "contract_id": str(vendor.get("contract_id", "")),
                "contract_status": str(vendor.get("contract_status", "")),
            }
        )

    result["conflicting_contracts"] = conflicting_contracts
    result["conflicting_vendor_ids"] = [
        str(contract.get("vendor_id", "")) for contract in conflicting_contracts
    ]
    result["conflicting_vendor_names"] = [
        str(contract.get("vendor_name", "")) for contract in conflicting_contracts
    ]

    if conflicting_contracts:
        result["violation"] = True
        result["reason"] = (
            "POL-001 conflict: above-threshold request uses a non-contracted vendor while "
            "active contracted alternatives exist in the same category."
        )
    else:
        result["reason"] = "No active conflicting contracts found in this category."

    return result
