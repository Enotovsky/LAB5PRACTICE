"""Сервис валидации сырых записей."""

from __future__ import annotations

import math
from datetime import date
from typing import Any

from app.core.exceptions import CurrencyMismatchError, InvalidTransactionError
from app.core.models import Transaction

REQUIRED_FIELDS = ("id", "amount", "category", "date")


class RecordValidator:
    """Проверяет записи и создает модели."""

    def validate_many(
        self,
        records: list[dict[str, Any]],
        source_file: str,
    ) -> list[Transaction]:
        currencies = {
            str(record.get("currency")).strip()
            for record in records
            if record.get("currency") not in (None, "")
        }
        if len(currencies) > 1:
            raise CurrencyMismatchError(
                "Отчет содержит смешанные валюты: "
                f"{', '.join(sorted(currencies))}."
            )

        return [self.validate_one(record, source_file) for record in records]

    def validate_one(self, record: dict[str, Any], source_file: str) -> Transaction:
        missing_fields = [field for field in REQUIRED_FIELDS if field not in record]
        if missing_fields:
            raise InvalidTransactionError(
                "Отсутствуют обязательные поля: "
                f"{', '.join(sorted(missing_fields))}."
            )

        transaction_id = str(record["id"]).strip()
        category = str(record["category"]).strip()
        raw_date = str(record["date"]).strip()
        currency = self._normalize_optional(record.get("currency"))

        if not transaction_id:
            raise InvalidTransactionError(
                "Поле 'id' не должно быть пустым."
            )
        if not category:
            raise InvalidTransactionError(
                "Поле 'category' не должно быть пустым."
            )

        try:
            amount = float(record["amount"])
        except (TypeError, ValueError) as error:
            raise InvalidTransactionError(
                "Поле 'amount' должно быть "
                "положительным числом."
            ) from error

        if not math.isfinite(amount) or amount <= 0:
            raise InvalidTransactionError(
                "Поле 'amount' должно быть больше нуля."
            )

        try:
            date.fromisoformat(raw_date)
        except ValueError as error:
            raise InvalidTransactionError(
                "Поле 'date' должно быть "
                "в ISO-формате YYYY-MM-DD."
            ) from error

        return Transaction(
            transaction_id=transaction_id,
            amount=amount,
            category=category,
            date=raw_date,
            currency=currency,
            source_file=source_file,
        )

    @staticmethod
    def _normalize_optional(value: Any) -> str | None:
        if value in (None, ""):
            return None
        return str(value).strip() or None
