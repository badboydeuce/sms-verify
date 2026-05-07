from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from core.database.session import (
    AsyncSessionLocal
)

from core.services.user_service import (
    UserService
)


class UserMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data
    ):

        telegram_user = data.get(
            "event_from_user"
        )

        if telegram_user:

            async with AsyncSessionLocal() as db:

                user = (
                    await UserService.get_or_create_user(
                        db=db,
                        telegram_id=telegram_user.id,
                        username=telegram_user.username
                    )
                )

                data["db_user"] = user

        return await handler(
            event,
            data
        )
