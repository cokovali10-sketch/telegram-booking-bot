from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import async_session
from app.utils.exceptions import DatabaseError


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as exc:
            await session.rollback()
            raise DatabaseError(
                f"Database operation failed: {exc}",
                user_message="❌ Ошибка базы данных. Попробуйте позже.",
            ) from exc
        except Exception:
            await session.rollback()
            raise
