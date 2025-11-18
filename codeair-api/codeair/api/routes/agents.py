from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from codeair.config import Config
from codeair.domain.agents.models import Agent, AgentConfig, AgentEngine, AgentProvider, AgentType
from codeair.domain.projects import ProjectRepository
from codeair.domain.users import User
from codeair.services import AgentService, WebhookService
from codeair.services.project_service import ProjectService
from litestar import Response, Router, get, patch, post
from litestar.params import Body, Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from pydantic import BaseModel

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
    await webhook_service.create_or_update_webhook(project_id, webhook_id)

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

    agent: Agent = await agent_service.get_agent(agent_id)

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
    webhook_service: WebhookService,
    current_user: User,
) -> Response[Any]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    webhook_id = await webhook_service.get_webhook_id_by_project_id(project_id)
    if not webhook_id:
        raise Exception("Webhook ID not found for project")
    await webhook_service.create_or_update_webhook(project_id, webhook_id)

    agent: Agent = await agent_service.update_agent(project_id, agent_id, data, current_user.id)

    return Response(
        status_code=HTTP_200_OK,
        content=AgentDetailResponse(agent=agent)
    )


@get("/api/v1/projects/{project_id:str}/agents/placeholders")
async def get_agent_placeholders(
    project_id: Annotated[int, Parameter(gt=0)],
    project_service: ProjectService,
) -> Response[Any]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    now = datetime.utcnow()

    # Create placeholder config
    placeholder_config = AgentConfig(
        provider=AgentProvider(Config.AI.DEFAULT_PROVIDER),
        model=Config.AI.DEFAULT_MODEL,
        token=Config.AI.DEFAULT_TOKEN,
        prompt=None,
    )

    # Create MR Describer placeholder
    mr_describer = Agent(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        type=AgentType.MR_DESCRIBER,
        engine=AgentEngine.PR_AGENT_V0_29,
        name="MR Description Writer",
        description="Automatically generates and adds descriptions to merge requests",
        enabled=False,
        config=placeholder_config,
        created_at=now,
        updated_at=now,
    )

    # Create MR Reviewer placeholder
    mr_reviewer = Agent(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        type=AgentType.MR_REVIEWER,
        engine=AgentEngine.PR_AGENT_V0_29,
        name="MR Code Reviewer",
        description="Reviews merge requests and adds comments with suggestions",
        enabled=False,
        config=placeholder_config,
        created_at=now,
        updated_at=now,
    )

    return Response(
        status_code=HTTP_200_OK,
        content=AgentsListResponse(
            total=2,
            agents=[mr_describer, mr_reviewer]
        )
    )


agent_router = Router(
    path="",
    route_handlers=[create_agent, list_agents, get_agent_placeholders, get_agent, update_agent],
)
