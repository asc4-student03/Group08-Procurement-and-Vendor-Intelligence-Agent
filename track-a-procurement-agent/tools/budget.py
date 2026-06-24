"""Budget check tool for validating request amounts against remaining budget."""

from __future__ import annotations

from data.loader import load_budgets


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a purchase request fits a cost center's remaining budget.

    This tool loads budget records via ``data.loader.load_budgets`` and compares
    ``requested_amount`` against the target cost center's remaining budget.

    Args:
        cost_center_id: Cost center identifier to evaluate (for example ``CC-001``).
        requested_amount: Requested purchase amount in USD.

    Returns:
        A dictionary with the following keys:
        - ``within_budget`` (bool): True when the request is within or equal to remaining budget.
        - ``cost_center_id`` (str): Echo of the evaluated cost center ID.
        - ``remaining_budget`` (float): Remaining budget for the matched cost center.
        - ``requested_amount`` (float): Echo of the requested amount.
        - ``overage`` (float): Positive amount over budget, or 0 when within budget.
        - ``error`` (str, optional): Present when budget data cannot be loaded,
          the cost center is unknown, or the remaining amount is unavailable.
    """
    requested = float(requested_amount)

    try:
        budgets = load_budgets()
    except Exception as exc:
        return {
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": requested,
            "overage": max(0.0, requested),
            "error": f"Budget data could not be loaded: {exc}",
        }

    budget_record = next(
        (
            record
            for record in budgets
            if isinstance(record, dict) and record.get("cost_center_id") == cost_center_id
        ),
        None,
    )

    if budget_record is None:
        return {
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": requested,
            "overage": max(0.0, requested),
            "error": f"Cost center '{cost_center_id}' not found.",
        }

    remaining_value = budget_record.get("remaining_budget", budget_record.get("remaining"))
    try:
        remaining_budget = float(remaining_value)
    except (TypeError, ValueError):
        return {
            "within_budget": False,
            "cost_center_id": cost_center_id,
            "remaining_budget": 0.0,
            "requested_amount": requested,
            "overage": max(0.0, requested),
            "error": f"Remaining budget unavailable for cost center '{cost_center_id}'.",
        }

    overage = max(0.0, requested - remaining_budget)
    return {
        "within_budget": overage == 0.0,
        "cost_center_id": cost_center_id,
        "remaining_budget": remaining_budget,
        "requested_amount": requested,
        "overage": overage,
    }
