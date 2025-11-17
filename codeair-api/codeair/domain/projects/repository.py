from logging import Logger
from uuid import UUID, uuid4

from codeair.clients import GitLabClient
from codeair.clients.database import DatabaseClient
from codeair.domain.projects.models import Project

__all__ = ["ProjectRepository"]


class ProjectRepository:
    def __init__(self, gitlab_client: GitLabClient, db_client: DatabaseClient, logger: Logger) -> None:
        self._gitlab_client = gitlab_client
        self._db_client = db_client
        self._logger = logger

    async def get_by_id(self, project_id: int, user_token: str) -> Project:
        data = await self._gitlab_client.get_project(project_id, user_token)
        return Project(**data)

    async def search(self, query: str, user_token: str) -> list[Project]:
        projects_data = await self._gitlab_client.search_projects(query, user_token)
        return [Project(**project) for project in projects_data]

    async def save_to_db(self, project_id: int, created_by: int) -> UUID:
        sql = """
            INSERT INTO projects (id, created_at, created_by, webhook_id)
            VALUES ($1, NOW(), $2, $3)
            ON CONFLICT (id) DO UPDATE
            SET webhook_id = COALESCE(projects.webhook_id, $3)
            RETURNING webhook_id
        """
        webhook_id = uuid4()
        result = await self._db_client.fetch_one(sql, project_id, created_by, webhook_id)
        return result["webhook_id"]

    async def get_webhook_id_project_id(self, project_id: int) -> UUID | None:
        sql = "SELECT webhook_id FROM projects WHERE id = $1"
        result = await self._db_client.fetch_one(sql, project_id)
        return result["webhook_id"] if result else None

    async def get_project_id_by_webhook_id(self, webhook_id: UUID) -> int:
        sql = "SELECT id FROM projects WHERE webhook_id = $1"
        result = await self._db_client.fetch_one(sql, webhook_id)
        return result["id"] if result else None
