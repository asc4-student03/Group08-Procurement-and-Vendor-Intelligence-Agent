"""Load mock procurement datasets from the project mock_data directory."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MOCK_DATA_DIR = PROJECT_ROOT / "mock_data"


def _load_json_list(file_name: str) -> list[Any]:
    """Load and parse a JSON file from mock_data and return its list content."""
    file_path = MOCK_DATA_DIR / file_name
    with file_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list):
        raise ValueError(f"Expected list data in {file_path}")

    return data


def load_budgets() -> list[Any]:
    """Load budget records from mock_data/budgets.json."""
    return _load_json_list("budgets.json")


def load_vendors() -> list[Any]:
    """Load vendor records from mock_data/vendors.json."""
    return _load_json_list("vendors.json")


def load_policies() -> list[Any]:
    """Load policy records from mock_data/policies.json."""
    return _load_json_list("policies.json")


def load_requests() -> list[Any]:
    """Load purchase request records from mock_data/requests.json."""
    return _load_json_list("requests.json")