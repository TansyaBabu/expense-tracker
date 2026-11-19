from decimal import Decimal

import pytest

from expense_tracker.validation import (
    validate_amount,
    validate_category,
    validate_date,
    validate_date_range,
)


def test_validate_amount_valid() -> None:
    assert validate_amount("12.50") == Decimal("12.50")
    assert validate_amount("12.500") == Decimal("12.50")
    assert validate_amount("5") == Decimal("5.00")
    assert validate_amount(10) == Decimal("10.00")
    assert validate_amount(Decimal("9.99")) == Decimal("9.99")
    assert validate_amount("  42.10  ") == Decimal("42.10")


def test_validate_amount_zero() -> None:
    for zero_val in (0, "0", "0.00", Decimal("0")):
        with pytest.raises(ValueError, match="Amount must be a positive number."):
            validate_amount(zero_val)


def test_validate_amount_negative() -> None:
    for neg_val in ("-12.50", -5, Decimal("-0.01")):
        with pytest.raises(ValueError, match="Amount must be a positive number."):
            validate_amount(neg_val)


def test_validate_amount_invalid_format() -> None:
    with pytest.raises(
        ValueError,
        match="Float values are not allowed for money. Use Decimal, int, or str.",
    ):
        validate_amount(12.5)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Amount must be a valid number."):
        validate_amount(True)  # type: ignore[arg-type]

    for non_num in ("abc", "", "   ", "$12.50", "12,50"):
        with pytest.raises(ValueError, match="Amount must be a valid number."):
            validate_amount(non_num)

    for non_finite in ("NaN", "Infinity", "-Infinity"):
        with pytest.raises(ValueError, match="Amount must be a finite number."):
            validate_amount(non_finite)


def test_validate_amount_more_than_two_decimals() -> None:
    for too_many_decimals in ("12.555", "0.001", Decimal("1.234"), "99.9999"):
        with pytest.raises(
            ValueError, match="Amount cannot have more than 2 decimal places."
        ):
            validate_amount(too_many_decimals)


def test_validate_date_valid() -> None:
    assert validate_date("2026-11-19") == "2026-11-19"
    # Leap year accepted
    assert validate_date("2024-02-29") == "2024-02-29"


def test_validate_date_malformed() -> None:
    # Must reject non-matching formats including 2026-1-1
    for bad_fmt in ("2026-1-1", "2026/11/19", "19-11-2026", "not-a-date", ""):
        with pytest.raises(ValueError, match="Invalid date format"):
            validate_date(bad_fmt)


def test_validate_date_invalid_calendar() -> None:
    # Non-leap year Feb 29 rejected
    with pytest.raises(ValueError, match="Invalid calendar date"):
        validate_date("2025-02-29")

    for bad_cal in ("2026-02-31", "2026-04-31", "2026-13-01"):
        with pytest.raises(ValueError, match="Invalid calendar date"):
            validate_date(bad_cal)


def test_validate_category() -> None:
    # Return stripped value and assert it
    assert validate_category("food") == "food"
    assert validate_category("  groceries  ") == "groceries"

    for empty_cat in ("", "   ", "\t\n"):
        with pytest.raises(ValueError, match="Category cannot be empty."):
            validate_category(empty_cat)

    with pytest.raises(ValueError, match="Category must be a string."):
        validate_category(123)  # type: ignore[arg-type]


def test_validate_date_range() -> None:
    # Valid ranges
    validate_date_range("2026-11-01", "2026-11-30")
    validate_date_range("2026-11-19", "2026-11-19")
    validate_date_range("2026-11-01", None)
    validate_date_range(None, "2026-11-30")
    validate_date_range(None, None)

    # Inverted range
    with pytest.raises(ValueError, match="--from date .* cannot be after --to date .*"):
        validate_date_range("2026-11-30", "2026-11-01")

    # Malformed arguments checked before comparing
    with pytest.raises(ValueError, match="Invalid date format '2026-1-1'"):
        validate_date_range("2026-1-1", "2026-11-30")

    with pytest.raises(ValueError, match="Invalid calendar date '2026-02-31'"):
        validate_date_range("2026-02-01", "2026-02-31")
