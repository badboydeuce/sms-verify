from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class UserMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data
    ):

        user = data.get("event_from_user")

        if user:
            # create user if not exists
            pass

        return await handler(event, data)