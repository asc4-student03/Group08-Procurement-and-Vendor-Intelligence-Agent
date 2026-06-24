"""Budget check tool for procurement request pre-screening."""

from __future__ import annotations

from data import loader


def _typed_error(error: Exception, stage: str) -> dict[str, str]:
    """Build a consistent typed error payload for tool responses."""
    return {
        "type": type(error).__name__,
        "message": str(error),
        "stage": stage,
    }


def check_budget(cost_center_id: str, requested_amount: float) -> dict[str, object]:
    """Evaluate whether a purchase request exceeds remaining quarterly budget.

    Args:
        cost_center_id: Cost center identifier from the purchase request.
        requested_amount: Request total amount in USD.

    Returns:
        A standard tool payload:
        {
          "signal": "approve|deny|escalate",
          "summary": str,
          "details": {
            "cost_center_id": str,
            "remaining_budget": float,
            "total_amount": float,
            "overage": float
          }
        }
        In data-lookup error cases, includes an additional "error" key.
    """
    try:
        budgets = loader.load_budgets()
    except FileNotFoundError as exc:
        return {
            "signal": "escalate",
            "summary": "Budget data file missing; escalate for manual review.",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": 0.0,
                "total_amount": float(requested_amount),
                "overage": float(requested_amount),
            },
            "error": _typed_error(exc, "data_load"),
        }
    except KeyError as exc:
        return {
            "signal": "escalate",
            "summary": "Budget data missing required fields; escalate for manual review.",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": 0.0,
                "total_amount": float(requested_amount),
                "overage": float(requested_amount),
            },
            "error": _typed_error(exc, "data_shape"),
        }
    except Exception as exc:
        return {
            "signal": "escalate",
            "summary": "Unexpected budget check failure; escalate for manual review.",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": 0.0,
                "total_amount": float(requested_amount),
                "overage": float(requested_amount),
            },
            "error": _typed_error(exc, "unexpected"),
        }

    record = next(
        (item for item in budgets if item.get("cost_center_id") == cost_center_id),
        None,
    )

    if record is None:
        return {
            "signal": "escalate",
            "summary": "Cost center not found in budget records; escalate for manual review.",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": 0.0,
                "total_amount": float(requested_amount),
                "overage": float(requested_amount),
            },
            "error": {
                "type": "ReferenceDataError",
                "message": f"Unknown cost_center_id: {cost_center_id}",
                "stage": "lookup",
            },
        }

    try:
        remaining = float(record["remaining"])
        amount = float(requested_amount)
        overage = max(0.0, round(amount - remaining, 2))
    except KeyError as exc:
        return {
            "signal": "escalate",
            "summary": "Budget record missing required fields; escalate for manual review.",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": 0.0,
                "total_amount": float(requested_amount),
                "overage": float(requested_amount),
            },
            "error": _typed_error(exc, "data_shape"),
        }
    except Exception as exc:
        return {
            "signal": "escalate",
            "summary": "Unexpected budget check failure; escalate for manual review.",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": 0.0,
                "total_amount": float(requested_amount),
                "overage": float(requested_amount),
            },
            "error": _typed_error(exc, "unexpected"),
        }

    if overage > 0:
        return {
            "signal": "deny",
            "summary": "Request exceeds remaining quarterly budget (POL-008).",
            "details": {
                "cost_center_id": cost_center_id,
                "remaining_budget": round(remaining, 2),
                "total_amount": round(amount, 2),
                "overage": overage,
            },
        }

    return {
        "signal": "approve",
        "summary": "Request is within remaining quarterly budget.",
        "details": {
            "cost_center_id": cost_center_id,
            "remaining_budget": round(remaining, 2),
            "total_amount": round(amount, 2),
            "overage": 0.0,
        },
    }
