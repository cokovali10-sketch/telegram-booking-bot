from __future__ import annotations

import re
from datetime import date, datetime, timezone

from app.utils.exceptions import ValidationError
# --- константы вынесены FORGE refactor ---
CONST_11 = 11


PHONE_PATTERN = re.compile(r"^\+?[0-9]{10,15}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def normalize_phone(raw_phone: str) -> str:
    cleaned = re.sub(r"[\s\-()]", "", raw_phone.strip())
    if cleaned.startswith("8") and len(cleaned) == CONST_11:
        cleaned = f"+7{cleaned[1:]}"
    if cleaned.isdigit() and len(cleaned) == CONST_11 and cleaned.startswith("7"):
        cleaned = f"+{cleaned}"
    return cleaned


def validate_phone(raw_phone: str) -> str:
    phone = normalize_phone(raw_phone)
    if not PHONE_PATTERN.match(phone):
        raise ValidationError(
            f"Invalid phone: {raw_phone}",
            user_message=(
                "❌ Неверный формат телефона.\n"
                "Введите номер в формате +79991234567 или нажмите «Поделиться контактом»."
            ),
        )
    return phone


def validate_time_slot(time_str: str) -> str:
    if not TIME_PATTERN.match(time_str):
        raise ValidationError(
            f"Invalid time: {time_str}",
            user_message="❌ Неверный формат времени. Выберите слот из списка.",
        )
    return time_str


def validate_booking_date(date_str: str) -> date:
    try:
        booking_date = date.fromisoformat(date_str)
    except ValueError as exc:
        raise ValidationError(
            f"Invalid date: {date_str}",
            user_message="❌ Неверная дата. Выберите дату в календаре.",
        ) from exc

    if booking_date < datetime.now(timezone.utc).date():
        raise ValidationError(
            f"Past date: {date_str}",
            user_message="❌ Нельзя записаться на прошедшую дату.",
        )
    return booking_date


def validate_booking_datetime(date_str: str, time_str: str) -> datetime:
    booking_date = validate_booking_date(date_str)
    time_slot = validate_time_slot(time_str)
    hour, minute = map(int, time_slot.split(":"))
    booking_time = datetime(
        booking_date.year,
        booking_date.month,
        booking_date.day,
        hour,
        minute,
        tzinfo=timezone.utc,
    )
    if booking_time <= datetime.now(timezone.utc):
        raise ValidationError(
            f"Past datetime: {date_str} {time_str}",
            user_message="❌ Нельзя записаться на прошедшее время.",
        )
    return booking_time


def validate_price(raw_price: str) -> int:
    if not raw_price.isdigit():
        raise ValidationError(
            f"Invalid price: {raw_price}",
            user_message="❌ Стоимость должна быть положительным числом.",
        )
    price = int(raw_price)
    if price <= 0:
        raise ValidationError(
            f"Non-positive price: {price}",
            user_message="❌ Стоимость должна быть больше нуля.",
        )
    return price


def validate_duration(raw_duration: str) -> int:
    if not raw_duration.isdigit():
        raise ValidationError(
            f"Invalid duration: {raw_duration}",
            user_message="❌ Длительность указывается в минутах (число).",
        )
    duration = int(raw_duration)
    if duration <= 0 or duration > 480:
        raise ValidationError(
            f"Invalid duration value: {duration}",
            user_message="❌ Длительность должна быть от 1 до 480 минут.",
        )
    return duration


def validate_title(raw_title: str, field_name: str = "название") -> str:
    title = raw_title.strip()
    if len(title) < 2:
        raise ValidationError(
            f"Title too short: {raw_title}",
            user_message=f"❌ {field_name.capitalize()} должно содержать минимум 2 символа.",
        )
    if len(title) > 255:
        raise ValidationError(
            f"Title too long: {raw_title}",
            user_message=f"❌ {field_name.capitalize()} слишком длинное (макс. 255 символов).",
        )
    return title
