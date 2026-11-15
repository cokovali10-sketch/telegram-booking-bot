from datetime import date, datetime, timedelta, timezone

import pytest

from app.utils.exceptions import ValidationError
from app.utils.validators import (
    normalize_phone,
    validate_booking_date,
    validate_booking_datetime,
    validate_duration,
    validate_phone,
    validate_price,
    validate_time_slot,
    validate_title,
)


def test_normalize_phone_strips_formatting():
    assert normalize_phone("+7 (999) 123-45-67") == "+79991234567"


def test_validate_phone_accepts_normalized_number():
    assert validate_phone("+79991234567") == "+79991234567"


def test_validate_phone_rejects_short_number():
    with pytest.raises(ValidationError):
        validate_phone("+7999")


def test_validate_time_slot_accepts_half_hour_steps():
    assert validate_time_slot("09:30") == "09:30"
    assert validate_time_slot("18:00") == "18:00"


def test_validate_time_slot_rejects_out_of_range():
    with pytest.raises(ValidationError):
        validate_time_slot("25:00")


def test_validate_booking_date_parses_iso():
    assert validate_booking_date("2026-12-01") == date(2026, 12, 1)


def test_validate_booking_date_rejects_garbage():
    with pytest.raises(ValidationError):
        validate_booking_date("01.12.2026")


def test_validate_booking_datetime_combines_parts():
    future = datetime.now(timezone.utc) + timedelta(days=30)
    assert validate_booking_datetime(future.strftime("%Y-%m-%d"), "10:00").tzinfo is not None


def test_validate_price_requires_digits():
    assert validate_price("1500") == 1500
    with pytest.raises(ValidationError):
        validate_price("abc")


def test_validate_duration_range():
    assert validate_duration("60") == 60
    with pytest.raises(ValidationError):
        validate_duration("0")


def test_validate_title_strips_and_checks_length():
    assert validate_title("  Haircut  ") == "Haircut"
    with pytest.raises(ValidationError):
        validate_title("")