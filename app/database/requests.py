from __future__ import annotations

from datetime import date, datetime
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import Booking, Category, Master, PromoCode, Review, Service, User
from app.utils.exceptions import DatabaseError, NotFoundError, ValidationError
from app.utils.validators import validate_booking_datetime


class BookingStats(TypedDict):
    total: int
    pending: int
    confirmed: int
    completed: int
    cancelled: int
    total_revenue: int


async def get_or_create_user(
    session: AsyncSession,
    tg_id: int,
    full_name: str,
    username: str | None = None,
    phone: str | None = None,
) -> tuple[User, bool]:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()

    if user is not None:
        user.full_name = full_name
        if username:
            user.username = username
        if phone is not None:
            user.phone = phone
        await session.flush()
        return user, False

    user = User(tg_id=tg_id, full_name=full_name, username=username, phone=phone)
    session.add(user)
    await session.flush()
    return user, True


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> User | None:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalar_one_or_none()


async def get_all_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).order_by(User.id.desc()))
    return list(result.scalars().all())


async def update_user_phone(session: AsyncSession, tg_id: int, phone: str) -> User:
    user = await get_user_by_tg_id(session, tg_id)
    if user is None:
        raise NotFoundError(
            f"User not found: tg_id={tg_id}",
            user_message="❌ Пользователь не найден. Нажмите /start.",
        )
    user.phone = phone
    await session.flush()
    return user


async def update_user_name(session: AsyncSession, tg_id: int, full_name: str) -> User:
    user = await get_user_by_tg_id(session, tg_id)
    if user is None:
        raise NotFoundError(
            f"User not found: tg_id={tg_id}",
            user_message="❌ Пользователь не найден.",
        )
    user.full_name = full_name
    await session.flush()
    return user


# --- Categories ---

async def get_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(
        select(Category).where(Category.is_active.is_(True)).order_by(Category.id)
    )
    return list(result.scalars().all())


async def create_category(session: AsyncSession, title: str, description: str | None = None) -> Category:
    cat = Category(title=title, description=description)
    session.add(cat)
    await session.flush()
    return cat


# --- Services ---

async def get_active_services(session: AsyncSession, category_id: int | None = None) -> list[Service]:
    stmt = select(Service).where(Service.is_active.is_(True))
    if category_id is not None:
        stmt = stmt.where(Service.category_id == category_id)
    stmt = stmt.order_by(Service.id)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_all_services(session: AsyncSession) -> list[Service]:
    result = await session.execute(select(Service).order_by(Service.id))
    return list(result.scalars().all())


async def get_service_by_id(session: AsyncSession, service_id: int) -> Service | None:
    return await session.get(Service, service_id)


async def create_service(
    session: AsyncSession,
    title: str,
    price: int,
    duration_min: int = 60,
    description: str | None = None,
    category_id: int | None = None,
) -> Service:
    service = Service(
        title=title,
        price=price,
        duration_min=duration_min,
        description=description,
        category_id=category_id,
    )
    session.add(service)
    await session.flush()
    return service


async def set_service_active(session: AsyncSession, service_id: int, is_active: bool) -> Service:
    service = await session.get(Service, service_id)
    if service is None:
        raise NotFoundError(
            f"Service not found: id={service_id}",
            user_message="❌ Услуга не найдена.",
        )
    service.is_active = is_active
    await session.flush()
    return service


# --- Masters ---

async def get_active_masters(session: AsyncSession) -> list[Master]:
    result = await session.execute(
        select(Master).where(Master.is_active.is_(True)).order_by(Master.id)
    )
    return list(result.scalars().all())


async def get_all_masters(session: AsyncSession) -> list[Master]:
    result = await session.execute(select(Master).order_by(Master.id))
    return list(result.scalars().all())


async def get_master_by_id(session: AsyncSession, master_id: int) -> Master | None:
    return await session.get(Master, master_id)


async def create_master(
    session: AsyncSession,
    full_name: str,
    phone: str | None = None,
    specialization: str | None = None,
    bio: str | None = None,
) -> Master:
    master = Master(
        full_name=full_name,
        phone=phone,
        specialization=specialization,
        bio=bio,
    )
    session.add(master)
    await session.flush()
    return master


async def set_master_active(session: AsyncSession, master_id: int, is_active: bool) -> Master:
    master = await session.get(Master, master_id)
    if master is None:
        raise NotFoundError(
            f"Master not found: id={master_id}",
            user_message="❌ Мастер не найден.",
        )
    master.is_active = is_active
    await session.flush()
    return master


# --- Promo Codes ---

async def get_promo_code(session: AsyncSession, code: str) -> PromoCode | None:
    result = await session.execute(
        select(PromoCode).where(
            func.lower(PromoCode.code) == code.strip().lower(),
            PromoCode.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def create_promo_code(
    session: AsyncSession, code: str, discount_percent: int, max_uses: int = 100
) -> PromoCode:
    promo = PromoCode(
        code=code.strip().upper(),
        discount_percent=discount_percent,
        max_uses=max_uses,
    )
    session.add(promo)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise ValidationError(
            f"Promo code already exists: {code}",
            user_message="❌ Такой промокод уже существует.",
        ) from exc
    return promo


async def get_all_promo_codes(session: AsyncSession) -> list[PromoCode]:
    result = await session.execute(select(PromoCode).order_by(PromoCode.id.desc()))
    return list(result.scalars().all())


# --- Bookings & Slots ---

async def get_busy_slots(session: AsyncSession, master_id: int, date_str: str) -> list[str]:
    target_date = date.fromisoformat(date_str)
    result = await session.execute(
        select(Booking).where(
            Booking.master_id == master_id,
            Booking.status.in_(("pending", "confirmed")),
        )
    )
    busy_slots: list[str] = []
    for booking in result.scalars().all():
        if booking.booking_time.date() == target_date:
            busy_slots.append(booking.booking_time.strftime("%H:%M"))
    return busy_slots


async def is_slot_available(
    session: AsyncSession, master_id: int, booking_time: datetime, exclude_booking_id: int | None = None
) -> bool:
    stmt = select(func.count(Booking.id)).where(
        Booking.master_id == master_id,
        Booking.booking_time == booking_time,
        Booking.status.in_(("pending", "confirmed")),
    )
    if exclude_booking_id:
        stmt = stmt.where(Booking.id != exclude_booking_id)
    result = await session.execute(stmt)
    return result.scalar_one() == 0


async def create_booking(
    session: AsyncSession,
    user_id: int,
    service_id: int,
    master_id: int,
    booking_time: datetime,
    status: str = "pending",
    comment: str | None = None,
    promo_code_id: int | None = None,
) -> Booking:
    if not await is_slot_available(session, master_id, booking_time):
        raise ValidationError(
            f"Slot busy: master={master_id}, time={booking_time}",
            user_message="❌ Это время уже занято. Выберите другой слот.",
        )

    service = await session.get(Service, service_id)
    if not service:
        raise NotFoundError("Service not found", user_message="❌ Услуга не найдена.")

    original_price = service.price
    final_price = original_price

    if promo_code_id:
        promo = await session.get(PromoCode, promo_code_id)
        if promo and promo.is_active and promo.times_used < promo.max_uses:
            discount = (original_price * promo.discount_percent) // 100
            final_price = max(0, original_price - discount)
            promo.times_used += 1

    booking = Booking(
        user_id=user_id,
        service_id=service_id,
        master_id=master_id,
        promo_code_id=promo_code_id,
        booking_time=booking_time,
        original_price=original_price,
        final_price=final_price,
        status=status,
        comment=comment,
    )
    session.add(booking)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise DatabaseError(
            f"Failed to create booking: {exc}",
            user_message="❌ Не удалось создать запись. Проверьте данные и попробуйте снова.",
        ) from exc
    return booking


async def get_user_bookings(session: AsyncSession, user_id: int) -> list[Booking]:
    result = await session.execute(
        select(Booking)
        .options(
            selectinload(Booking.service),
            selectinload(Booking.master),
            selectinload(Booking.review),
        )
        .where(
            Booking.user_id == user_id,
            Booking.status.in_(("pending", "confirmed")),
        )
        .order_by(Booking.booking_time.asc())
    )
    return list(result.scalars().all())


async def get_user_all_bookings(session: AsyncSession, user_id: int) -> list[Booking]:
    result = await session.execute(
        select(Booking)
        .options(
            selectinload(Booking.service),
            selectinload(Booking.master),
            selectinload(Booking.review),
        )
        .where(Booking.user_id == user_id)
        .order_by(Booking.booking_time.desc())
    )
    return list(result.scalars().all())


async def get_active_bookings(session: AsyncSession) -> list[Booking]:
    result = await session.execute(
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.service),
            selectinload(Booking.master),
        )
        .where(Booking.status.in_(("pending", "confirmed")))
        .order_by(Booking.booking_time.asc())
    )
    return list(result.scalars().all())


async def get_all_bookings(session: AsyncSession) -> list[Booking]:
    result = await session.execute(
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.service),
            selectinload(Booking.master),
        )
        .order_by(Booking.booking_time.desc())
    )
    return list(result.scalars().all())


async def get_booking_by_id(session: AsyncSession, booking_id: int) -> Booking | None:
    result = await session.execute(
        select(Booking)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.service),
            selectinload(Booking.master),
            selectinload(Booking.review),
        )
        .where(Booking.id == booking_id)
    )
    return result.scalar_one_or_none()


async def update_booking_status(session: AsyncSession, booking_id: int, status: str) -> Booking:
    booking = await get_booking_by_id(session, booking_id)
    if booking is None:
        raise NotFoundError(
            f"Booking not found: id={booking_id}",
            user_message="❌ Запись не найдена.",
        )
    booking.status = status
    await session.flush()
    return booking


async def reschedule_booking(
    session: AsyncSession, booking_id: int, new_booking_time: datetime
) -> Booking:
    booking = await get_booking_by_id(session, booking_id)
    if booking is None:
        raise NotFoundError("Booking not found", user_message="❌ Запись не найдена.")

    if not await is_slot_available(session, booking.master_id, new_booking_time, exclude_booking_id=booking_id):
        raise ValidationError(
            "Slot unavailable",
            user_message="❌ Выбранный слот уже занят. Выберите другое время.",
        )

    booking.booking_time = new_booking_time
    booking.status = "pending"
    await session.flush()
    return booking


async def cancel_user_booking(session: AsyncSession, booking_id: int, user_id: int) -> Booking:
    booking = await get_booking_by_id(session, booking_id)
    if booking is None or booking.user_id != user_id:
        raise NotFoundError(
            f"Booking not found for user: booking={booking_id}, user={user_id}",
            user_message="❌ Запись не найдена или недоступна для отмены.",
        )
    if booking.status == "cancelled":
        raise ValidationError(
            f"Booking already cancelled: id={booking_id}",
            user_message="❌ Эта запись уже отменена.",
        )
    booking.status = "cancelled"
    await session.flush()
    return booking


# --- Reviews ---

async def create_review(
    session: AsyncSession, booking_id: int, user_id: int, rating: int, comment: str | None = None
) -> Review:
    booking = await get_booking_by_id(session, booking_id)
    if not booking or booking.user_id != user_id:
        raise NotFoundError("Booking not found", user_message="❌ Запись не найдена.")

    review = Review(
        booking_id=booking_id,
        user_id=user_id,
        master_id=booking.master_id,
        rating=rating,
        comment=comment,
    )
    session.add(review)
    try:
        await session.flush()
    except IntegrityError as exc:
        raise ValidationError(
            "Review already exists",
            user_message="❌ Вы уже оставили отзыв для этой записи.",
        ) from exc
    return review


async def get_master_reviews(session: AsyncSession, master_id: int) -> list[Review]:
    result = await session.execute(
        select(Review)
        .options(selectinload(Review.user))
        .where(Review.master_id == master_id)
        .order_by(Review.created_at.desc())
    )
    return list(result.scalars().all())


async def get_master_rating(session: AsyncSession, master_id: int) -> tuple[float, int]:
    result = await session.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.master_id == master_id)
    )
    avg_rating, count = result.one()
    return round(float(avg_rating or 0.0), 1), int(count or 0)


# --- Stats ---

async def get_booking_stats(session: AsyncSession) -> BookingStats:
    total = await session.scalar(select(func.count(Booking.id))) or 0
    pending = await session.scalar(select(func.count(Booking.id)).where(Booking.status == "pending")) or 0
    confirmed = await session.scalar(select(func.count(Booking.id)).where(Booking.status == "confirmed")) or 0
    completed = await session.scalar(select(func.count(Booking.id)).where(Booking.status == "completed")) or 0
    cancelled = await session.scalar(select(func.count(Booking.id)).where(Booking.status == "cancelled")) or 0

    revenue_stmt = select(func.sum(Booking.final_price)).where(Booking.status.in_(("confirmed", "completed")))
    total_revenue = await session.scalar(revenue_stmt) or 0

    return BookingStats(
        total=total,
        pending=pending,
        confirmed=confirmed,
        completed=completed,
        cancelled=cancelled,
        total_revenue=int(total_revenue),
    )


def parse_booking_datetime(date_str: str, time_str: str) -> datetime:
    return validate_booking_datetime(date_str, time_str)


# --- Seed Data ---

async def seed_initial_data(session: AsyncSession) -> None:
    categories_count = await session.scalar(select(func.count(Category.id))) or 0
    if categories_count == 0:
        cat_hair = Category(title="💇‍♂️ Стрижка и Укладка", description="Мужские и женские стрижки, модельные укладки")
        cat_care = Category(title="💆‍♀️ Спа и Уход", description="Расслабляющий уход за кожей и волосами")
        cat_consult = Category(title="💬 Консультации", description="Индивидуальный подбор стиля и ухода")
        session.add_all([cat_hair, cat_care, cat_consult])
        await session.flush()

    services_count = await session.scalar(select(func.count(Service.id))) or 0
    if services_count == 0:
        session.add_all(
            [
                Service(
                    title="Первичная консультация",
                    description="Подбор стиля и индивидуальные рекомендации",
                    price=1000,
                    duration_min=30,
                    category_id=1,
                ),
                Service(
                    title="Модельная стрижка",
                    description="Классическая или трендовая стрижка + мытье головы",
                    price=3500,
                    duration_min=45,
                    category_id=1,
                ),
                Service(
                    title="Премиум Спа-Уход",
                    description="Комплексный восстановливающий уход",
                    price=7500,
                    duration_min=75,
                    category_id=2,
                ),
            ]
        )

    masters_count = await session.scalar(select(func.count(Master.id))) or 0
    if masters_count == 0:
        session.add_all(
            [
                Master(
                    full_name="Алексей Смирнов",
                    phone="+77001234567",
                    specialization="Топ-стилист / Барбер",
                    bio="Опыт работы 7 лет. Эксперт по мужским стрижкам.",
                ),
                Master(
                    full_name="Елена Соколова",
                    phone="+77007654321",
                    specialization="Мастер Спа и Колорист",
                    bio="Опыт работы 5 лет. Авторские техники ухода.",
                ),
            ]
        )

    promo_count = await session.scalar(select(func.count(PromoCode.id))) or 0
    if promo_count == 0:
        session.add(
            PromoCode(
                code="START10",
                discount_percent=10,
                max_uses=500,
            )
        )

    await session.flush()
