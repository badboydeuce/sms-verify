from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database.init_db import (
    init_db
)

from api.routes.health import (
    router as health_router
)

from api.routes.wallet import (
    router as wallet_router
)

from api.routes.webhook import (
    router as webhook_router
)

from api.routes.orders import (
    router as orders_router
)

from api.routes.profile import (
    router as profile_router
)

from api.routes.admin import (
    router as admin_router
)

from api.routes.countries import (
    router as countries_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()

    yield


app = FastAPI(
    title="DeuceVerify API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():

    return {
        "name": "DeuceVerify API",
        "status": "running",
        "version": "1.0.0"
    }


app.include_router(health_router)
app.include_router(wallet_router)
app.include_router(webhook_router)
app.include_router(orders_router)
app.include_router(profile_router)
app.include_router(admin_router)

# NEW ROUTE
app.include_router(
    countries_router,
    prefix="/api",
    tags=["Countries"]
)