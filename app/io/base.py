"""Базовые абстракции для чтения файлов."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class BaseReader(ABC):
    """Общий интерфейс обработчика чтения."""

    @abstractmethod
    def read(self, file_path: Path) -> Iterator[dict[str, Any]]:
        """Считывает сырые записи из файла."""
