from aiogram import Bot, Dispatcher
import asyncio
import os

from app.bot.handlers import start, buy

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(buy.router)


async def main():
    await dp.start_polling(bot)


def run_bot():
    asyncio.run(main())