import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config.settings import settings
from app.database.db import init_db

from app.handlers.start import router as start_router
from app.handlers.booking import router as booking_router
from app.handlers.admin import router as admin_router
from app.middlewares.errors import ErrorHandlerMiddleware


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # Инициализация структуры базы данных
    await init_db()
    logging.info("База данных успешно инициализирована.")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    # Подключаем Middleware ошибок
    dp.update.outer_middleware(ErrorHandlerMiddleware())

    # Подключаем роутеры
    dp.include_router(start_router)
    dp.include_router(booking_router)
    dp.include_router(admin_router)

    logging.info("===================================")
    logging.info("🤖 Booking Bot v2.0 успешно запущен и готов к работе!")
    logging.info("===================================")

    # Пропускаем накопившиеся апдейты и запускаем поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен пользователем.")
