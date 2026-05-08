import time

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ThrottlingMiddleware(
    BaseMiddleware
):

    cache = {}

    RATE_LIMIT = 0

    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data
    ):

        user = data.get(
            "event_from_user"
        )

        if not user:
            return await handler(
                event,
                data
            )

        now = time.time()

        last_request = self.cache.get(
            user.id,
            0
        )

        if now - last_request < self.RATE_LIMIT:

            return

        self.cache[user.id] = now

        return await handler(
            event,
            data
        )
