from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from codeair.config import Config
from codeair.domain.agents.models import Agent, AgentConfig, AgentEngine, AgentProvider, AgentType
from codeair.domain.job_logs import JobLogRepository
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


class JobLogResponse(BaseModel):
    job_id: int
    mr_url: str
    created_at: datetime
    started_at: datetime | None
    ended_at: datetime | None
    exit_code: int | None
    stdout: str | None
    stderr: str | None
    elapsed_ms: int | None


class AgentLogsResponse(BaseModel):
    total: int
    logs: list[JobLogResponse]


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


@get("/api/v1/projects/{project_id:str}/agents/{agent_id:str}/logs")
async def get_agent_logs(
    project_id: Annotated[int, Parameter(gt=0)],
    agent_id: Annotated[UUID, Parameter()],
    limit: Annotated[int, Parameter(gt=0, le=100, default=10)],
    project_service: ProjectService,
    agent_service: AgentService,
    job_log_repository: JobLogRepository,
) -> Response[AgentLogsResponse]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    # Verify agent exists and belongs to the project
    agent: Agent = await agent_service.get_agent(agent_id)

    # Get logs for this agent
    logs_data = await job_log_repository.find_by_agent_id(str(agent.id), limit=limit)
    logs = [
        JobLogResponse(
            job_id=log["job_id"],
            mr_url=log["mr_url"],
            created_at=log["created_at"],
            started_at=log.get("started_at"),
            ended_at=log.get("ended_at"),
            exit_code=log.get("exit_code"),
            stdout=log.get("stdout"),
            stderr=log.get("stderr"),
            elapsed_ms=log.get("elapsed_ms"),
        )
        for log in logs_data
    ]

    return Response(
        status_code=HTTP_200_OK,
        content=AgentLogsResponse(
            total=len(logs),
            logs=logs
        )
    )


@get("/api/v1/projects/{project_id:str}/agents/{agent_id:str}/logs/{job_id:int}")
async def get_job_log(
    project_id: Annotated[int, Parameter(gt=0)],
    agent_id: Annotated[UUID, Parameter()],
    job_id: Annotated[int, Parameter(gt=0)],
    project_service: ProjectService,
    agent_service: AgentService,
    job_log_repository: JobLogRepository,
) -> Response[JobLogResponse]:
    # Fetch project from GitLab to ensure it exists
    await project_service.get_project_by_id(project_id)

    # Verify agent exists and belongs to the project
    agent: Agent = await agent_service.get_agent(agent_id)

    # Get the specific job log
    log_data = await job_log_repository.find_by_job_id_with_details(job_id, str(agent.id))

    if not log_data:
        raise Exception("Job log not found")

    log = JobLogResponse(
        job_id=log_data["job_id"],
        mr_url=log_data["mr_url"],
        created_at=log_data["created_at"],
        started_at=log_data.get("started_at"),
        ended_at=log_data.get("ended_at"),
        exit_code=log_data.get("exit_code"),
        stdout=log_data.get("stdout"),
        stderr=log_data.get("stderr"),
        elapsed_ms=log_data.get("elapsed_ms"),
    )

    return Response(
        status_code=HTTP_200_OK,
        content=log
    )


agent_router = Router(
    path="",
    route_handlers=[create_agent, list_agents, get_agent_placeholders, get_agent,
                    update_agent, get_agent_logs, get_job_log],
)
