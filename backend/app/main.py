import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router
from app.core.config import Settings
from app.core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        configure_logging(settings.log_level)
        logger = logging.getLogger("careermatch")
        application.state.ready = True
        logger.info("application_started")
        try:
            yield
        finally:
            application.state.ready = False
            logger.info("application_stopped")

    application = FastAPI(title="CareerMatch AI", version="0.1.0", lifespan=lifespan)
    application.state.ready = False
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["Accept", "Content-Type"],
    )
    application.include_router(router)
    return application


app = create_app()
