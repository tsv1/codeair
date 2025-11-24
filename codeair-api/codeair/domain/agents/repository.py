import json
from logging import Logger
from uuid import UUID

from codeair.clients.database import DatabaseClient, Record
from codeair.domain.agents import Agent, AgentConfig

__all__ = ["AgentRepository"]


class AgentRepository:
    def __init__(self, db_client: DatabaseClient, logger: Logger) -> None:
        self._db_client = db_client
        self._logger = logger

    def _row_to_agent(self, row: Record) -> Agent:
        config_data = json.loads(row["config"]) if isinstance(row["config"], str) else row["config"]
        config = AgentConfig(**config_data)
        return Agent(
            id=row["id"],
            type=row["agent_type"],
            engine=row["engine"],
            name=row["name"],
            description=row["description"],
            enabled=row["enabled"],
            config=config,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        # Note: created_by and updated_by are stored in DB but not exposed in the model

    async def find_by_id(self, agent_id: UUID) -> Agent | None:
        sql = """
            SELECT id, agent_type, engine, name, description, enabled, config,
                   created_at, updated_at
            FROM agents
            WHERE id = $1
        """
        row = await self._db_client.fetch_one(sql, agent_id)
        return self._row_to_agent(row) if row else None

    async def find_by_project_id(self, project_id: int) -> list[Agent]:
        sql = """
            SELECT id, agent_type, engine, name, description, enabled, config,
                   created_at, updated_at
            FROM agents
            WHERE project_id = $1
            ORDER BY agent_type ASC, created_at DESC
        """
        rows = await self._db_client.fetch_many(sql, project_id)
        return [self._row_to_agent(row) for row in rows]

    async def save(self, project_id: int, agent: Agent, user_id: int) -> Agent:
        config_json = json.dumps(agent.config.model_dump(mode="json"))

        sql = """
            INSERT INTO agents
            (id, project_id, agent_type, engine, name, description, enabled, config,
             created_at, created_by, updated_at, updated_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), $9, NOW(), $10)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                enabled = EXCLUDED.enabled,
                config = EXCLUDED.config,
                updated_at = NOW(),
                updated_by = EXCLUDED.updated_by
            RETURNING id, agent_type, engine, name, description, enabled, config,
                      created_at, updated_at
        """
        row = await self._db_client.fetch_one(
            sql,
            agent.id,
            project_id,
            agent.type,
            agent.engine,
            agent.name,
            agent.description,
            agent.enabled,
            config_json,
            user_id,
            user_id,
        )

        return self._row_to_agent(row)
