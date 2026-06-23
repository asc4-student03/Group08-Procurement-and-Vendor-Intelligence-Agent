"""Compatibility loader that delegates to project-root data.loader."""

from __future__ import annotations

from data.loader import (
    load_budgets as _load_budgets,
    load_policies as _load_policies,
    load_requests as _load_requests,
    load_vendors as _load_vendors,
)


def load_budgets() -> list[dict[str, object]]:
    """Return all cost center budget records."""
    return _load_budgets()


def load_vendors() -> list[dict[str, object]]:
    """Return all vendor records."""
    return _load_vendors()


def load_policies() -> list[dict[str, object]]:
    """Return all procurement policy records."""
    return _load_policies()


def load_requests() -> list[dict[str, object]]:
    """Return all sample purchase request records."""
    return _load_requests()
