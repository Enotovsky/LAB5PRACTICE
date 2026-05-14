from __future__ import annotations

import pytest

from app.core.exceptions import ValidationError
from app.core.models import Transaction
from app.services.aggregator import RecordAggregator


def make_transaction(
    transaction_id: str,
    amount: float,
    category: str = "food",
) -> Transaction:
    return Transaction(
        transaction_id=transaction_id,
        amount=amount,
        category=category,
        date="2026-04-19",
        currency="RUB",
        source_file="operations.csv",
    )


def test_aggregator_groups_rounds_and_counts_transactions() -> None:
    aggregator = RecordAggregator()

    aggregator.add_transactions(
        [
            make_transaction("tx-001", 10.124, "food"),
            make_transaction("tx-002", 7.236, "food"),
            make_transaction("tx-003", 3.0, "books"),
        ]
    )

    assert aggregator.export_summary() == {
        "books": {"total_amount": 3.0, "transaction_count": 1},
        "food": {"total_amount": 17.36, "transaction_count": 2},
    }


def test_aggregator_ignores_identical_duplicate_transaction() -> None:
    aggregator = RecordAggregator()
    transaction = make_transaction("tx-001", 10.0)

    aggregator.add_transactions([transaction, transaction])

    assert aggregator.export_summary()["food"]["transaction_count"] == 1


def test_aggregator_rejects_conflicting_duplicate_transaction() -> None:
    aggregator = RecordAggregator()
    aggregator.add_transactions([make_transaction("tx-001", 10.0)])

    with pytest.raises(ValidationError):
        aggregator.add_transactions([make_transaction("tx-001", 99.0)])
