from tools.risk_assessment import assess_risk


def test_compliance_flag_vendor_is_critical() -> None:
    result = assess_risk("V-006")
    assert result["risk_level"] == "critical"
    assert result["compliance_flag"] is True


def test_expired_contract_vendor_is_high() -> None:
    result = assess_risk("V-010")
    assert result["risk_level"] == "high"
    assert result["contract_status"] == "expired"


def test_unknown_vendor_returns_structured_error() -> None:
    result = assess_risk("V-999")
    assert result["risk_level"] == "critical"
    assert "error" in result
    assert result["error"]["type"] == "ReferenceDataError"
