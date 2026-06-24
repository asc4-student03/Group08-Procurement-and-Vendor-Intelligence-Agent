from pathlib import Path

import pytest

from data import loader


def test_load_requests_returns_records() -> None:
    records = loader.load_requests()
    assert isinstance(records, list)
    assert len(records) > 0
    assert "request_id" in records[0]


def test_load_raises_for_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        loader._load("missing-file.json")


def test_load_raises_for_non_list_payload(tmp_path: Path, monkeypatch) -> None:
    bad_path = tmp_path / "bad.json"
    bad_path.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(loader, "_MOCK_DATA_DIR", tmp_path)

    with pytest.raises(TypeError):
        loader._load("bad.json")
