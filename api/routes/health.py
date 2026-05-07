from flask import Blueprint
from datetime import datetime

health_router = Blueprint(
    "health",
    __name__
)


@health_router.get("/api/health")
def health():

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }