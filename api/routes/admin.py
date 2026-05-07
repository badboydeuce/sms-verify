from fastapi import APIRouter

router = APIRouter()


@router.get("/api/admin/stats")
async def admin_stats():

    return {
        "users": 0,
        "orders": 0,
        "revenue": 0
    }
