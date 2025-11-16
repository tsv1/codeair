from typing import Annotated, Any
from uuid import UUID

from litestar import Response, Router, post
from litestar.params import Body, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from pydantic import BaseModel

from codeair.domain.projects import ProjectRepository
from codeair.services.job_queue_service import JobQueueService

__all__ = ["webhook_router"]


class WebhookPayload(BaseModel):
    event_type: str | None = None
    object_attributes: dict[str, Any] | None = None


class WebhookResponse(BaseModel):
    message: str


@post("/api/v1/webhooks/{webhook_id:str}")
async def handle_webhook(
    webhook_id: Annotated[UUID, Parameter()],
    data: Annotated[WebhookPayload, Body()],
    project_repository: ProjectRepository,
    job_queue_service: JobQueueService,
) -> Response[WebhookResponse]:
    project_id = await project_repository.get_project_id_by_webhook(webhook_id)

    if not project_id:
        return Response(
            status_code=HTTP_404_NOT_FOUND,
            content=WebhookResponse(message=f"Webhook {webhook_id} not found")
        )

    # Check if this is a merge_request open event
    if (
        data.event_type == "merge_request"
        and data.object_attributes
        and data.object_attributes.get("action") == "open"
    ):
        # Extract the MR URL and create payload
        mr_url = data.object_attributes.get("url")
        payload = {
            "mr_url": mr_url,
        }

        # Enqueue jobs for all enabled agents
        jobs = await job_queue_service.enqueue_jobs_for_project(project_id, payload)

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
