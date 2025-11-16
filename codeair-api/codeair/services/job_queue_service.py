from logging import Logger

from codeair.domain.agents import AgentRepository
from codeair.domain.jobs import Job
from codeair.domain.jobs.repository import JobRepository

__all__ = ["JobQueueService"]


class JobQueueService:
    def __init__(
        self,
        job_repository: JobRepository,
        agent_repository: AgentRepository,
        logger: Logger,
    ):
        self._job_repository = job_repository
        self._agent_repository = agent_repository
        self._logger = logger

    async def enqueue_jobs_for_project(self, project_id: int, payload: dict) -> list[Job]:
        agents = await self._agent_repository.find_by_project_id(project_id)

        enabled_agents = [agent for agent in agents if agent.enabled]

        created_jobs = []
        for agent in enabled_agents:
            job = Job(
                agent_id=agent.id,
                payload=payload,
            )
            created_job = await self._job_repository.create(job)
            created_jobs.append(created_job)
            self._logger.info(
                f"Created job {created_job.id} for agent {agent.id} (type={agent.type})"
            )

        return created_jobs

    async def get_pending_job(self) -> list[Job]:
        return await self._job_repository.find_pending_job()

    async def start_job(self, job_id: int) -> Job | None:
        return await self._job_repository.start_job(job_id)

    async def end_job(self, job_id: int) -> Job | None:
        return await self._job_repository.end_job(job_id)
