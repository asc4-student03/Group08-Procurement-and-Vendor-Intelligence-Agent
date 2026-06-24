"""Tests for policy compliance checks using real mock data."""

import pytest

import data.loader as data_loader
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def test_pol_004_catering_prohibition_deny() -> None:
    """REQ-009 style case: catering requests should trigger POL-004 denial."""
    request = PurchaseRequest(
        request_id="REQ-009",
        requestor="P. Harrington",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co.",
        vendor_id="V-017",
        category="catering",
        item_description="Executive offsite catering service",
        quantity=1,
        unit_price=3200.0,
        total_amount=3200.0,
    )

    result = check_policy_compliance(request)

    assert any(
        v["policy_id"] == "POL-004" and v["forced_decision"] == "deny"
        for v in result["violations"]
    )


def test_pol_002_manager_approval_threshold_escalate() -> None:
    """Any request in 10,000 to 49,999 range should trigger POL-002."""
    request = PurchaseRequest(
        request_id="REQ-POL-002",
        requestor="T. Beaumont",
        cost_center_id="CC-004",
        vendor_name="Pinnacle Hardware",
        vendor_id="V-005",
        category="hardware",
        item_description="Manager-threshold purchase",
        quantity=1,
        unit_price=12000.0,
        total_amount=12000.0,
    )

    result = check_policy_compliance(request)

    assert any(
        v["policy_id"] == "POL-002" and v["forced_decision"] == "escalate"
        for v in result["violations"]
    )


def test_pol_005_expired_contract_vendor_deny() -> None:
    """REQ-007 case: Crestview expired contract should trigger POL-005 denial."""
    request = PurchaseRequest(
        request_id="REQ-007",
        requestor="C. Johnson",
        cost_center_id="CC-010",
        vendor_name="Crestview Print and Media",
        vendor_id="V-010",
        category="marketing_materials",
        item_description="Campaign collateral print run",
        quantity=1,
        unit_price=5400.0,
        total_amount=5400.0,
    )

    result = check_policy_compliance(request)

    assert any(
        v["policy_id"] == "POL-005" and v["forced_decision"] == "deny"
        for v in result["violations"]
    )


def test_policy_compliance_mixed_severity_sets_highest_to_escalate() -> None:
    """When deny and escalate violations coexist, highest_severity should be escalate."""
    request = PurchaseRequest(
        request_id="REQ-MIXED",
        requestor="F. Osei",
        cost_center_id="CC-001",
        vendor_name="Vertex Consulting Group",
        vendor_id="V-006",
        category="catering",
        item_description="Mixed severity policy trigger case",
        quantity=1,
        unit_price=12000.0,
        total_amount=12000.0,
    )

    result = check_policy_compliance(request)

    assert any(v["forced_decision"] == "deny" for v in result["violations"])
    assert any(v["forced_decision"] == "escalate" for v in result["violations"])
    assert result["highest_severity"] == "escalate"


def test_policy_compliance_no_policy_violations_returns_none() -> None:
    """Requests with no policy trigger should return zero violations and none severity."""
    request = PurchaseRequest(
        request_id="REQ-004",
        requestor="D. Whitfield",
        cost_center_id="CC-008",
        vendor_name="Delta Fleet Parts",
        vendor_id="V-013",
        category="fleet_parts",
        item_description="Low amount contracted vendor purchase",
        quantity=24,
        unit_price=415.0,
        total_amount=9960.0,
    )

    result = check_policy_compliance(request)

    assert result["violations"] == []
    assert result["violation_count"] == 0
    assert result["highest_severity"] == "none"


def test_policy_compliance_handles_data_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Policy loader failures should return escalate-safe error output."""

    def _raise_loader_error() -> list[object]:
        raise FileNotFoundError("policies.json missing")

    monkeypatch.setattr(data_loader, "load_policies", _raise_loader_error)

    request = PurchaseRequest(
        request_id="REQ-001",
        requestor="M. Okonkwo",
        cost_center_id="CC-001",
        vendor_name="BlueSky Cloud Solutions",
        vendor_id="V-002",
        category="software_licenses",
        item_description="Loader error path",
        quantity=500,
        unit_price=48.0,
        total_amount=24000.0,
    )

    result = check_policy_compliance(request)

    assert result["violations"] == []
    assert result["violation_count"] == 0
    assert result["highest_severity"] == "escalate"
    assert "error" in result
