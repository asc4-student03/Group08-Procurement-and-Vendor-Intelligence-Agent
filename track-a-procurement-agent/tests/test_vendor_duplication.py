from tools.vendor_duplication import check_vendor_duplication


def test_check_vendor_duplication_req_008_conflicts() -> None:
    """REQ-008 should find contracted office_supplies conflicts V-001 and V-003."""
    result = check_vendor_duplication("V-012", "office_supplies", 28500.0)

    assert result["signal"] == "deny"

    conflict_ids = result["details"]["conflicting_vendor_ids"]
    assert sorted(conflict_ids) == ["V-001", "V-003"]
