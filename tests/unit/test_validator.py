from __future__ import annotations

from typing import Any

import pytest

from app.core.exceptions import InvalidTransactionError, ValidationError
from app.services.validator import RecordValidator


@pytest.mark.parametrize(
    ("field", "value", "is_valid"),
    [
        ("amount", "0.01", True),
        ("amount", 1_000_000_000_000, True),
        ("amount", "0", False),
        ("amount", "-0.01", False),
        ("amount", "abc", False),
        ("amount", None, False),
        ("amount", "1e309", False),
        ("date", "2026-02-28", True),
        ("date", "2026-02-30", False),
        ("date", "19.04.2026", False),
        ("id", "   ", False),
        ("category", "", False),
    ],
)
def test_validator_boundary_values(
    valid_record: dict[str, Any],
    field: str,
    value: Any,
    is_valid: bool,
) -> None:
    record = {**valid_record, field: value}
    validator = RecordValidator()

    if is_valid:
        transaction = validator.validate_one(record, "source.csv")

        assert transaction.transaction_id == record["id"].strip()
        assert transaction.amount > 0
        assert transaction.source_file == "source.csv"
    else:
        with pytest.raises(ValidationError):
            validator.validate_one(record, "source.csv")


def test_validator_raises_domain_error_for_garbage_row() -> None:
    validator = RecordValidator()

    with pytest.raises(InvalidTransactionError):
        validator.validate_one({"this": "is not a transaction"}, "trash.csv")
