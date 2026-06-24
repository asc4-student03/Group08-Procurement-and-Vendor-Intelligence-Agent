"""Tests for root model contracts."""

import pytest
from pydantic import ValidationError

from models import ProcurementRecommendation, PurchaseRequest


def test_purchase_request_accepts_operational_fields_only() -> None:
    """PurchaseRequest should validate with only the 10 operational fields."""
    request = PurchaseRequest(
        request_id="REQ-001",
        requestor="M. Okonkwo",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Cloud license renewal",
        quantity=500,
        unit_price=48.0,
        total_amount=24000.0,
    )

    assert request.request_id == "REQ-001"


def test_purchase_request_rejects_non_positive_numeric_values() -> None:
    """PurchaseRequest should reject invalid non-positive numeric values."""
    with pytest.raises(ValidationError):
        PurchaseRequest(
            request_id="REQ-NEG",
            requestor="A. User",
            cost_center_id="CC-001",
            vendor_name="Vendor",
            vendor_id="V-001",
            category="office_supplies",
            item_description="Bad numeric input",
            quantity=0,
            unit_price=10.0,
            total_amount=10.0,
        )


def test_purchase_request_rejects_amount_mismatch() -> None:
    """PurchaseRequest should reject totals that mismatch quantity times unit_price."""
    with pytest.raises(ValidationError):
        PurchaseRequest(
            request_id="REQ-MISMATCH",
            requestor="A. User",
            cost_center_id="CC-001",
            vendor_name="Vendor",
            vendor_id="V-001",
            category="office_supplies",
            item_description="Amount mismatch",
            quantity=2,
            unit_price=10.0,
            total_amount=25.0,
        )


def test_procurement_recommendation_rejects_invalid_decision() -> None:
    """ProcurementRecommendation should reject decision values outside allowed domain."""
    with pytest.raises(ValidationError):
        ProcurementRecommendation(
            request_id="REQ-001",
            decision="hold",
            rationale="Needs more information",
        )


def test_procurement_recommendation_rejects_empty_rationale() -> None:
    """ProcurementRecommendation rationale must be non-empty after stripping."""
    with pytest.raises(ValidationError):
        ProcurementRecommendation(
            request_id="REQ-001",
            decision="approve",
            rationale="   ",
        )
