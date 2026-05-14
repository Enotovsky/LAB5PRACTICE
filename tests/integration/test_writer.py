from __future__ import annotations

import json
from pathlib import Path

from app.services.writer import ResultWriter


def test_writer_saves_json_payload(tmp_path: Path) -> None:
    output_path = tmp_path / "result.json"
    payload = {"food": {"total_amount": 10.5, "transaction_count": 1}}

    ResultWriter().write(output_path, payload)

    assert json.loads(output_path.read_text(encoding="utf-8")) == payload
    assert not output_path.with_suffix(".json.tmp").exists()
