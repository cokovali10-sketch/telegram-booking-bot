from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from app.config.settings import settings
from app.database import requests as db
from app.database.session import get_session
from app.database.models import Master, Service
from app.keyboards import inline
from app.services import calendar_service
# --- константы вынесены FORGE refactor ---
CONST_3 = 3


logger = logging.getLogger(__name__)

router = Router()


class BookingStates(StatesGroup):
    select_category = State()
    select_service = State()
    select_employee = State()
    select_date = State()
    select_time = State()
    enter_promo = State()
    input_phone = State()
    input_comment = State()
    confirm = State()
    reschedule_date = State()
    reschedule_time = State()


def _service_to_dict(service: Service) -> dict[str, int | str]:
    return {"id": service.id, "name": service.title, "price": service.price}


def _master_to_dict(master: Master) -> dict[str, int | str]:
    spec = master.specialization or master.phone or "—"
    return {"id": master.id, "name": master.full_name, "role": spec}


@router.message(F.text.in_({"📅 Записаться", "/book"}))
async def start_booking(message: Message, state: FSMContext) -> None:
    await state.clear()
    async with get_session() as session:
        categories = await db.get_categories(session)

    if categories:
        cat_items = [{"id": c.id, "title": c.title} for c in categories]
        await state.set_state(BookingStates.select_category)
        await message.answer(
            "<b>📂 Шаг 1 из 5: Выберите категорию услуг:</b>",
            reply_markup=inline.categories_keyboard(cat_items),
            parse_mode="HTML",
        )
    else:
        # If no categories, show services directly
        async with get_session() as session:
            services = await db.get_active_services(session)
        if not services:
            await message.answer("😔 К сожалению, список услуг сейчас пуст.")
            return
        await state.set_state(BookingStates.select_service)
        await message.answer(
            "<b>📋 Шаг 1 из 5: Выберите услугу:</b>",
            reply_markup=inline.services_keyboard([_service_to_dict(s) for s in services]),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "cancel_booking")
async def cancel_booking_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer("Запись отменена.")
    await callback.message.edit_text("❌ Вы отменили процесс записи.")


@router.callback_query(BookingStates.select_category, F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery, state: FSMContext) -> None:
    cat_param = callback.data.split("_")[1]
    async with get_session() as session:
        if cat_param == "all":
            services = await db.get_active_services(session)
        else:
            category_id = int(cat_param)
            services = await db.get_active_services(session, category_id=category_id)

    if not services:
        await callback.answer("В этой категории пока нет услуг", show_alert=True)
        return

    await state.set_state(BookingStates.select_service)
    await callback.message.edit_text(
        "<b>📋 Шаг 2 из 5: Выберите услугу:</b>",
        reply_markup=inline.services_keyboard([_service_to_dict(s) for s in services]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "go_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext) -> None:
    async with get_session() as session:
        categories = await db.get_categories(session)

    if categories:
        cat_items = [{"id": c.id, "title": c.title} for c in categories]
        await state.set_state(BookingStates.select_category)
        await callback.message.edit_text(
            "<b>📂 Выберите категорию услуг:</b>",
            reply_markup=inline.categories_keyboard(cat_items),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(BookingStates.select_service, F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext) -> None:
    service_id = int(callback.data.split("_")[1])
    await state.update_data(service_id=service_id)

    async with get_session() as session:
        masters = await db.get_active_masters(session)

    if not masters:
        await callback.answer("Нет доступных специалистов", show_alert=True)
        return

    await state.set_state(BookingStates.select_employee)
    await callback.message.edit_text(
        "<b>👨‍💼 Шаг 3 из 5: Выберите специалиста:</b>",
        reply_markup=inline.masters_keyboard([_master_to_dict(m) for m in masters]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "go_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext) -> None:
    async with get_session() as session:
        services = await db.get_active_services(session)

    await state.set_state(BookingStates.select_service)
    await callback.message.edit_text(
        "<b>📋 Выберите услугу:</b>",
        reply_markup=inline.services_keyboard([_service_to_dict(s) for s in services]),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(BookingStates.select_employee, F.data.startswith("master_"))
async def master_selected(callback: CallbackQuery, state: FSMContext) -> None:
    master_id = int(callback.data.split("_")[1])
    await state.update_data(master_id=master_id)

    await state.set_state(BookingStates.select_date)
    await callback.message.edit_text(
        "<b>📅 Шаг 4 из 5: Выберите дату визита:</b>",
        reply_markup=calendar_service.generate_calendar_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cal_nav_"))
async def calendar_navigation(callback: CallbackQuery) -> None:
    parts = callback.data.split("_")
    year, month = int(parts[2]), int(parts[CONST_3])

    await callback.message.edit_reply_markup(
        reply_markup=calendar_service.generate_calendar_keyboard(year, month)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cal_date_"))
async def date_selected(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    parts = callback.data.split("_")
    year, month, day = int(parts[2]), int(parts[CONST_3]), int(parts[4])
    formatted_date = f"{year:04d}-{month:02d}-{day:02d}"

    await state.update_data(booking_date=formatted_date)
    data = await state.get_data()

    async with get_session() as session:
        busy_slots = await db.get_busy_slots(session, data["master_id"], formatted_date)

    await state.set_state(BookingStates.select_time)
    await callback.message.edit_text(
        f"<b>📅 Выбрана дата: {day:02d}.{month:02d}.{year}</b>\n\n"
        f"<b>⏰ Шаг 5 из 5: Выберите доступное время:</b>",
        reply_markup=calendar_service.generate_time_slots_keyboard(busy_slots),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "go_to_calendar")
async def back_to_calendar(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookingStates.select_date)
    await callback.message.edit_text(
        "<b>📅 Выберите дату визита:</b>",
        reply_markup=calendar_service.generate_calendar_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(BookingStates.select_time, F.data.startswith("time_"))
async def time_selected(callback: CallbackQuery, state: FSMContext) -> None:
    time_slot = callback.data.split("_")[1]
    await state.update_data(booking_time=time_slot)

    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, callback.from_user.id)

    if user is None or not user.phone:
        await state.set_state(BookingStates.input_phone)

        phone_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Поделиться контактом", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )

        await callback.message.delete()
        await callback.message.answer(
            "<b>📱 Укажите ваш контактный номер телефона:</b>\n"
            "Нажмите на кнопку ниже, чтобы отправить номер в один клик.",
            reply_markup=phone_keyboard,
            parse_mode="HTML",
        )
    else:
        await show_confirmation(callback.message, state)

    await callback.answer()


@router.message(BookingStates.input_phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = message.contact.phone_number if message.contact else message.text.strip()

    async with get_session() as session:
        await db.update_user_phone(session, message.from_user.id, phone)

    await message.answer("✅ Номер телефона сохранен!", reply_markup=ReplyKeyboardRemove())
    await show_confirmation(message, state)


@router.callback_query(BookingStates.confirm, F.data == "enter_promo")
async def start_enter_promo(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookingStates.enter_promo)
    await callback.message.edit_text("<b>🏷 Введите ваш промокод:</b>", parse_mode="HTML")
    await callback.answer()


@router.message(BookingStates.enter_promo)
async def process_promo_code(message: Message, state: FSMContext) -> None:
    code = message.text.strip()
    async with get_session() as session:
        promo = await db.get_promo_code(session, code)

    if not promo:
        await message.answer("❌ Промокод не существует или неактивен. Попробуйте еще раз:")
        return

    await state.update_data(promo_code_id=promo.id, discount_percent=promo.discount_percent)
    await message.answer(f"🎉 Промокод <b>{promo.code}</b> применен! Скидка {promo.discount_percent}%.", parse_mode="HTML")
    await show_confirmation(message, state)


@router.callback_query(BookingStates.confirm, F.data == "add_comment")
async def start_add_comment(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BookingStates.input_comment)
    await callback.message.edit_text("<b>💬 Введите комментарий или пожелание к записи:</b>", parse_mode="HTML")
    await callback.answer()


@router.message(BookingStates.input_comment)
async def process_comment(message: Message, state: FSMContext) -> None:
    await state.update_data(comment=message.text.strip())
    await message.answer("✅ Комментарий сохранен!", parse_mode="HTML")
    await show_confirmation(message, state)


async def show_confirmation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    async with get_session() as session:
        service = await db.get_service_by_id(session, data["service_id"])
        master = await db.get_master_by_id(session, data["master_id"])

    if service is None or master is None:
        await message.answer("❌ Не удалось загрузить данные записи. Начните заново.")
        await state.clear()
        return

    original_price = service.price
    discount_percent = data.get("discount_percent", 0)
    final_price = original_price - (original_price * discount_percent // 100) if discount_percent else original_price

    price_text = f"{final_price} ₸"
    if discount_percent:
        price_text += f" (скидка {discount_percent}%, старая цена: <s>{original_price} ₸</s>)"

    comment = data.get("comment", "Отсутствует")

    text = (
        "<b>🎉 Проверьте данные вашей записи:</b>\n\n"
        f"🛠 <b>Услуга:</b> {service.title}\n"
        f"💰 <b>Стоимость:</b> {price_text}\n"
        f"👨‍💼 <b>Мастер:</b> {master.full_name}\n"
        f"📅 <b>Дата:</b> {data['booking_date']}\n"
        f"⏰ <b>Время:</b> {data['booking_time']}\n"
        f"💬 <b>Комментарий:</b> {comment}\n\n"
        "Все верно?"
    )

    await state.set_state(BookingStates.confirm)
    has_promo = "promo_code_id" in data
    await message.answer(text, reply_markup=inline.confirm_booking_keyboard(has_promo=has_promo), parse_mode="HTML")


@router.callback_query(BookingStates.confirm, F.data == "confirm_booking")
async def save_booking(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, callback.from_user.id)
        if user is None:
            await callback.answer("Пользователь не найден. Нажмите /start.", show_alert=True)
            return

        booking_time = db.parse_booking_datetime(data["booking_date"], data["booking_time"])
        booking = await db.create_booking(
            session,
            user_id=user.id,
            service_id=data["service_id"],
            master_id=data["master_id"],
            booking_time=booking_time,
            comment=data.get("comment"),
            promo_code_id=data.get("promo_code_id"),
        )
        booking_id = booking.id

    await state.clear()
    await callback.message.edit_text(
        f"✅ <b>Вы успешно записаны! (Номер брони: #{booking_id})</b>\n\n"
        "Мы ждем вас в указанное время. Посмотреть свои записи можно в меню «📋 Мои записи».",
        parse_mode="HTML",
    )
    await callback.answer()

    # Notify Admins
    for admin_id in settings.ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🚨 <b>Новая запись #{booking_id}!</b>\n\n"
                f"👤 Клиент: {callback.from_user.full_name}\n"
                f"📅 Дата: {data['booking_date']} в {data['booking_time']}\n"
                f"🛠 Услуга: {service.title if 'service' in locals() else ''}",
                parse_mode="HTML",
                reply_markup=inline.admin_booking_action_keyboard(booking_id),
            )
        except Exception:
            pass


# --- Cancel & Reschedule ---

@router.callback_query(F.data.startswith("cancel_user_booking_"))
async def cancel_user_booking_callback(callback: CallbackQuery) -> None:
    booking_id = int(callback.data.split("_")[CONST_3])
    async with get_session() as session:
        user = await db.get_user_by_tg_id(session, callback.from_user.id)
        if user:
            await db.cancel_user_booking(session, booking_id, user.id)

    await callback.message.edit_text(f"❌ Запись #{booking_id} успешно отменена.")
    await callback.answer("Запись отменена.")


@router.callback_query(F.data.startswith("reschedule_"))
async def reschedule_start(callback: CallbackQuery, state: FSMContext) -> None:
    booking_id = int(callback.data.split("_")[1])
    await state.update_data(reschedule_booking_id=booking_id)
    await state.set_state(BookingStates.reschedule_date)

    await callback.message.edit_text(
        f"<b>🔄 Перенос записи #{booking_id}</b>\n\nВыберите новую дату:",
        reply_markup=calendar_service.generate_calendar_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
