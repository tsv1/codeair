import asyncio
from logging import Logger

import httpx
from codeair.domain.agents import Agent, AgentEngine, AgentType
from codeair.domain.jobs import Job
from codeair.services.agent_service import AgentService
from codeair.services.job_queue_service import JobQueueService
from codeair.workers.base_worker import BaseWorker

__all__ = ["AgentWorker"]


class AgentWorker(BaseWorker):
    def __init__(
        self,
        job_queue_service: JobQueueService,
        agent_service: AgentService,
        http_client: httpx.AsyncClient,
        logger: Logger,
    ) -> None:
        self._job_queue_service = job_queue_service
        self._agent_service = agent_service
        self._http_client = http_client
        self._logger = logger
        self._running = False
        self._poll_interval = 1.0  # seconds

    async def _run_mr_describer(self, job_id: int) -> None:
        self._logger.info(f"Running echo mr-describer for job {job_id}")
        process = await asyncio.create_subprocess_shell(
            "echo mr-describer",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={},
        )
        stdout, stderr = await process.communicate()
        exit_code = process.returncode
        stdout_str = stdout.decode().strip() if stdout else ""
        stderr_str = stderr.decode().strip() if stderr else ""

        if stdout:
            self._logger.info(f"mr-reviewer output: {stdout_str}")
        if stderr:
            self._logger.info(f"mr-reviewer error: {stderr_str}")
        self._logger.info(f"mr-describer exit code: {exit_code}")

    async def _run_mr_reviewer(self, job_id: int) -> None:
        self._logger.info(f"Running mr-reviewer for job {job_id}")
        process = await asyncio.create_subprocess_shell(
            "mr-reviewer",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        exit_code = process.returncode
        stdout_str = stdout.decode().strip() if stdout else ""
        stderr_str = stderr.decode().strip() if stderr else ""

        if stdout:
            self._logger.info(f"mr-reviewer output: {stdout_str}")
        if stderr:
            self._logger.info(f"mr-reviewer error: {stderr_str}")
        self._logger.info(f"mr-describer exit code: {exit_code}")

    async def _process_external_engine(self, job: Job, agent: Agent) -> None:
        if not agent.enabled:
            self._logger.info(f"Agent {agent.id} is disabled, skipping job {job.id}")
            return

        mr_url = job.payload.get("mr_url")
        if not mr_url:
            self._logger.error(f"No MR URL found in job {job.id} payload")
            return

        request_body = {
            "agent_id": str(agent.id),
            "agent_type": agent.type.value,
            "mr_url": mr_url,
            "provider": agent.config.provider.value,
            "model": agent.config.model,
            "token": agent.config.token,
        }

        self._logger.info(f"Calling external URL {agent.config.external_url} for job {job.id}")
        try:
            response = await self._http_client.post(str(agent.config.external_url), json=request_body)
            response.raise_for_status()
        except Exception as e:
            self._logger.error(f"Error calling external URL for job {job.id}: {e}", exc_info=True)
            raise
        else:
            self._logger.info(f"External call completed for job {job.id}: {response.status_code}")

    async def _process_pr_agent_v0_29(self, job: Job, agent: Agent) -> None:
        if agent.type == AgentType.MR_DESCRIBER:
            await self._run_mr_describer(job.id)
        elif agent.type == AgentType.MR_REVIEWER:
            await self._run_mr_reviewer(job.id)
        else:
            self._logger.error(f"Unknown agent type {agent.type} for job {job.id}")

    async def _process_job(self, job: Job) -> None:
        agent = await self._agent_service.get_agent_with_raw_token(job.agent_id)

        self._logger.info(
            f"Processing job {job.id} for agent {agent.id} (type={agent.type}, engine={agent.engine})"
        )

        if agent.engine == AgentEngine.EXTERNAL:
            await self._process_external_engine(job, agent)
        elif agent.engine == AgentEngine.PR_AGENT_V0_29:
            await self._process_pr_agent_v0_29(job, agent)
        else:
            self._logger.error(f"Unknown engine type {agent.engine} for job {job.id}")

    async def run(self) -> None:
        self._running = True
        self._logger.info("Agent worker started, waiting for jobs...")

        while self._running:
            try:
                job = await self._job_queue_service.claim_next_job()
                if job:
                    self._logger.info(f"Processing job {job.id} for agent {job.agent_id}")
                    await self._process_job(job)
                    await self._job_queue_service.complete_job(job.id)
                    self._logger.info(f"Job {job.id} completed successfully")
                else:
                    await asyncio.sleep(self._poll_interval)
            except Exception as e:
                self._logger.error(f"Error processing job: {e}", exc_info=True)
                await asyncio.sleep(1)

    async def cleanup(self) -> None:
        self._logger.info("Stopping agent worker...")
        self._running = False
