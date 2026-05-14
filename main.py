"""Точка входа для движка интеграции данных."""

from __future__ import annotations

import logging
import sys
import tracemalloc
from pathlib import Path

from app.io.registry import ReaderRegistry
from app.services.aggregator import RecordAggregator
from app.services.engine import DataIntegrationEngine
from app.services.validator import RecordValidator
from app.services.writer import ResultWriter


def configure_logging(log_path: Path) -> logging.Logger:
    """Настраивает корневой логгер для записи сообщений в файл."""

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )
    return logging.getLogger("data_integration_engine")


def main() -> int:
    """Запускает приложение и возвращает код завершения процесса."""
    tracemalloc.start()

    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    output_path = project_root / "result.json"
    log_path = project_root / "app.log"

    if not data_dir.exists() or not data_dir.is_dir():
        print("Критическая ошибка: директория data отсутствует.")
        return 1

    logger = configure_logging(log_path)
    engine = DataIntegrationEngine(
        registry=ReaderRegistry(),
        validator=RecordValidator(),
        aggregator=RecordAggregator(),
        writer=ResultWriter(),
        logger=logger,
    )

    try:
        result = engine.run(data_dir, output_path)
    except OSError as error:
        logger.exception("Критическая ошибка файловой системы")
        print(f"Критическая ошибка: {error}")
        return 1

    print(
        f"Обработано файлов: {result.stats.processed_files}. "
        f"Успешно: {result.stats.successful_files}. "
        f"Ошибок: {result.stats.failed_files}."
    )

    if result.errors:
        print("Список ошибок:")
        for processing_error in result.errors:
            print(
                "- "
                f"{processing_error.file_path}: "
                f"{processing_error.error_type} -> "
                f"{processing_error.message}"
            )

    print(f"Результат сохранен в: {result.output_path}")
    print(f"Логи сохранены в: {log_path}")

    current, peak = tracemalloc.get_traced_memory()
    print(f"Peak Memory Usage: {peak / 1024 / 1024:.2f} MB")
    tracemalloc.stop()

    return 0


if __name__ == "__main__":
    sys.exit(main())
