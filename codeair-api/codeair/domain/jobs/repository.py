import json
from logging import Logger
from uuid import UUID

from codeair.clients.database import DatabaseClient, Record
from codeair.domain.jobs import Job

__all__ = ["JobRepository"]


class JobRepository:
    def __init__(self, db_client: DatabaseClient, logger: Logger) -> None:
        self._db_client = db_client
        self._logger = logger

    def _row_to_job(self, row: Record) -> Job:
        payload_data = json.loads(row["payload"]) if isinstance(row["payload"], str) else row["payload"]
        return Job(
            id=row["id"],
            agent_id=row["agent_id"],
            payload=payload_data,
            created_at=row["created_at"],
            started_at=row.get("started_at"),
            ended_at=row.get("ended_at"),
        )

    async def create(self, job: Job) -> Job:
        payload_json = json.dumps(job.payload)

        sql = """
            INSERT INTO jobs (agent_id, payload, created_at, started_at, ended_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, agent_id, payload, created_at, started_at, ended_at
        """
        row = await self._db_client.fetch_one(
            sql,
            job.agent_id,
            payload_json,
            job.created_at,
            job.started_at,
            job.ended_at,
        )

        return self._row_to_job(row)

    async def find_by_agent_id(self, agent_id: UUID) -> list[Job]:
        sql = """
            SELECT id, agent_id, payload, created_at, started_at, ended_at
            FROM jobs
            WHERE agent_id = $1
            ORDER BY created_at DESC
        """
        rows = await self._db_client.fetch_many(sql, agent_id)
        return [self._row_to_job(row) for row in rows]

    async def claim_next_job(self) -> Job | None:
        sql = """
            UPDATE jobs
            SET started_at = NOW()
            WHERE id = (
                SELECT id FROM jobs
                WHERE started_at IS NULL
                ORDER BY created_at ASC
                LIMIT 1
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id, agent_id, payload, created_at, started_at, ended_at
        """
        row = await self._db_client.fetch_one(sql)
        return self._row_to_job(row) if row else None

    async def complete_job(self, job_id: int) -> Job | None:
        sql = """
            UPDATE jobs
            SET ended_at = NOW()
            WHERE id = $1
            RETURNING id, agent_id, payload, created_at, started_at, ended_at
        """
        row = await self._db_client.fetch_one(sql, job_id)
        return self._row_to_job(row) if row else None
