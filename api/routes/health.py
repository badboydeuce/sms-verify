from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/api/health")
async def health():

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
