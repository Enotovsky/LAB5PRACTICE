"""Сервис агрегации данных."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from app.core.exceptions import ValidationError
from app.core.models import Transaction


class RecordAggregator:
    """Агрегирует записи."""

    def __init__(self) -> None:
        self._seen_transactions: dict[str, int] = {}
        self._category_totals: dict[str, float] = defaultdict(float)
        self._category_counts: dict[str, int] = defaultdict(int)

    def add_transactions(self, transactions: Iterable[Transaction]) -> None:
        for transaction in transactions:
            self._add_transaction(transaction)

    def export_summary(self) -> dict[str, dict[str, float | int]]:
        return {
            category: {
                "total_amount": round(self._category_totals[category], 2),
                "transaction_count": self._category_counts[category],
            }
            for category in sorted(self._category_totals.keys())
        }

    def _add_transaction(self, transaction: Transaction) -> None:
        tx_hash = hash(transaction)
        existing_hash = self._seen_transactions.get(transaction.transaction_id)

        if existing_hash is not None:
            if existing_hash != tx_hash:
                raise ValidationError(
                    "Обнаружен конфликтующий "
                    "дубликат id: "
                    f"{transaction.transaction_id}."
                )
            return

        self._seen_transactions[transaction.transaction_id] = tx_hash
        self._category_totals[transaction.category] += transaction.amount
        self._category_counts[transaction.category] += 1
