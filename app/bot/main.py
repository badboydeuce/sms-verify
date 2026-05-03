# app/bot/main.py

import asyncio
import os
from aiogram import Bot, Dispatcher

from app.bot.handlers.start import router as start_router
from app.bot.handlers.buy import router as buy_router

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Register routers
dp.include_router(start_router)
dp.include_router(buy_router)


async def main():
    print("🤖 DeuceVerify Bot is running...")
    await dp.start_polling(bot)


def run_bot():
    asyncio.run(main())
