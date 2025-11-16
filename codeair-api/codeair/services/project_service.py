from logging import Logger

from codeair.clients.gitlab import GitlabNotFoundError
from codeair.domain.errors import EntityNotFoundError
from codeair.domain.projects.models import Project
from codeair.domain.projects.repository import ProjectRepository

__all__ = ["ProjectService"]


class ProjectService:
    def __init__(self, project_repository: ProjectRepository, bot_token: str, logger: Logger) -> None:
        self._project_repository = project_repository
        self._bot_token = bot_token
        self._logger = logger

    async def search_projects(self, query: str) -> list[Project]:
        return await self._project_repository.search(query, self._bot_token)

    async def get_project_by_id(self, project_id: int) -> Project:
        try:
            return await self._project_repository.get_by_id(project_id, self._bot_token)
        except GitlabNotFoundError as e:
            raise EntityNotFoundError("Project not found") from e
