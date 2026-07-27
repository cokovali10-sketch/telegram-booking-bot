from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.database import requests as db
from app.database.session import get_session
from app.keyboards import inline
from app.keyboards.reply import main_reply_keyboard
from app.utils.formatters import booking_to_keyboard_item, format_booking_card, format_user_profile

logger = logging.getLogger(__name__)

router = Router()


class UserStates(StatesGroup):
    edit_name = State()
    edit_phone = State()
    enter_review_comment = State()


@router.message(CommandStart())
async def start_cmd(message: Message) -> None:
    try:
        async with get_session() as session:
            user, created = await db.get_or_create_user(
                session,
                tg_id=message.from_user.id,
                full_name=message.from_user.full_name or "Пользователь",
                username=message.from_user.username,
                phone=None,
            )
        logger.info(
            "User %s (%s)",
            "registered" if created else "updated",
            user.tg_id,
        )
    except Exception as e:
        logger.exception("Failed to register user tg_id=%s: %s", message.from_user.id, e)
        await message.answer(
            "❌ Не удалось сохранить профиль. Попробуйте позже или нажмите /start снова."
        )
        return

    welcome_text = (
        f"<b>Привет, {message.from_user.first_name}! 👋</b>\n\n"
        "Добро пожаловать в наш онлайн-сервис бронирования!\n"
        "Здесь вы можете выбрать услугу, удобное время и любимого мастера за пару кликов.\n\n"
        "✨ <b>Доступные функции:</b>\n"
        "• 📅 <b>Записаться</b> — Выбор категории, услуги, мастера и слота\n"
        "• 📋 <b>Мои записи</b> — Просмотр, перенос и отмена броней\n"
        "• 👤 <b>Профиль</b> — Ваши данные и история\n"
        "• 🏷 <b>Промокоды</b> — Скидки на услуги\n"
        "• ⭐ <b>Отзывы</b> — Оценка качества работы мастеров\n\n"
        "Выберите действие в меню ниже:"
    )

    await message.answer(
        welcome_text,
        reply_markup=main_reply_keyboard(message.from_user.id),
        parse_mode="HTML",
    )


@router.message(F.text == "👤 Профиль")
async def user_profile_handler(message: Message) -> None:
    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, message.from_user.id)
        if not user:
            await message.answer("❌ Профиль не найден. Нажмите /start.")
            return
        user_bookings = await db.get_user_all_bookings(session, user.id)

    profile_text = format_user_profile(user, len(user_bookings))
    await message.answer(
        profile_text,
        reply_markup=inline.profile_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "edit_profile_name")
async def start_edit_name(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserStates.edit_name)
    await callback.message.edit_text("<b>✏ Введите ваше новое имя:</b>", parse_mode="HTML")
    await callback.answer()


@router.message(UserStates.edit_name)
async def process_edit_name(message: Message, state: FSMContext) -> None:
    new_name = message.text.strip()
    if len(new_name) < 2:
        await message.answer("❌ Имя слишком короткое. Введите хотя бы 2 символа:")
        return

    async with get_session() as session:
        await db.update_user_name(session, message.from_user.id, new_name)

    await state.clear()
    await message.answer(f"✅ Имя успешно обновлено на: <b>{new_name}</b>", parse_mode="HTML")


@router.callback_query(F.data == "edit_profile_phone")
async def start_edit_phone(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(UserStates.edit_phone)
    await callback.message.edit_text(
        "<b>📱 Введите ваш новый номер телефона (например, +77001234567):</b>", parse_mode="HTML"
    )
    await callback.answer()


@router.message(UserStates.edit_phone)
async def process_edit_phone(message: Message, state: FSMContext) -> None:
    phone = message.text.strip()
    async with get_session() as session:
        await db.update_user_phone(session, message.from_user.id, phone)

    await state.clear()
    await message.answer(f"✅ Номер телефона обновлен: <b>{phone}</b>", parse_mode="HTML")


@router.message(F.text.in_({"📋 Мои записи", "/my_bookings"}))
@router.callback_query(F.data.in_({"view_my_bookings", "back_to_my_bookings"}))
async def my_bookings_handler(event: Message | CallbackQuery) -> None:
    user_id = event.from_user.id
    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, user_id)
        if not user:
            msg = "❌ Профиль не найден. Нажмите /start."
            if isinstance(event, Message):
                await event.answer(msg)
            else:
                await event.message.answer(msg)
            return

        bookings = await db.get_user_all_bookings(session, user.id)

    if not bookings:
        text = "<b>📋 У вас пока нет ни одной записи.</b>\nНажмите «📅 Записаться», чтобы сделать первую запись!"
        if isinstance(event, Message):
            await event.answer(text, parse_mode="HTML")
        else:
            await event.message.edit_text(text, parse_mode="HTML")
            await event.answer()
        return

    items = [booking_to_keyboard_item(b) for b in bookings]
    text = "<b>📋 Ваши записи:</b>\nВыберите запись из списка ниже для управления:"

    if isinstance(event, Message):
        await event.answer(text, reply_markup=inline.my_bookings_keyboard(items), parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=inline.my_bookings_keyboard(items), parse_mode="HTML")
        await event.answer()


@router.callback_query(F.data.startswith("view_booking_"))
async def view_booking_detail(callback: CallbackQuery) -> None:
    booking_id = int(callback.data.split("_")[2])
    async with get_session() as session:
        booking = await db.get_booking_by_id(session, booking_id)

    if not booking:
        await callback.answer("Запись не найдена", show_alert=True)
        return

    card_text = format_booking_card(booking)
    has_review = booking.review is not None
    await callback.message.edit_text(
        card_text,
        reply_markup=inline.booking_detail_keyboard(booking.id, booking.status, has_review),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(F.text == "ℹ️ О нас и FAQ")
async def faq_handler(message: Message) -> None:
    text = (
        "<b>ℹ️ Информация о нашем сервисе</b>\n\n"
        "Мы предоставляем профессиональные услуги высокого качества с индивидуальным подходом.\n\n"
        "📍 <b>Адрес:</b> г. Алматы, пр. Абая 150/1\n"
        "📞 <b>Телефон:</b> +7 (700) 123-45-67\n"
        "🕒 <b>График работы:</b> Ежедневно с 09:00 до 20:00\n\n"
        "Выберите вопрос ниже для получения подробной информации:"
    )
    await message.answer(text, reply_markup=inline.faq_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("faq_"))
async def process_faq_callbacks(callback: CallbackQuery) -> None:
    topic = callback.data.split("_")[1]
    answers = {
        "hours": "🕒 <b>Режим работы:</b>\nЕжедневно с 09:00 до 20:00 без перерывов и выходных.",
        "location": "📍 <b>Как нас найти:</b>\nг. Алматы, пр. Абая 150/1 (рядом со станцией метро). У нас есть удобная парковка!",
        "payment": "💳 <b>Способы оплаты:</b>\nПринимаем Kaspi QR, наличные, карты Visa/Mastercard.",
        "promo": "🏷 <b>Использование промокодов:</b>\nПри оформлении записи нажмите «🏷 Ввести промокод» и укажите ваш секретный код!",
    }
    answer_text = answers.get(topic, "Информация обновляется.")
    await callback.message.answer(answer_text, parse_mode="HTML")
    await callback.answer()


@router.message(F.text == "⭐ Оставить отзыв")
async def start_general_review(message: Message) -> None:
    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, message.from_user.id)
        if not user:
            await message.answer("❌ Профиль не найден. Нажмите /start.")
            return
        bookings = await db.get_user_all_bookings(session, user.id)

    completed_without_review = [b for b in bookings if b.status == "completed" and not b.review]
    if not completed_without_review:
        await message.answer(
            "<b>⭐ Оставить отзыв</b>\n\n"
            "У вас нет завершенных записей без отзыва.\n"
            "После посещения специалиста здесь появится возможность оценить работу!",
            parse_mode="HTML",
        )
        return

    b = completed_without_review[0]
    await message.answer(
        f"<b>⭐ Оцените услугу «{b.service.title}» у мастера {b.master.full_name}:</b>",
        reply_markup=inline.rating_stars_keyboard(b.id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("rate_"))
async def process_rating_stars(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split("_")
    booking_id = int(parts[1])
    rating = int(parts[2])

    await state.update_data(review_booking_id=booking_id, review_rating=rating)
    await state.set_state(UserStates.enter_review_comment)

    await callback.message.edit_text(
        f"<b>Вы поставили {'⭐' * rating} ({rating}/5).</b>\n\n"
        "Напишите краткий комментарий к отзыву (или отправьте «-», чтобы пропустить):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(UserStates.enter_review_comment)
async def process_review_comment(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    comment = message.text.strip()
    if comment in ("-", "нет", "no"):
        comment = None

    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, message.from_user.id)
        if user:
            await db.create_review(
                session,
                booking_id=data["review_booking_id"],
                user_id=user.id,
                rating=data["review_rating"],
                comment=comment,
            )

    await state.clear()
    await message.answer("🎉 <b>Спасибо за ваш отзыв!</b>\nМы очень ценим ваше мнение.", parse_mode="HTML")


@router.message(F.text == "📞 Контакты")
async def contacts_cmd(message: Message) -> None:
    await message.answer(
        "<b>📞 Наши Контакты</b>\n\n"
        "🏢 <b>Адрес:</b> г. Алматы, пр. Абая 150/1\n"
        "📱 <b>Телефон:</b> +7 (700) 123-45-67\n"
        "💬 <b>Telegram:</b> @BookingBotSupport\n"
        "🌐 <b>Инстаграм:</b> @booking_bot_official\n\n"
        "Мы всегда рады ответить на любые ваши вопросы!",
        parse_mode="HTML",
    )
