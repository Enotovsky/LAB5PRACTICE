"""Чтение JSON-файлов."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from app.core.exceptions import DataFormatError
from app.io.base import BaseReader


class JsonReader(BaseReader):
    """Считывает данные из JSON-файлов."""

    def read(self, file_path: Path) -> Iterator[dict[str, Any]]:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
        except UnicodeDecodeError as error:
            raise DataFormatError(
                "JSON-файл не является "
                "корректным UTF-8 текстом."
            ) from error
        except json.JSONDecodeError as error:
            raise DataFormatError(
                f"Некорректный JSON: {error.msg}."
            ) from error
        except OSError as error:
            raise DataFormatError(
                f"Не удалось прочитать JSON-файл: {error}"
            ) from error

        if isinstance(payload, dict):
            records = payload.get("records")
            if records is None:
                raise DataFormatError(
                    "JSON-объект должен "
                    "содержать поле 'records'."
                )
        elif isinstance(payload, list):
            records = payload
        else:
            raise DataFormatError(
                "Корень JSON должен быть списком "
                "или объектом с полем 'records'."
            )

        if not isinstance(records, list) or not records:
            raise DataFormatError("JSON-файл не содержит записей.")

        for item in records:
            if not isinstance(item, dict):
                raise DataFormatError(
                    "Каждая JSON-запись "
                    "должна быть объектом."
                )
            yield item
