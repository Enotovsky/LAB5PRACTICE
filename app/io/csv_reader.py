"""Чтение CSV-файлов."""

from __future__ import annotations

import csv
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from app.core.exceptions import DataFormatError
from app.io.base import BaseReader


class CsvReader(BaseReader):
    """Считывает данные из CSV-файлов."""

    def read(self, file_path: Path) -> Iterator[dict[str, Any]]:
        has_data = False
        try:
            with file_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames:
                    raise DataFormatError(
                        "CSV-файл пуст "
                        "или не содержит заголовков."
                    )

                for row in reader:
                    has_data = True
                    yield dict(row)
        except UnicodeDecodeError as error:
            raise DataFormatError(
                "CSV-файл не является "
                "корректным UTF-8 текстом."
            ) from error
        except OSError as error:
            raise DataFormatError(
                f"Не удалось прочитать CSV-файл: {error}"
            ) from error

        if not has_data:
            raise DataFormatError(
                "CSV-файл не содержит строк с данными."
            )
