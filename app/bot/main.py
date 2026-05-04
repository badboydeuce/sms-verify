import asyncio
import os

from aiogram import Bot, Dispatcher

from app.bot.handlers.start import router as start_router
from app.bot.handlers.buy import router as buy_router
from app.bot.handlers.wallet import router as wallet_router
from app.bot.handlers.support import router as support_router

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # register routers INSIDE function (IMPORTANT)
    dp.include_router(start_router)
    dp.include_router(buy_router)
    dp.include_router(wallet_router)
    dp.include_router(support_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
