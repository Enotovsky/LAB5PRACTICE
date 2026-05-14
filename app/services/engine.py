"""Оркестрация процесса интеграции."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from app.core.exceptions import BaseAppError, ValidationError
from app.core.models import ProcessingError, ProcessingResult, Transaction
from app.io.registry import ReaderRegistry
from app.services.aggregator import RecordAggregator
from app.services.validator import RecordValidator
from app.services.writer import ResultWriter


class DataIntegrationEngine:
    """Координирует чтение, валидацию и экспорт."""

    def __init__(
        self,
        registry: ReaderRegistry,
        validator: RecordValidator,
        aggregator: RecordAggregator,
        writer: ResultWriter,
        logger: logging.Logger,
    ) -> None:
        self._registry = registry
        self._validator = validator
        self._aggregator = aggregator
        self._writer = writer
        self._logger = logger

    def _process_records(
        self,
        raw_records: Iterator[dict[str, Any]],
        file_path: Path,
        result: ProcessingResult,
    ) -> Iterator[Transaction]:
        for row_number, raw_record in enumerate(raw_records, start=1):
            try:
                yield self._validator.validate_one(
                    raw_record,
                    file_path.name,
                )
            except ValidationError as error:
                self._logger.error(
                    "Невалидная запись %s:%s: %s",
                    file_path,
                    row_number,
                    error,
                )
                result.errors.append(
                    ProcessingError(
                        file_path=f"{file_path}:{row_number}",
                        error_type=type(error).__name__,
                        message=str(error),
                    )
                )

    def run(self, data_dir: Path, output_path: Path) -> ProcessingResult:
        result = ProcessingResult()

        files = sorted(path for path in data_dir.iterdir() if path.is_file())

        for file_path in files:
            result.stats.processed_files += 1

            try:
                reader = self._registry.get_reader(file_path)
                raw_records = reader.read(file_path)
                transactions = self._process_records(raw_records, file_path, result)
                self._aggregator.add_transactions(transactions)
            except BaseAppError as error:
                self._logger.error(
                    "Не удалось обработать %s: %s",
                    file_path,
                    error,
                )
                result.errors.append(
                    ProcessingError(
                        file_path=str(file_path),
                        error_type=type(error).__name__,
                        message=(
                            str(error)
                        ),
                    )
                )
                result.stats.failed_files += 1
                continue
            except Exception as error:  # pragma: no cover
                self._logger.exception(
                    "Непредвиденная ошибка "
                    "при обработке %s",
                    file_path,
                )
                result.errors.append(
                    ProcessingError(
                        file_path=str(file_path),
                        error_type=type(error).__name__,
                        message=(
                            "Непредвиденная "
                            "ошибка обработки."
                        ),
                    )
                )
                result.stats.failed_files += 1
                continue

            result.stats.successful_files += 1

        summary = self._aggregator.export_summary()
        try:
            self._writer.write(output_path, summary)
        except OSError as error:
            self._logger.exception(
                "Не удалось сохранить результат %s",
                output_path,
            )
            result.errors.append(
                ProcessingError(
                    file_path=str(output_path),
                    error_type=type(error).__name__,
                    message=str(error),
                )
            )
            result.output_path = output_path
            return result

        result.output_path = output_path
        return result
