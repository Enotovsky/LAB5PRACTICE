from __future__ import annotations

from app.core.models import Transaction


def test_transaction_model_is_value_object() -> None:
    first = Transaction(
        transaction_id="tx-001",
        amount=10.0,
        category="books",
        date="2026-04-19",
        currency="RUB",
        source_file="operations.csv",
    )
    second = Transaction(
        transaction_id="tx-001",
        amount=10.0,
        category="books",
        date="2026-04-19",
        currency="RUB",
        source_file="operations.csv",
    )

    assert first == second
