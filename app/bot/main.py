import asyncio
import os
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.database import init_db  # ✅ ADD THIS

from app.bot.handlers.start import router as start_router
from app.bot.handlers.buy import router as buy_router
from app.bot.handlers.wallet import router as wallet_router
from app.bot.handlers.support import router as support_router
from app.bot.handlers.profile import router as profile_router

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set")

    logging.basicConfig(level=logging.INFO)

    # ✅ INIT DATABASE FIRST
    init_db()

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    dp = Dispatcher(storage=MemoryStorage())

    # REGISTER ROUTERS
    dp.include_router(start_router)
    dp.include_router(buy_router)
    dp.include_router(wallet_router)
    dp.include_router(support_router)
    dp.include_router(profile_router)

    logging.info("🚀 Bot is running...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
