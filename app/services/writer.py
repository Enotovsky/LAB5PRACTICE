"""Безопасная запись результатов интеграции."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ResultWriter:
    """Сохраняет результат атомарно."""

    def write(self, output_path: Path, payload: dict[str, Any]) -> None:
        temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        temporary_path.replace(output_path)
