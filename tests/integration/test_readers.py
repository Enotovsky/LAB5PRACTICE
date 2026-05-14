from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.exceptions import DataFormatError
from app.io.csv_reader import CsvReader
from app.io.json_reader import JsonReader
from app.io.registry import ReaderRegistry


def test_csv_reader_reads_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "operations.csv"
    csv_path.write_text(
        "id,amount,category,date\n"
        "tx-001,10.5,food,2026-04-19\n",
        encoding="utf-8-sig",
    )

    assert list(CsvReader().read(csv_path)) == [
        {
            "id": "tx-001",
            "amount": "10.5",
            "category": "food",
            "date": "2026-04-19",
        }
    ]


def test_csv_reader_rejects_empty_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(DataFormatError):
        list(CsvReader().read(csv_path))


def test_json_reader_accepts_records_object(tmp_path: Path) -> None:
    json_path = tmp_path / "operations.json"
    payload = {
        "records": [
            {
                "id": "tx-001",
                "amount": 10.5,
                "category": "food",
                "date": "2026-04-19",
            }
        ]
    }
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    assert list(JsonReader().read(json_path)) == payload["records"]


@pytest.mark.parametrize("payload", [{}, [], "wrong", [1]])
def test_json_reader_rejects_invalid_payloads(tmp_path: Path, payload) -> None:
    json_path = tmp_path / "bad.json"
    json_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(DataFormatError):
        list(JsonReader().read(json_path))


def test_registry_rejects_unknown_extension(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"

    with pytest.raises(DataFormatError):
        ReaderRegistry().get_reader(file_path)
