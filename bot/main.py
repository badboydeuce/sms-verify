# bot/main.py

import asyncio
import logging

from aiogram.enums import ParseMode

from bot.loader import dp, bot

from bot.middlewares.user import UserMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

from bot.handlers.start import router as start_router
from bot.handlers.wallet import router as wallet_router
from bot.handlers.buy import router as buy_router
from bot.handlers.orders import router as orders_router
from bot.handlers.profile import router as profile_router
from bot.handlers.support import router as support_router
from bot.handlers.admin import router as admin_router

logger = logging.getLogger(__name__)


async def main():
    # Middlewares
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(ThrottlingMiddleware())

    # Routers
    dp.include_router(start_router)
    dp.include_router(wallet_router)
    dp.include_router(buy_router)
    dp.include_router(orders_router)
    dp.include_router(profile_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)

    # ✅ Drop pending updates and delete webhook before polling
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Starting bot polling...")

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Bot shutting down...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
