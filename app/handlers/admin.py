from __future__ import annotations

import csv
import io
import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from app.config.settings import settings
from app.database import requests as db
from app.database.session import get_session
from app.keyboards import inline
from app.utils.formatters import master_to_manage_item, service_to_manage_item
# --- константы вынесены FORGE refactor ---
CONST_3 = 3


logger = logging.getLogger(__name__)

router = Router()


class AdminStates(StatesGroup):
    add_service_name = State()
    add_service_price = State()
    add_service_duration = State()
    add_master_name = State()
    add_master_spec = State()
    add_master_phone = State()
    add_promo_code = State()
    add_promo_discount = State()
    broadcast_text = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(F.text.in_({"👑 Админ-панель", "👑 Админ", "/admin"}))
@router.callback_query(F.data == "admin_menu")
async def admin_menu(event: Message | CallbackQuery) -> None:
    user_id = event.from_user.id
    if not is_admin(user_id):
        msg = "⛔ Доступ запрещён."
        if isinstance(event, Message):
            await event.answer(msg)
        else:
            await event.answer(msg, show_alert=True)
        return

    text = (
        "<b>👑 Панель Администратора</b>\n\n"
        "Управление записями, статистикой, каталогом услуг, мастерами и рассылками.\n"
        "Выберите нужное действие ниже:"
    )

    if isinstance(event, Message):
        await event.answer(text, reply_markup=inline.admin_keyboard(), parse_mode="HTML")
    else:
        await event.message.edit_text(text, reply_markup=inline.admin_keyboard(), parse_mode="HTML")
        await event.answer()


@router.callback_query(F.data == "admin_bookings")
async def view_admin_bookings(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    async with get_session() as session:
        bookings = await db.get_active_bookings(session)

    if not bookings:
        await callback.message.edit_text(
            "<b>📋 Нет активных записей.</b>",
            reply_markup=inline.admin_back_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return

    await callback.message.answer("<b>📋 Активные записи:</b>", parse_mode="HTML")
    for b in bookings[:10]:  # Show top 10
        status_text = {
            "pending": "⏳ Ожидает",
            "confirmed": "✅ Подтверждена",
            "completed": "🎉 Завершена",
            "cancelled": "❌ Отменена",
        }.get(b.status, b.status)

        text = (
            f"<b>Запись #{b.id}</b> [{status_text}]\n"
            f"👤 <b>Клиент:</b> {b.user.full_name} ({b.user.phone or 'нет ном.'})\n"
            f"🛠 <b>Услуга:</b> {b.service.title} ({b.final_price} ₸)\n"
            f"👨‍💼 <b>Мастер:</b> {b.master.full_name}\n"
            f"📅 <b>Дата:</b> {b.booking_time.strftime('%d.%m.%Y в %H:%M')}"
        )
        await callback.message.answer(
            text,
            reply_markup=inline.admin_booking_action_keyboard(b.id),
            parse_mode="HTML",
        )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def view_admin_stats(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    async with get_session() as session:
        stats = await db.get_booking_stats(session)
        users = await db.get_all_users(session)

    text = (
        "<b>📊 Аналитика & Статистика</b>\n\n"
        f"👥 <b>Всего клиентов:</b> {len(users)}\n"
        f"📋 <b>Всего броней:</b> {stats['total']}\n"
        f"⏳ <b>В ожидании:</b> {stats['pending']}\n"
        f"✅ <b>Подтверждено:</b> {stats['confirmed']}\n"
        f"🎉 <b>Завершено:</b> {stats['completed']}\n"
        f"❌ <b>Отменено:</b> {stats['cancelled']}\n\n"
        f"💰 <b>Ориентировочная выручка:</b> {stats['total_revenue']:,} ₸"
    )
    await callback.message.edit_text(text, reply_markup=inline.admin_back_keyboard(), parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "admin_export_csv")
async def export_bookings_csv(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    async with get_session() as session:
        bookings = await db.get_all_bookings(session)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "User", "Phone", "Service", "Price", "Master", "Status"])

    for b in bookings:
        writer.writerow(
            [
                b.id,
                b.booking_time.strftime("%Y-%m-%d %H:%M"),
                b.user.full_name,
                b.user.phone or "",
                b.service.title,
                b.final_price,
                b.master.full_name,
                b.status,
            ]
        )

    output.seek(0)
    file_bytes = output.getvalue().encode("utf-8-sig")
    document = BufferedInputFile(file_bytes, filename="bookings_report.csv")

    await callback.message.answer_document(
        document, caption="📊 Полный экспорт бронирований в формате CSV."
    )
    await callback.answer()


# --- Add Service ---

@router.callback_query(F.data == "admin_add_service")
async def start_add_service(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.add_service_name)
    await callback.message.edit_text(
        "<b>🛠 Добавление услуги (Шаг 1 из 2)</b>\n\nВведите название новой услуги:",
        reply_markup=inline.cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.add_service_name)
async def process_service_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminStates.add_service_price)
    await message.answer(
        "<b>💰 Шаг 2 из 2:</b> Введите стоимость услуги (числом в ₸):",
        parse_mode="HTML",
    )


@router.message(AdminStates.add_service_price)
async def process_service_price(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit():
        await message.answer("❌ Введите корректное число!")
        return

    data = await state.get_data()
    price = int(message.text)

    async with get_session() as session:
        await db.create_service(session, title=data["name"], price=price)

    await state.clear()
    await message.answer(
        f"✅ Услуга <b>«{data['name']}»</b> ({price} ₸) успешно добавлена!",
        reply_markup=inline.admin_keyboard(),
        parse_mode="HTML",
    )


# --- Add Master ---

@router.callback_query(F.data == "admin_add_master")
async def start_add_master(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.add_master_name)
    await callback.message.edit_text(
        "<b>👨‍💼 Добавление мастера (Шаг 1 из 2)</b>\n\nВведите ФИО мастера:",
        reply_markup=inline.cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.add_master_name)
async def process_master_name(message: Message, state: FSMContext) -> None:
    await state.update_data(master_name=message.text.strip())
    await state.set_state(AdminStates.add_master_spec)
    await message.answer(
        "<b>💼 Шаг 2 из 2:</b> Введите специализацию мастера (например: Топ-Стилист):",
        parse_mode="HTML",
    )


@router.message(AdminStates.add_master_spec)
async def process_master_spec(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    spec = message.text.strip()

    async with get_session() as session:
        await db.create_master(session, full_name=data["master_name"], specialization=spec)

    await state.clear()
    await message.answer(
        f"✅ Мастер <b>{data['master_name']}</b> ({spec}) успешно добавлен!",
        reply_markup=inline.admin_keyboard(),
        parse_mode="HTML",
    )


# --- Add Promo Code ---

@router.callback_query(F.data == "admin_add_promo")
async def start_add_promo(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.add_promo_code)
    await callback.message.edit_text(
        "<b>🏷 Создание промокода (Шаг 1 из 2)</b>\n\nВведите название промокода (например: SUMMER2026):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.add_promo_code)
async def process_promo_code_name(message: Message, state: FSMContext) -> None:
    await state.update_data(promo_code=message.text.strip().upper())
    await state.set_state(AdminStates.add_promo_discount)
    await message.answer("<b>💰 Шаг 2 из 2:</b> Введите процент скидки (1-99):", parse_mode="HTML")


@router.message(AdminStates.add_promo_discount)
async def process_promo_discount(message: Message, state: FSMContext) -> None:
    if not message.text.isdigit() or not (1 <= int(message.text) <= 99):
        await message.answer("❌ Введите число от 1 до 99!")
        return

    data = await state.get_data()
    discount = int(message.text)

    async with get_session() as session:
        await db.create_promo_code(session, code=data["promo_code"], discount_percent=discount)

    await state.clear()
    await message.answer(
        f"✅ Промокод <b>{data['promo_code']}</b> с проблемой {discount}% создана!",
        reply_markup=inline.admin_keyboard(),
        parse_mode="HTML",
    )


# --- Broadcast ---

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(AdminStates.broadcast_text)
    await callback.message.edit_text(
        "<b>📢 Массовая рассылка клиентам</b>\n\n"
        "Отправьте текст сообщения для рассылки всем зарегистрированным пользователям:",
        reply_markup=inline.cancel_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(AdminStates.broadcast_text)
async def process_broadcast(message: Message, state: FSMContext) -> None:
    text = message.text
    async with get_session() as session:
        users = await db.get_all_users(session)

    sent = 0
    failed = 0
    for u in users:
        try:
            await message.bot.send_message(u.tg_id, f"📢 <b>Сообщение от администрации:</b>\n\n{text}", parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1

    await state.clear()
    await message.answer(
        f"🎉 <b>Рассылка завершена!</b>\n\n"
        f"✅ Успешно доставлено: {sent}\n"
        f"❌ Ошибок: {failed}",
        reply_markup=inline.admin_keyboard(),
        parse_mode="HTML",
    )


# --- Service / Master Management ---

@router.callback_query(F.data == "admin_manage_services")
async def manage_services_list(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    async with get_session() as session:
        services = await db.get_all_services(session)

    items = [service_to_manage_item(s) for s in services]
    await callback.message.edit_text(
        "<b>🛠 Управление услугами:</b>\nНажмите на услугу, чтобы включить/выключить ее.",
        reply_markup=inline.admin_services_manage_keyboard(items),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_service_"))
async def toggle_service_status(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    parts = callback.data.split("_")
    action, service_id = parts[2], int(parts[CONST_3])
    is_active = action == "activate"

    async with get_session() as session:
        await db.set_service_active(session, service_id, is_active)
        services = await db.get_all_services(session)

    items = [service_to_manage_item(s) for s in services]
    await callback.message.edit_reply_markup(
        reply_markup=inline.admin_services_manage_keyboard(items)
    )
    await callback.answer("Статус услуги изменен.")


@router.callback_query(F.data == "admin_manage_masters")
async def manage_masters_list(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    async with get_session() as session:
        masters = await db.get_all_masters(session)

    items = [master_to_manage_item(m) for m in masters]
    await callback.message.edit_text(
        "<b>👥 Управление мастерами:</b>\nНажмите на мастера, чтобы включить/выключить его.",
        reply_markup=inline.admin_masters_manage_keyboard(items),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_master_"))
async def toggle_master_status(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    parts = callback.data.split("_")
    action, master_id = parts[2], int(parts[CONST_3])
    is_active = action == "activate"

    async with get_session() as session:
        await db.set_master_active(session, master_id, is_active)
        masters = await db.get_all_masters(session)

    items = [master_to_manage_item(m) for m in masters]
    await callback.message.edit_reply_markup(
        reply_markup=inline.admin_masters_manage_keyboard(items)
    )
    await callback.answer("Статус мастера изменен.")


@router.callback_query(F.data.startswith("adm_status_"))
async def change_booking_status(callback: CallbackQuery) -> None:
    if not is_admin(callback.from_user.id):
        return

    parts = callback.data.split("_")
    booking_id = int(parts[2])
    status = parts[CONST_3]

    async with get_session() as session:
        booking = await db.update_booking_status(session, booking_id, status)
        if booking is None:
            await callback.answer("Запись не найдена.", show_alert=True)
            return

    status_labels = {
        "confirmed": "подтверждена ✅",
        "completed": "завершена 🎉",
        "cancelled": "отклонена ❌",
    }
    status_text = status_labels.get(status, status)

    await callback.message.edit_text(
        f"{callback.message.text}\n\n<b>📌 Статус обновлен: Запись {status_text}</b>",
        parse_mode="HTML",
    )
    await callback.answer("Статус обновлен.")

    # Notify User
    try:
        user_msg = {
            "confirmed": f"✅ Ваша запись #{booking_id} была подтверждена администратором!",
            "completed": f"🎉 Ваша запись #{booking_id} была успешно завершена! Будем рады вашему отзыву в меню «⭐ Оставить отзыв».",
            "cancelled": f"❌ К сожалению, ваша запись #{booking_id} была отменена администратором.",
        }.get(status)

        if user_msg and booking.user:
            await callback.bot.send_message(booking.user.tg_id, user_msg)
    except Exception:
        pass
