import asyncio
from datetime import datetime
from enum import StrEnum
from typing import Optional

from codeair.clients import DatabaseClient, GitLabClient
from codeair.config import Config as cfg
from litestar import Response, Router, get
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from pydantic import BaseModel, Field

__all__ = ["healthcheck_router"]


STARTUP_TIME = datetime.now()


def get_uptime_seconds() -> int:
    return int((datetime.now() - STARTUP_TIME).total_seconds())


def get_current_timestamp() -> str:
    return datetime.now().isoformat()


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class CheckStatus(StrEnum):
    OK = "ok"
    FAILED = "failed"


class HealthResponse(BaseModel):
    status: HealthStatus
    service: str = Field(default=cfg.App.NAME)
    timestamp: str = Field(default_factory=get_current_timestamp)
    version: str = Field(default=cfg.App.VERSION)
    uptime_seconds: int = Field(default_factory=get_uptime_seconds)


class HealthCheckResult(BaseModel):
    status: CheckStatus
    message: Optional[str] = None


class DetailedHealthResponse(HealthResponse):
    checks: dict[str, HealthCheckResult]



@get("/api/v1/healthcheck")
async def healthcheck() -> Response[HealthResponse]:
    return Response(
        content=HealthResponse(
            status=HealthStatus.HEALTHY,
        ),
        status_code=HTTP_200_OK,
    )


@get("/api/v1/healthcheck/detailed")
async def detailed_healthcheck(
    db_client: DatabaseClient,
    gitlab_client: GitLabClient,
) -> Response[DetailedHealthResponse]:
    overall_status = HealthStatus.HEALTHY
    database_check = HealthCheckResult(status=CheckStatus.OK)
    gitlab_check = HealthCheckResult(status=CheckStatus.OK)

    db_result, gitlab_result = await asyncio.gather(
        db_client.healthcheck(),
        gitlab_client.healthcheck(),
        return_exceptions=True,
    )

    if isinstance(db_result, Exception):
        database_check = HealthCheckResult(status=CheckStatus.FAILED)
        print("Database healthcheck failed:", db_result)
        overall_status = HealthStatus.DEGRADED

    if isinstance(gitlab_result, Exception):
        gitlab_check = HealthCheckResult(status=CheckStatus.FAILED)
        print("GitLab healthcheck failed:", gitlab_result)
        overall_status = HealthStatus.DEGRADED

    if overall_status == HealthStatus.HEALTHY:
        status_code = HTTP_200_OK
    else:
        status_code = HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        content=DetailedHealthResponse(
            status=overall_status,
            checks={
                "database": database_check,
                "gitlab": gitlab_check,
            },
        ),
        status_code=status_code,
    )


healthcheck_router = Router(
    path="",
    route_handlers=[
        healthcheck,
        detailed_healthcheck,
    ],
)
