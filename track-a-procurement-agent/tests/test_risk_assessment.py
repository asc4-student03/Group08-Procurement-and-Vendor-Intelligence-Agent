"""Tests for risk assessment tool behavior using real mock vendor data."""

import pytest

import data.loader as data_loader
from tools.risk_assessment import assess_risk


def test_assess_risk_compliance_flagged_vendor_is_critical() -> None:
    """Compliance-flagged vendors should map to critical risk."""
    result = assess_risk("V-006")

    assert result["risk_level"] == "critical"
    assert result["compliance_flag"] is True
    assert "error" not in result


def test_assess_risk_expired_contract_vendor_is_high() -> None:
    """Expired-contract vendors should map to high risk."""
    result = assess_risk("V-010")

    assert result["risk_level"] == "high"
    assert result["contract_status"] == "expired"
    assert "error" not in result


def test_assess_risk_no_contract_vendor_is_medium() -> None:
    """No-contract vendors should map to medium risk."""
    result = assess_risk("V-012")

    assert result["risk_level"] == "medium"
    assert result["contract_status"] == "none"
    assert "error" not in result


def test_assess_risk_active_clean_vendor_is_low() -> None:
    """Active clean vendors should map to low risk."""
    result = assess_risk("V-002")

    assert result["risk_level"] == "low"
    assert result["contract_status"] == "active"
    assert result["compliance_flag"] is False


def test_assess_risk_unknown_vendor_returns_error_and_conservative_risk() -> None:
    """Unknown vendors should return error and escalation-safe risk output."""
    result = assess_risk("V-999")

    assert "error" in result
    assert result["risk_level"] == "critical"
    assert result["contract_status"] == "unknown"


def test_assess_risk_handles_data_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Loader failures should return error and conservative risk output."""

    def _raise_loader_error() -> list[object]:
        raise FileNotFoundError("vendors.json missing")

    monkeypatch.setattr(data_loader, "load_vendors", _raise_loader_error)

    result = assess_risk("V-002")

    assert "error" in result
    assert result["risk_level"] == "critical"
    assert result["contract_status"] == "unknown"
