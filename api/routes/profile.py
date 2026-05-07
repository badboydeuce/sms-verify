from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from api.dependencies.db import (
    get_db
)

from core.services.user_service import (
    UserService
)

router = APIRouter()


@router.get("/api/profile/{telegram_id}")
async def profile(
    telegram_id: int,
    db: AsyncSession = Depends(get_db)
):

    user = (
        await UserService.get_user_by_telegram_id(
            db,
            telegram_id
        )
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "telegram_id":
        user.telegram_id,

        "username":
        user.username,

        "balance":
        float(user.balance)
    }
