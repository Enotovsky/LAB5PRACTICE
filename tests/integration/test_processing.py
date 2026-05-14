from __future__ import annotations

import json
import logging
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

from app.services.engine import DataIntegrationEngine
from app.services.writer import ResultWriter


def test_processor_keeps_only_valid_csv_rows(
    tmp_path: Path,
    csv_file: Path,
    make_engine: Callable[[logging.Logger | None], DataIntegrationEngine],
) -> None:
    csv_file.write_text(
        "\n".join(
            [
                "id,amount,category,date,currency",
                "tx-001,10.50,food,2026-04-19,RUB",
                "tx-002,0,food,2026-04-19,RUB",
                "tx-003,12.00,food,not-a-date,RUB",
            ]
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "result.json"

    result = make_engine().run(tmp_path, output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload == {"food": {"total_amount": 10.5, "transaction_count": 1}}
    assert result.stats.processed_files == 1
    assert result.stats.successful_files == 1
    assert len(result.errors) == 2


def test_writer_error_is_logged_without_crashing(
    tmp_path: Path,
    csv_file: Path,
    make_engine: Callable[[logging.Logger | None], DataIntegrationEngine],
    caplog,
) -> None:
    csv_file.write_text(
        "\n".join(
            [
                "id,amount,category,date,currency",
                "tx-001,10.50,food,2026-04-19,RUB",
            ]
        ),
        encoding="utf-8",
    )
    logger = logging.getLogger("tests.writer_error")

    with caplog.at_level(logging.ERROR, logger=logger.name):
        with patch.object(
            ResultWriter,
            "write",
            side_effect=PermissionError("disk is write-protected"),
        ):
            result = make_engine(logger).run(tmp_path, tmp_path / "result.json")

    assert result.output_path == tmp_path / "result.json"
    assert result.errors[-1].error_type == "PermissionError"
    assert "disk is write-protected" in result.errors[-1].message
    assert "Не удалось сохранить результат" in caplog.text
