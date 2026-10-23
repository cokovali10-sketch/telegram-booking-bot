from aiogram.utils.keyboard import InlineKeyboardBuilder


def services_keyboard(services):

    builder = InlineKeyboardBuilder()

    for service in services:

        builder.button(
            text=f"{service[1]} • {service[2]}₸",
            callback_data=f"service_{service[0]}"
        )

    builder.adjust(1)

    return builder.as_markup()


def employees_keyboard(employees):

    builder = InlineKeyboardBuilder()

    for employee in employees:

        builder.button(
            text=employee[1],
            callback_data=f"employee_{employee[0]}"
        )

    builder.adjust(1)

    return builder.as_markup()


def time_keyboard():

    builder = InlineKeyboardBuilder()

    times = [

        "09:00",
        "10:00",
        "11:00",
        "12:00",

        "13:00",
        "14:00",
        "15:00",
        "16:00",

        "17:00",
        "18:00",
        "19:00",
        "20:00"

    ]

    for time in times:

        builder.button(
            text=time,
            callback_data=f"time_{time}"
        )

    builder.adjust(3)

    return builder.as_markup()


def admin_keyboard():

    builder = InlineKeyboardBuilder()

    builder.button(
        text="📊 Статистика",
        callback_data="admin_stats"
    )

    builder.button(
        text="📋 Все записи",
        callback_data="admin_bookings"
    )

    builder.button(
        text="➕ Добавить услугу",
        callback_data="admin_add_service"
    )

    builder.button(
        text="➕ Добавить сотрудника",
        callback_data="admin_add_employee"
    )

    builder.button(
        text="📤 Экспорт Excel",
        callback_data="admin_export"
    )

    builder.button(
        text="⚙ Настройки",
        callback_data="admin_settings"
    )

    builder.adjust(1)

    return builder.as_markup()