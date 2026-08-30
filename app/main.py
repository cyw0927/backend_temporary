from fastapi import FastAPI

from app.api.health import router as health_router
from app.modules.grading.router import router as grading_router
from app.modules.housing.router import router as housing_router
from app.modules.identity.router import router as identity_router
from app.modules.learning.router import router as learning_router
from app.modules.shop.router import router as shop_router


def create_app() -> FastAPI:
    app = FastAPI(title="Cat Game Backend", version="0.1.0")
    app.include_router(health_router)
    app.include_router(identity_router)
    app.include_router(learning_router)
    app.include_router(grading_router)
    app.include_router(shop_router)
    app.include_router(housing_router)
    return app


app = create_app()
