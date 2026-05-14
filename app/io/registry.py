"""Реестр обработчиков по расширению файла."""

from __future__ import annotations

from pathlib import Path

from app.core.exceptions import DataFormatError
from app.io.base import BaseReader
from app.io.csv_reader import CsvReader
from app.io.json_reader import JsonReader


class ReaderRegistry:
    """Возвращает reader по расширению файла."""

    def __init__(self) -> None:
        self._readers: dict[str, BaseReader] = {
            ".csv": CsvReader(),
            ".json": JsonReader(),
        }

    def get_reader(self, file_path: Path) -> BaseReader:
        try:
            return self._readers[file_path.suffix.lower()]
        except KeyError as error:
            raise DataFormatError(
                "Неподдерживаемое расширение файла: "
                f"{file_path.suffix or '<без расширения>'}."
            ) from error
