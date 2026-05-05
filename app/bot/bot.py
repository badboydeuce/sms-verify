import asyncio
import os

from aiogram import Bot, Dispatcher

from app.bot.handlers import start, buy

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # =========================
    # REGISTER ROUTERS
    # =========================
    dp.include_router(start.router)
    dp.include_router(buy.router)

    print("🚀 Bot is running...")

    await dp.start_polling(bot)


def run_bot():
    asyncio.run(main())


if __name__ == "__main__":
    run_bot()
