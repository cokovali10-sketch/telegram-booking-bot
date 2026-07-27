from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📅 Записаться")
        ],
        [
            KeyboardButton(text="📋 Мои записи")
        ],
        [
            KeyboardButton(text="📞 Контакты")
        ],
        [
            KeyboardButton(text="👑 Админ")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)