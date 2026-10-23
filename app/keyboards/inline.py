from __future__ import annotations

from typing import TypedDict

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class CategoryItem(TypedDict):
    id: int
    title: str


class ServiceKeyboardItem(TypedDict):
    id: int
    name: str
    price: int


class MasterKeyboardItem(TypedDict):
    id: int
    name: str
    role: str


class BookingKeyboardItem(TypedDict):
    id: int
    booking_date: str
    service_title: str
    status: str
    has_review: bool


class ServiceManageItem(TypedDict):
    id: int
    name: str
    price: int
    is_active: bool


class MasterManageItem(TypedDict):
    id: int
    name: str
    is_active: bool


def cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить", callback_data="cancel_booking")
    return builder.as_markup()


def admin_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить", callback_data="cancel_booking")
    return builder.as_markup()


def categories_keyboard(categories: list[CategoryItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(text=f"📂 {cat['title']}", callback_data=f"category_{cat['id']}")
    builder.button(text="📋 Все услуги", callback_data="category_all")
    builder.adjust(1)
    builder.button(text="❌ Отмена", callback_data="cancel_booking")
    return builder.as_markup()


def services_keyboard(services: list[ServiceKeyboardItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.button(
            text=f"🛠 {service['name']} — {service['price']} ₸",
            callback_data=f"service_{service['id']}",
        )
    builder.adjust(1)
    builder.button(text="⬅ Назад", callback_data="go_to_categories")
    builder.button(text="❌ Отмена", callback_data="cancel_booking")
    return builder.as_markup()


def masters_keyboard(masters: list[MasterKeyboardItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for master in masters:
        builder.button(
            text=f"👨‍💼 {master['name']} ({master['role']})",
            callback_data=f"master_{master['id']}",
        )
    builder.adjust(1)
    builder.button(text="⬅ Назад", callback_data="go_to_services")
    builder.button(text="❌ Отмена", callback_data="cancel_booking")
    return builder.as_markup()


def confirm_booking_keyboard(has_promo: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить запись", callback_data="confirm_booking")
    if not has_promo:
        builder.button(text="🏷 Ввести промокод", callback_data="enter_promo")
    builder.button(text="💬 Добавить комментарий", callback_data="add_comment")
    builder.button(text="❌ Отменить", callback_data="cancel_booking")
    builder.adjust(1)
    return builder.as_markup()


def my_bookings_keyboard(bookings: list[BookingKeyboardItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for booking in bookings:
        status_icon = "🟢" if booking["status"] in ("pending", "confirmed") else "🔴"
        builder.button(
            text=f"{status_icon} #{booking['id']} | {booking['service_title']} ({booking['booking_date']})",
            callback_data=f"view_booking_{booking['id']}",
        )
    builder.adjust(1)
    return builder.as_markup()


def booking_detail_keyboard(booking_id: int, status: str, has_review: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status in ("pending", "confirmed"):
        builder.button(text="🔄 Перенести время", callback_data=f"reschedule_{booking_id}")
        builder.button(text="❌ Отменить запись", callback_data=f"cancel_user_booking_{booking_id}")
    elif status == "completed" and not has_review:
        builder.button(text="⭐ Оставить отзыв", callback_data=f"review_booking_{booking_id}")

    builder.button(text="⬅ К спискам записей", callback_data="back_to_my_bookings")
    builder.adjust(1)
    return builder.as_markup()


def rating_stars_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for stars in range(5, 0, -1):
        builder.button(text=f"{'⭐' * stars} ({stars})", callback_data=f"rate_{booking_id}_{stars}")
    builder.adjust(1)
    builder.button(text="❌ Отмена", callback_data="cancel_booking")
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏ Изменить имя", callback_data="edit_profile_name")
    builder.button(text="📱 Изменить телефон", callback_data="edit_profile_phone")
    builder.button(text="📋 Мои записи", callback_data="view_my_bookings")
    builder.adjust(2, 1)
    return builder.as_markup()


def faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🕒 Режим работы", callback_data="faq_hours")
    builder.button(text="📍 Как нас найти", callback_data="faq_location")
    builder.button(text="💳 Способы оплаты", callback_data="faq_payment")
    builder.button(text="🏷 Как использовать промокод", callback_data="faq_promo")
    builder.adjust(2)
    return builder.as_markup()


def admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Активные записи", callback_data="admin_bookings")
    builder.button(text="📊 Аналитика & Отчеты", callback_data="admin_stats")
    builder.button(text="➕ Добавить услугу", callback_data="admin_add_service")
    builder.button(text="👨‍💼 Добавить мастера", callback_data="admin_add_master")
    builder.button(text="🏷 Создать промокод", callback_data="admin_add_promo")
    builder.button(text="📢 Рассылка клиентам", callback_data="admin_broadcast")
    builder.button(text="🛠 Управление услугами", callback_data="admin_manage_services")
    builder.button(text="👥 Управление мастерами", callback_data="admin_manage_masters")
    builder.button(text="📂 Экспорт записей (CSV)", callback_data="admin_export_csv")
    builder.adjust(2)
    return builder.as_markup()


def admin_booking_action_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=f"adm_status_{booking_id}_confirmed")
    builder.button(text="🎉 Завершить", callback_data=f"adm_status_{booking_id}_completed")
    builder.button(text="🚫 Отклонить", callback_data=f"adm_status_{booking_id}_cancelled")
    builder.adjust(2, 1)
    return builder.as_markup()


def admin_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅ В админ-панель", callback_data="admin_menu")
    return builder.as_markup()


def admin_services_manage_keyboard(services: list[ServiceManageItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in services:
        status = "🟢" if service["is_active"] else "🔴"
        action = "deactivate" if service["is_active"] else "activate"
        builder.button(
            text=f"{status} {service['name']} — {service['price']} ₸",
            callback_data=f"admin_service_{action}_{service['id']}",
        )
    builder.adjust(1)
    builder.button(text="⬅ В админ-панель", callback_data="admin_menu")
    return builder.as_markup()


def admin_masters_manage_keyboard(masters: list[MasterManageItem]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for master in masters:
        status = "🟢" if master["is_active"] else "🔴"
        action = "deactivate" if master["is_active"] else "activate"
        builder.button(
            text=f"{status} {master['name']}",
            callback_data=f"admin_master_{action}_{master['id']}",
        )
    builder.adjust(1)
    builder.button(text="⬅ В админ-панель", callback_data="admin_menu")
    return builder.as_markup()
