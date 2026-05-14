"""Доменные модели приложения."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True, frozen=True)
class Transaction:
    """Провалидированная финансовая запись."""

    transaction_id: str
    amount: float
    category: str
    date: str
    currency: str | None = None
    source_file: str = ""


@dataclass(slots=True)
class ProcessingError:
    """Сведения об ошибке обработки."""

    file_path: str
    error_type: str
    message: str


@dataclass(slots=True)
class ProcessingStats:
    """Статистика выполнения всего запуска."""

    processed_files: int = 0
    successful_files: int = 0
    failed_files: int = 0


@dataclass(slots=True)
class ProcessingResult:
    """Результат выполнения интеграции."""

    stats: ProcessingStats = field(default_factory=ProcessingStats)
    errors: list[ProcessingError] = field(default_factory=list)
    output_path: Path | None = None
