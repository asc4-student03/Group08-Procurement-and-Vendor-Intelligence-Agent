"""Tests for centralized mock data loader functions."""

from pathlib import Path

import pytest

import data.loader as loader


def test_loader_success_paths_return_lists() -> None:
    """Each loader function should return parsed list data for existing datasets."""
    assert isinstance(loader.load_budgets(), list)
    assert isinstance(loader.load_vendors(), list)
    assert isinstance(loader.load_policies(), list)
    assert isinstance(loader.load_requests(), list)


def test_loader_raises_when_dataset_is_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Loader should raise a detectable file error when required files are missing."""
    monkeypatch.setattr(loader, "MOCK_DATA_DIR", Path("__missing_mock_data_dir__"))

    with pytest.raises(FileNotFoundError):
        loader.load_budgets()
