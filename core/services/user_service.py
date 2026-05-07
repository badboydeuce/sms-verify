from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.user import User


class UserService:

    @staticmethod
    async def get_user_by_telegram_id(
        db: AsyncSession,
        telegram_id: int
    ):

        result = await db.execute(
            select(User).where(
                User.telegram_id == telegram_id
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        db: AsyncSession,
        telegram_id: int,
        username: str | None = None
    ):

        user = User(
            telegram_id=telegram_id,
            username=username
        )

        db.add(user)

        await db.commit()

        await db.refresh(user)

        return user

    @staticmethod
    async def get_or_create_user(
        db: AsyncSession,
        telegram_id: int,
        username: str | None = None
    ):

        user = await UserService.get_user_by_telegram_id(
            db,
            telegram_id
        )

        if user:
            return user

        return await UserService.create_user(
            db,
            telegram_id,
            username
        )