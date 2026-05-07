import asyncio

from bot.loader import dp, bot

from bot.handlers.start import router as start_router
from bot.handlers.wallet import router as wallet_router
from bot.handlers.buy import router as buy_router
from bot.handlers.orders import router as orders_router
from bot.handlers.profile import router as profile_router
from bot.handlers.support import router as support_router
from bot.handlers.admin import router as admin_router

from bot.middlewares.user import UserMiddleware


async def main():

    dp.update.middleware(UserMiddleware())

    dp.include_router(start_router)
    dp.include_router(wallet_router)
    dp.include_router(buy_router)
    dp.include_router(orders_router)
    dp.include_router(profile_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())