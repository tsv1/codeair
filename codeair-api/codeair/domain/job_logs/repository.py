from logging import Logger

from codeair.clients.database import DatabaseClient, Record
from codeair.domain.job_logs import JobLog

__all__ = ["JobLogRepository"]


class JobLogRepository:
    def __init__(self, db_client: DatabaseClient, logger: Logger) -> None:
        self._db_client = db_client
        self._logger = logger

    def _row_to_job_log(self, row: Record) -> JobLog:
        return JobLog(
            job_id=row["job_id"],
            exit_code=row["exit_code"],
            stdout=row.get("stdout"),
            stderr=row.get("stderr"),
            elapsed_ms=row["elapsed_ms"],
            created_at=row["created_at"],
        )

    async def create(self, job_log: JobLog) -> JobLog:
        sql = """
            INSERT INTO job_logs (job_id, exit_code, stdout, stderr, elapsed_ms, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING job_id, exit_code, stdout, stderr, elapsed_ms, created_at
        """
        row = await self._db_client.fetch_one(
            sql,
            job_log.job_id,
            job_log.exit_code,
            job_log.stdout,
            job_log.stderr,
            job_log.elapsed_ms,
            job_log.created_at,
        )

        return self._row_to_job_log(row)

    async def find_by_job_id(self, job_id: int) -> JobLog | None:
        sql = """
            SELECT job_id, exit_code, stdout, stderr, elapsed_ms, created_at
            FROM job_logs
            WHERE job_id = $1
        """
        row = await self._db_client.fetch_one(sql, job_id)
        return self._row_to_job_log(row) if row else None

    async def find_by_job_id_with_details(self, job_id: int, agent_id: str) -> dict | None:
        sql = """
            SELECT
                j.id as job_id,
                j.payload->>'mr_url' as mr_url,
                j.created_at,
                j.started_at,
                j.ended_at,
                jl.exit_code,
                jl.stdout,
                jl.stderr,
                jl.elapsed_ms
            FROM jobs j
            LEFT JOIN job_logs jl ON j.id = jl.job_id
            WHERE j.id = $1 AND j.agent_id = $2
        """
        row = await self._db_client.fetch_one(sql, job_id, agent_id)
        return dict(row) if row else None

    async def find_by_agent_id(self, agent_id: str, limit: int = 10) -> list[dict]:
        sql = """
            SELECT
                j.id as job_id,
                j.payload->>'mr_url' as mr_url,
                j.created_at,
                j.started_at,
                j.ended_at,
                jl.exit_code,
                jl.stdout,
                jl.stderr,
                jl.elapsed_ms
            FROM jobs j
            LEFT JOIN job_logs jl ON j.id = jl.job_id
            WHERE j.agent_id = $1
            ORDER BY j.created_at DESC
            LIMIT $2
        """
        rows = await self._db_client.fetch_many(sql, agent_id, limit)
        return [dict(row) for row in rows]
