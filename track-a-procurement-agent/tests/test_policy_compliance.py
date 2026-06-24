from data.loader import load_requests
from models import PurchaseRequest
from tools.policy_compliance import check_policy_compliance


def _find_request(request_id: str) -> dict[str, object]:
    for item in load_requests():
        if item.get("request_id") == request_id:
            return item
    raise AssertionError(f"Request not found: {request_id}")


def test_policy_compliance_pol_004_catering_prohibition() -> None:
    """Catering request should include POL-004 deny violation."""
    request = PurchaseRequest(
        request_id="REQ-009",
        requestor="P. Harrington",
        cost_center_id="CC-005",
        vendor_name="Summit Catering Co.",
        vendor_id="V-017",
        category="catering",
        item_description="Executive leadership offsite lunch service",
        quantity=4,
        unit_price=800.0,
        total_amount=3200.0,
    )

    result = check_policy_compliance(request)
    violations = result["details"]["violations"]
    pol_004 = [v for v in violations if v["policy_id"] == "POL-004"]

    assert pol_004
    assert pol_004[0]["forced_decision"] == "deny"
    assert "violated_rule" in pol_004[0]


def test_policy_compliance_pol_002_manager_threshold() -> None:
    """Any amount in manager threshold range should include POL-002 escalation."""
    request = PurchaseRequest(
        request_id="REQ-005",
        requestor="A. Patel",
        cost_center_id="CC-001",
        vendor_name="Ironclad Security Systems",
        vendor_id="V-011",
        category="security",
        item_description="Access control system upgrade",
        quantity=1,
        unit_price=14200.0,
        total_amount=14200.0,
    )

    result = check_policy_compliance(request)
    violations = result["details"]["violations"]
    pol_002 = [v for v in violations if v["policy_id"] == "POL-002"]

    assert pol_002
    assert pol_002[0]["forced_decision"] == "escalate"


def test_policy_compliance_pol_005_expired_contract_req_007() -> None:
    """REQ-007 should include POL-005 deny violation for expired vendor contract."""
    req_007 = _find_request("REQ-007")
    request = PurchaseRequest(
        request_id=str(req_007["request_id"]),
        requestor=str(req_007["requestor"]),
        cost_center_id=str(req_007["cost_center_id"]),
        vendor_name=str(req_007["vendor_name"]),
        vendor_id=str(req_007["vendor_id"]),
        category=str(req_007["category"]),
        item_description=str(req_007["item_description"]),
        quantity=int(req_007["quantity"]),
        unit_price=float(req_007["unit_price"]),
        total_amount=float(req_007["total_amount"]),
    )

    result = check_policy_compliance(request)
    violations = result["details"]["violations"]
    pol_005 = [v for v in violations if v["policy_id"] == "POL-005"]

    assert pol_005
    assert pol_005[0]["forced_decision"] == "deny"
