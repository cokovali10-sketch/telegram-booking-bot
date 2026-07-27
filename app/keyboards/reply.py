from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from app.config.settings import settings


def main_reply_keyboard(user_id: int | None = None) -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(text="📅 Записаться"),
            KeyboardButton(text="📋 Мои записи"),
        ],
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="ℹ️ О нас и FAQ"),
        ],
        [
            KeyboardButton(text="⭐ Оставить отзыв"),
            KeyboardButton(text="📞 Контакты"),
        ],
    ]

    if user_id is not None and user_id in settings.ADMIN_IDS:
        buttons.append([KeyboardButton(text="👑 Админ-панель")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие в меню...",
    )


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Поделиться контактом", request_contact=True)],
            [KeyboardButton(text="❌ Отменить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
