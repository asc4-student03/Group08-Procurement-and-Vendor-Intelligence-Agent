"""Tests for vendor duplication checks using real mock vendor data."""

import pytest

from tools.vendor_duplication import check_vendor_duplication
import tools.vendor_duplication as vendor_duplication_tool


def test_req_008_novaprint_conflicts_with_active_office_supply_vendors() -> None:
    """REQ-008: NovaPrint office_supplies at 28,500 should conflict with V-001 and V-003."""
    result = check_vendor_duplication("V-012", "office_supplies", 28500.0)

    assert result["violation"] is True
    assert result["vendor_id"] == "V-012"
    assert result["category"] == "office_supplies"
    assert result["amount"] == 28500.0

    conflict_ids = result["conflicting_vendor_ids"]
    assert isinstance(conflict_ids, list)
    assert set(conflict_ids) == {"V-001", "V-003"}

    conflict_names = result["conflicting_vendor_names"]
    assert isinstance(conflict_names, list)
    assert set(conflict_names) == {"Apex Office Supplies", "Meridian Office Products"}

    conflicting_contracts = result["conflicting_contracts"]
    assert isinstance(conflicting_contracts, list)
    assert {contract["vendor_id"] for contract in conflicting_contracts} == {"V-001", "V-003"}

    assert "error" not in result


def test_vendor_duplication_at_threshold_is_not_violation() -> None:
    """At the POL-001 threshold, violation should remain false with threshold reason text."""
    result = check_vendor_duplication("V-012", "office_supplies", 25000.0)

    assert result["violation"] is False
    assert result["conflicting_vendor_ids"] == []
    assert result["conflicting_vendor_names"] == []
    assert "threshold" in str(result["reason"]).lower()


def test_vendor_duplication_handles_data_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Loader failures should return non-error keys plus error message."""

    def _raise_loader_error() -> list[object]:
        raise FileNotFoundError("vendors.json missing")

    monkeypatch.setattr(vendor_duplication_tool, "load_vendors", _raise_loader_error)

    result = check_vendor_duplication("V-012", "office_supplies", 28500.0)

    assert result["violation"] is False
    assert result["vendor_id"] == "V-012"
    assert result["category"] == "office_supplies"
    assert result["amount"] == 28500.0
    assert result["conflicting_vendor_ids"] == []
    assert result["conflicting_vendor_names"] == []
    assert result["conflicting_contracts"] == []
    assert "error" in result
