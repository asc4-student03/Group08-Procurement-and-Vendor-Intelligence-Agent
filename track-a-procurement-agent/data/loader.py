"""Mock data loader for purchase requests, vendors, budgets, and policies."""

from __future__ import annotations

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_MOCK_DATA_DIR = _PROJECT_ROOT / "mock_data"


def _load(filename: str) -> list[dict[str, object]]:
    """Read a mock_data JSON file and return its records as a list."""
    path = _MOCK_DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Mock data file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise TypeError(f"Expected list data in {path}, got {type(data).__name__}")
    return data


def load_requests() -> list[dict[str, object]]:
    """Load and return purchase request records from mock_data/requests.json."""
    return _load("requests.json")


def load_policies() -> list[dict[str, object]]:
    """Load and return policy records from mock_data/policies.json."""
    return _load("policies.json")


def load_vendors() -> list[dict[str, object]]:
    """Load and return vendor records from mock_data/vendors.json."""
    return _load("vendors.json")


def load_budgets() -> list[dict[str, object]]:
    """Load and return budget records from mock_data/budgets.json."""
    return _load("budgets.json")
