from typing import Annotated, Any
from uuid import UUID

from litestar import Response, Router, get, patch, post
from litestar.params import Body, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from pydantic import BaseModel

from codeair.domain.agents.models import Agent
from codeair.domain.projects import ProjectRepository
from codeair.domain.users import User
from codeair.services import AgentService, WebhookService
from codeair.services.project_service import ProjectService

__all__ = ["agent_router"]


class AgentDetailResponse(BaseModel):
    agent: Agent


class AgentsListResponse(BaseModel):
    total: int
    agents: list[Agent]


@post("/api/v1/projects/{project_id:str}/agents")
async def create_agent(
    project_id: Annotated[int, Parameter(gt=0)],
    data: Annotated[Agent, Body()],
    agent_service: AgentService,
    project_repository: ProjectRepository,
    project_service: ProjectService,
    webhook_service: WebhookService,
    current_user: User,
) -> Response[Any]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    webhook_id = await project_repository.save_to_db(project_id, current_user.id)
    await webhook_service.ensure_webhook(project_id, webhook_id)

    agent: Agent = await agent_service.create_agent(project_id, data, current_user.id)

    return Response(
        status_code=HTTP_201_CREATED,
        content=AgentDetailResponse(agent=agent)
    )


@get("/api/v1/projects/{project_id:str}/agents")
async def list_agents(
    project_id: Annotated[int, Parameter(gt=0)],
    project_service: ProjectService,
    agent_service: AgentService,
) -> Response[Any]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    agents: list[Agent] = await agent_service.list_agents(project_id)

    return Response(
        status_code=HTTP_200_OK,
        content=AgentsListResponse(
            total=len(agents),
            agents=agents
        )
    )


@get("/api/v1/projects/{project_id:str}/agents/{agent_id:str}")
async def get_agent(
    project_id: Annotated[int, Parameter(gt=0)],
    agent_id: Annotated[UUID, Parameter()],
    project_service: ProjectService,
    agent_service: AgentService,
) -> Response[Any]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    agent: Agent = await agent_service.get_agent(project_id, agent_id)

    return Response(
        status_code=HTTP_200_OK,
        content=AgentDetailResponse(agent=agent)
    )


@patch("/api/v1/projects/{project_id:str}/agents/{agent_id:str}")
async def update_agent(
    project_id: Annotated[int, Parameter(gt=0)],
    agent_id: Annotated[UUID, Parameter()],
    data: Annotated[Agent, Body()],
    project_service: ProjectService,
    agent_service: AgentService,
    current_user: User,
) -> Response[Any]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    agent: Agent = await agent_service.update_agent(project_id, agent_id, data, current_user.id)

    return Response(
        status_code=HTTP_200_OK,
        content=AgentDetailResponse(agent=agent)
    )


agent_router = Router(
    path="",
    route_handlers=[create_agent, list_agents, get_agent, update_agent],
)
