from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from app.io.registry import ReaderRegistry
from app.services.aggregator import RecordAggregator
from app.services.engine import DataIntegrationEngine
from app.services.validator import RecordValidator
from app.services.writer import ResultWriter


@pytest.fixture
def valid_record() -> dict[str, Any]:
    return {
        "id": "tx-001",
        "amount": "25.50",
        "category": "food",
        "date": "2026-04-19",
        "currency": "RUB",
    }


@pytest.fixture
def make_engine() -> Callable[[logging.Logger | None], DataIntegrationEngine]:
    def factory(logger: logging.Logger | None = None) -> DataIntegrationEngine:
        return DataIntegrationEngine(
            registry=ReaderRegistry(),
            validator=RecordValidator(),
            aggregator=RecordAggregator(),
            writer=ResultWriter(),
            logger=logger or logging.getLogger("tests.data_integration"),
        )

    return factory


@pytest.fixture
def csv_file(tmp_path: Path) -> Path:
    return tmp_path / "operations.csv"
