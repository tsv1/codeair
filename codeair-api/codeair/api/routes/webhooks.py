from enum import StrEnum
from typing import Annotated
from uuid import UUID

from codeair.domain.projects import ProjectRepository
from codeair.services.job_queue_service import JobQueueService
from litestar import Response, Router, post
from litestar.params import Body, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from pydantic import BaseModel, Field, HttpUrl

__all__ = ["webhook_router"]


class WebhookEventType(StrEnum):
    MERGE_REQUEST = "merge_request"


class MergeRequestAction(StrEnum):
    OPEN = "open"
    UPDATE = "update"
    CLOSE = "close"
    MERGE = "merge"


class ObjectAttributes(BaseModel):
    action: str | None = Field(default=None, min_length=1)
    url: HttpUrl | None = Field(default=None)


class WebhookPayload(BaseModel):
    event_type: str | None = Field(default=None, min_length=1)
    object_attributes: ObjectAttributes | None = Field(default=None)


class WebhookResponse(BaseModel):
    message: str


def is_merge_request_open_event(data: WebhookPayload) -> bool:
    return (
        data.event_type == WebhookEventType.MERGE_REQUEST
        and data.object_attributes is not None
        and data.object_attributes.action == MergeRequestAction.OPEN
    )


@post("/api/v1/webhooks/{webhook_id:str}")
async def handle_webhook(
    webhook_id: Annotated[UUID, Parameter()],
    data: Annotated[WebhookPayload, Body()],
    project_repository: ProjectRepository,
    job_queue_service: JobQueueService,
) -> Response[WebhookResponse]:
    project_id = await project_repository.get_project_id_by_webhook_id(webhook_id)

    if not project_id:
        return Response(
            status_code=HTTP_404_NOT_FOUND,
            content=WebhookResponse(message=f"Webhook {webhook_id} not found")
        )

    if is_merge_request_open_event(data):
        jobs = await job_queue_service.enqueue_jobs_for_project(project_id, payload={
            "mr_url": str(data.object_attributes.url),
        })

        return Response(
            status_code=HTTP_200_OK,
            content=WebhookResponse(
                message=f"Created {len(jobs)} job(s) for project {project_id}"
            )
        )

    return Response(
        status_code=HTTP_200_OK,
        content=WebhookResponse(message=f"Webhook received for project {project_id}")
    )


webhook_router = Router(
    path="",
    route_handlers=[handle_webhook],
)
