from tools.budget import check_budget


def test_check_budget_within_and_over_budget_for_cc_003() -> None:
    """Validate within-budget and over-budget outcomes using real mock data."""
    within_budget = check_budget("CC-003", 6900.0)
    assert within_budget["signal"] == "approve"
    assert within_budget["details"]["remaining_budget"] == 6900.0
    assert within_budget["details"]["overage"] == 0.0

    over_budget = check_budget("CC-003", 11200.0)
    assert over_budget["signal"] == "deny"
    assert over_budget["details"]["remaining_budget"] == 6900.0
    assert over_budget["details"]["overage"] == 4300.0
