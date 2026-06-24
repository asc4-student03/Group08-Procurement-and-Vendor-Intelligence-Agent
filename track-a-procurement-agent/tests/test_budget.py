"""Tests for budget check tool behavior using real mock data."""

import pytest

import data.loader as data_loader
from tools.budget import check_budget


def test_check_budget_within_and_exceeding_for_cc003() -> None:
    """Validate within-budget and over-budget outcomes for cost center CC-003."""
    within_result = check_budget("CC-003", 6900.0)
    over_result = check_budget("CC-003", 7000.0)

    assert within_result["within_budget"] is True
    assert within_result["cost_center_id"] == "CC-003"
    assert within_result["remaining_budget"] == 6900.0
    assert within_result["requested_amount"] == 6900.0
    assert within_result["overage"] == 0.0

    assert over_result["within_budget"] is False
    assert over_result["cost_center_id"] == "CC-003"
    assert over_result["remaining_budget"] == 6900.0
    assert over_result["requested_amount"] == 7000.0
    assert over_result["overage"] == 100.0


def test_check_budget_unknown_cost_center_returns_structured_error() -> None:
    """Unknown cost centers should return within_budget false and include an error."""
    result = check_budget("CC-999", 1000.0)

    assert result["within_budget"] is False
    assert result["cost_center_id"] == "CC-999"
    assert result["requested_amount"] == 1000.0
    assert result["remaining_budget"] == 0.0
    assert result["overage"] == 1000.0
    assert "error" in result


def test_check_budget_handles_data_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Loader failures should produce a structured error payload."""

    def _raise_loader_error() -> list[object]:
        raise FileNotFoundError("budgets.json missing")

    monkeypatch.setattr(data_loader, "load_budgets", _raise_loader_error)

    result = check_budget("CC-003", 100.0)

    assert result["within_budget"] is False
    assert result["cost_center_id"] == "CC-003"
    assert result["requested_amount"] == 100.0
    assert result["remaining_budget"] == 0.0
    assert result["overage"] == 100.0
    assert "error" in result
