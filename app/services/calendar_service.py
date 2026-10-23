import calendar
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
# --- константы вынесены FORGE refactor ---
CONST_9 = 9
CONST_12 = 12


MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    CONST_9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", CONST_12: "Декабрь"
}


def generate_calendar_keyboard(year: int = None, month: int = None) -> InlineKeyboardMarkup:
    """Генерация стильного интерактивного календаря."""
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    builder = InlineKeyboardBuilder()

    # Шапка: Месяц и Год
    builder.row(InlineKeyboardButton(
        text=f"🗓 {MONTHS_RU[month]} {year}",
        callback_data="ignore"
    ))

    # Дни недели
    days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    builder.row(*[InlineKeyboardButton(text=day, callback_data="ignore") for day in days_of_week])

    # Дни месяца
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                date_obj = datetime(year, month, day).date()
                # Прошедшие даты блокируем
                if date_obj < now.date():
                    row.append(InlineKeyboardButton(text="❌", callback_data="ignore"))
                else:
                    row.append(InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"cal_date_{year}_{month}_{day}"
                    ))
        builder.row(*row)

    # Навигация (Предыдущий / Следующий месяц)
    nav_buttons = []
    prev_month = month - 1 if month > 1 else CONST_12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < CONST_12 else 1
    next_year = year if month < CONST_12 else year + 1

    # Запрещаем отматывать календарь в прошлые месяцы
    if datetime(year, month, 1).date() > datetime(now.year, now.month, 1).date():
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"cal_nav_{prev_year}_{prev_month}"))
    else:
        nav_buttons.append(InlineKeyboardButton(text="⛔", callback_data="ignore"))

    nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"cal_nav_{next_year}_{next_month}"))
    builder.row(*nav_buttons)

    # Кнопка отмены
    builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking"))

    return builder.as_markup()


def generate_time_slots_keyboard(busy_slots: list) -> InlineKeyboardMarkup:
    """Генерация временных слотов с визуализацией доступности."""
    builder = InlineKeyboardBuilder()

    # Стандартные временные слоты с 09:00 до 18:00
    all_slots = [f"{hour:02d}:00" for hour in range(CONST_9, 19)]

    for slot in all_slots:
        if slot in busy_slots:
            builder.button(text=f"🔴 {slot} (Занято)", callback_data="ignore")
        else:
            builder.button(text=f"🟢 {slot}", callback_data=f"time_{slot}")

    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅ Выбрать другую дату", callback_data="go_to_calendar"))
    builder.row(InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking"))

    return builder.as_markup()