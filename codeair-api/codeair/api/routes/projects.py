import asyncio
from typing import Annotated

from codeair.domain.projects import Project
from codeair.domain.users import User
from codeair.services.project_service import ProjectService
from codeair.services.user_service import UserService
from litestar import Router, get
from litestar.params import Parameter
from pydantic import BaseModel

__all__ = ["project_router"]


class ProjectSearchResponse(BaseModel):
    total: int
    items: list[Project]
    bot_user: User


class ProjectDetailResponse(BaseModel):
    project: Project


@get("/api/v1/projects/search")
async def search_projects(
    q: Annotated[str, Parameter(min_length=1)],
    project_service: ProjectService,
    user_service: UserService,
) -> ProjectSearchResponse:
    projects, bot_user = await asyncio.gather(
        project_service.search_projects(q),
        user_service.get_bot_user_info(),
    )
    return ProjectSearchResponse(
        total=len(projects),
        items=projects,
        bot_user=bot_user,
    )


@get("/api/v1/projects/{project_id:str}")
async def get_project(
    project_id: Annotated[int, Parameter(gt=0)],
    project_service: ProjectService,
) -> ProjectDetailResponse:
    project = await project_service.get_project_by_id(project_id)
    return ProjectDetailResponse(project=project)


project_router = Router(
    path="",
    route_handlers=[
        search_projects,
        get_project,
    ],
)
