from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from sqlalchemy.exc import SQLAlchemyError

from app.utils.exceptions import AppError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except AppError as exc:
            logger.warning("Application error: %s", exc)
            await self._send_user_message(event, exc.user_message)
            return None
        except SQLAlchemyError as exc:
            logger.exception("Database error")
            await self._send_user_message(
                event,
                "❌ Ошибка базы данных. Попробуйте позже.",
            )
            return None
        except Exception:
            logger.exception("Unhandled error")
            await self._send_user_message(
                event,
                "❌ Произошла непредвиденная ошибка. Попробуйте позже.",
            )
            return None

    @staticmethod
    async def _send_user_message(event: TelegramObject, text: str) -> None:
        if isinstance(event, Message):
            await event.answer(text)
        elif isinstance(event, CallbackQuery):
            if event.message is not None:
                await event.message.answer(text)
            await event.answer("Ошибка", show_alert=True)
