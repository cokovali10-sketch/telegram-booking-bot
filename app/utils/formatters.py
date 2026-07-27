from __future__ import annotations

from app.database.models import Booking, Master, Service, User
from app.keyboards.inline import (
    BookingKeyboardItem,
    MasterKeyboardItem,
    MasterManageItem,
    ServiceKeyboardItem,
    ServiceManageItem,
)


def service_to_keyboard_item(service: Service) -> ServiceKeyboardItem:
    return ServiceKeyboardItem(id=service.id, name=service.title, price=service.price)


def master_to_keyboard_item(master: Master) -> MasterKeyboardItem:
    return MasterKeyboardItem(
        id=master.id,
        name=master.full_name,
        role=master.specialization or master.phone or "Специалист",
    )


def service_to_manage_item(service: Service) -> ServiceManageItem:
    return ServiceManageItem(
        id=service.id,
        name=service.title,
        price=service.price,
        is_active=service.is_active,
    )


def master_to_manage_item(master: Master) -> MasterManageItem:
    return MasterManageItem(
        id=master.id,
        name=master.full_name,
        is_active=master.is_active,
    )


def booking_to_keyboard_item(booking: Booking) -> BookingKeyboardItem:
    service_title = booking.service.title if booking.service else "Услуга"
    return BookingKeyboardItem(
        id=booking.id,
        booking_date=booking.booking_time.strftime("%d.%m %H:%M"),
        service_title=service_title,
        status=booking.status,
        has_review=booking.review is not None,
    )


def format_booking_card(booking: Booking) -> str:
    service_title = booking.service.title if booking.service else "—"
    service_price = f"{booking.final_price} ₸" if booking.final_price else f"{booking.service.price} ₸" if booking.service else "—"
    master_name = booking.master.full_name if booking.master else "—"
    user_name = booking.user.full_name if booking.user else "—"
    user_phone = booking.user.phone if booking.user and booking.user.phone else "—"

    status_map = {
        "pending": "⏳ В ожидании",
        "confirmed": "✅ Подтверждена",
        "completed": "🎉 Завершена",
        "cancelled": "❌ Отменена",
    }
    status_str = status_map.get(booking.status, booking.status)

    promo_str = f"🏷 Скидка применилась (Итого: {booking.final_price} ₸)\n" if booking.promo_code_id else ""
    comment_str = f"💬 Комментарий: {booking.comment}\n" if booking.comment else ""

    return (
        f"<b>📋 Запись #{booking.id}</b>\n"
        f"<b>Статус:</b> {status_str}\n"
        f"<b>📅 Дата и время:</b> {booking.booking_time.strftime('%d.%m.%Y в %H:%M')}\n"
        f"<b>🛠 Услуга:</b> {service_title}\n"
        f"<b>💰 Стоимость:</b> {service_price}\n"
        f"<b>👨‍💼 Мастер:</b> {master_name}\n"
        f"<b>👤 Клиент:</b> {user_name} ({user_phone})\n"
        f"{promo_str}"
        f"{comment_str}"
    )


def format_user_profile(user: User, total_bookings: int) -> str:
    phone_str = user.phone if user.phone else "не указан (укажите при записи)"
    username_str = f"@{user.username}" if user.username else "не указан"
    return (
        f"<b>👤 Ваш Профиль</b>\n\n"
        f"<b>Имя:</b> {user.full_name}\n"
        f"<b>Телефон:</b> {phone_str}\n"
        f"<b>Telegram Username:</b> {username_str}\n"
        f"<b>Всего записей:</b> {total_bookings}\n"
        f"<b>Дата регистрации:</b> {user.created_at.strftime('%d.%m.%Y')}\n"
    )
