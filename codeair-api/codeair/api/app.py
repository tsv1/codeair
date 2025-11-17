import logging
from pathlib import Path

from codeair.api.error_handlers import (domain_exception_handler, generic_exception_handler, http_exception_handler,
                                        validation_exception_handler)
from codeair.api.routes import (agent_router, auth_router, healthcheck_router, project_router, static_router,
                                webhook_router)
from codeair.config import Config
from codeair.di.containers import api_dependencies
from codeair.di.providers import DatabaseClientManager, HTTPClientManager, jwt_auth
from codeair.domain.errors import DomainError
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.exceptions import HTTPException, ValidationException
from litestar.logging import LoggingConfig
from litestar.static_files import create_static_files_router

logger = logging.getLogger(__name__)


def create_app() -> Litestar:
    logging_config = LoggingConfig(
        root={"level": logging.getLevelName(Config.Logging.LEVEL), "handlers": ["console"]},
        formatters={
            "standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        },
    )

    cors_config = CORSConfig(
        allow_origins=list(Config.CORS.ALLOW_ORIGINS),
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True,
        max_age=600,
    )

    async def on_startup(app: Litestar) -> None:
        logger.info("CodeAir server is starting up...")
        logger.info(f"Connecting to database: {Config.Database.URL}")
        await DatabaseClientManager.get_client()
        HTTPClientManager.get_client()
        logger.info("Database and HTTP clients initialized")

    async def on_shutdown(app: Litestar) -> None:
        logger.info("CodeAir server is shutting down...")
        await DatabaseClientManager.shutdown()
        await HTTPClientManager.shutdown()
        logger.info("All clients shut down")

    static_files_router = create_static_files_router(
        path="/assets",
        directories=[Config.App.STATIC_DIR / "assets"],
        html_mode=True,
        name="static",
    )

    return Litestar(
        route_handlers=[
            agent_router,
            auth_router,
            healthcheck_router,
            project_router,
            webhook_router,
            static_files_router,
            static_router,
        ],
        dependencies=api_dependencies,
        cors_config=cors_config,
        logging_config=logging_config,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        on_app_init=[jwt_auth.on_app_init],
        exception_handlers={
            DomainError: domain_exception_handler,
            HTTPException: http_exception_handler,
            ValidationException: validation_exception_handler,
            Exception: generic_exception_handler,
        },
    )
