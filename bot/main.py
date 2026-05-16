# bot/main.py

import asyncio
import logging
from asyncio import create_task

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


from workers.cleanup import cleanup_worker  # ✅ added

logger = logging.getLogger(__name__)


async def main():
    dp.update.middleware(UserMiddleware())
    dp.update.middleware(ThrottlingMiddleware())

    dp.include_router(start_router)
    dp.include_router(wallet_router)
    dp.include_router(buy_router)
    dp.include_router(orders_router)
    dp.include_router(profile_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)

    await bot.delete_webhook(drop_pending_updates=True)

    # ✅ Start cleanup worker
    create_task(cleanup_worker())

    logger.info("Starting bot polling...")

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("Bot shutting down...")
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
