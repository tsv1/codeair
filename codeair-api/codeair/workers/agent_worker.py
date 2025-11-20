import asyncio
import time
from logging import Logger

import httpx
from codeair.config import Config
from codeair.domain.agents import Agent, AgentEngine, AgentType
from codeair.domain.job_logs import JobLog, JobLogRepository
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
        job_log_repository: JobLogRepository,
        logger: Logger,
    ) -> None:
        self._job_queue_service = job_queue_service
        self._agent_service = agent_service
        self._http_client = http_client
        self._job_log_repository = job_log_repository
        self._logger = logger
        self._running = False
        self._poll_interval = 1.0  # seconds

    async def _run_mr_describer(self, job: Job, agent: Agent) -> None:
        mr_url = job.payload.get("mr_url")
        if not mr_url:
            self._logger.error(f"No MR URL found in job {job.id} payload")
            return

        self._logger.info(f"Running pr_agent describe for job {job.id} on {mr_url}")

        env = {
            'CONFIG__GIT_PROVIDER': 'gitlab',
            'CONFIG__MODEL': agent.config.model,
            'GITLAB__URL': Config.GitLab.API_BASE_URL,
            'GITLAB__PERSONAL_ACCESS_TOKEN': Config.GitLab.BOT_TOKEN,
            'ANTHROPIC__KEY': agent.config.token,
            'ANTHROPIC_API_BASE': Config.AI.PROVIDER_BASE_URL,
        }
        if agent.config.prompt:
            env['PR_DESCRIPTION__EXTRA_INSTRUCTIONS'] = agent.config.prompt

        start_time = time.time()
        process = await asyncio.create_subprocess_exec(
            '/usr/local/bin/python3', '-m', 'pr_agent.cli',
            f'--pr_url={mr_url}',
            'describe',
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600.0)  # 10 minutes
            elapsed_ms = int((time.time() - start_time) * 1000)  # Convert to milliseconds

            job_log = JobLog(
                job_id=job.id,
                exit_code=process.returncode,
                stdout=stdout.decode().strip() if stdout else None,
                stderr=stderr.decode().strip() if stderr else None,
                elapsed_ms=elapsed_ms,
            )
            await self._job_log_repository.create(job_log)
        except asyncio.TimeoutError:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self._logger.error(f"pr_agent describe timed out after 10 minutes for job {job.id}")

            # Try to kill the process
            try:
                process.kill()
                await process.wait()
            except Exception as e:
                self._logger.error(f"Failed to kill process for job {job.id}: {e}")

            # Save log with timeout error
            job_log = JobLog(
                job_id=job.id,
                exit_code=-2,  # Timeout exit code
                stdout=None,
                stderr="Process timed out after 10 minutes",
                elapsed_ms=elapsed_ms,
            )
            await self._job_log_repository.create(job_log)
            raise

    async def _run_mr_reviewer(self, job: Job, agent: Agent) -> None:
        mr_url = job.payload.get("mr_url")
        if not mr_url:
            self._logger.error(f"No MR URL found in job {job.id} payload")
            return

        self._logger.info(f"Running pr_agent improve for job {job.id} on {mr_url}")

        env = {
            'CONFIG__GIT_PROVIDER': 'gitlab',
            'CONFIG__MODEL': agent.config.model,
            'GITLAB__URL': Config.GitLab.API_BASE_URL,
            'GITLAB__PERSONAL_ACCESS_TOKEN': Config.GitLab.BOT_TOKEN,
            'ANTHROPIC__KEY': agent.config.token,
            'ANTHROPIC_API_BASE': Config.AI.PROVIDER_BASE_URL,
        }
        if agent.config.prompt:
            env['PR_CODE_SUGGESTIONS__EXTRA_INSTRUCTIONS'] = agent.config.prompt

        env["PR_CODE_SUGGESTIONS__COMMITABLE_CODE_SUGGESTIONS"] = "true"
        env["PR_CODE_SUGGESTIONS__SUGGESTIONS_SCORE_THRESHOLD"] = "4"
        env["PR_CODE_SUGGESTIONS__NUM_CODE_SUGGESTIONS_PER_CHUNK"] = "5"

        start_time = time.time()
        process = await asyncio.create_subprocess_exec(
            '/usr/local/bin/python3', '-m', 'pr_agent.cli',
            f'--pr_url={mr_url}',
            'improve',
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600.0)  # 10 minutes
            elapsed_ms = int((time.time() - start_time) * 1000)  # Convert to milliseconds

            job_log = JobLog(
                job_id=job.id,
                exit_code=process.returncode,
                stdout=stdout.decode().strip() if stdout else None,
                stderr=stderr.decode().strip() if stderr else None,
                elapsed_ms=elapsed_ms,
            )
            await self._job_log_repository.create(job_log)
        except asyncio.TimeoutError:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self._logger.error(f"pr_agent improve timed out after 10 minutes for job {job.id}")

            # Try to kill the process
            try:
                process.kill()
                await process.wait()
            except Exception as e:
                self._logger.error(f"Failed to kill process for job {job.id}: {e}")

            # Save log with timeout error
            job_log = JobLog(
                job_id=job.id,
                exit_code=-2,  # Timeout exit code
                stdout=None,
                stderr="Process timed out after 10 minutes",
                elapsed_ms=elapsed_ms,
            )
            await self._job_log_repository.create(job_log)
            raise

    async def _process_external_engine(self, job: Job, agent: Agent) -> None:
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
            "prompt": agent.config.prompt,
        }

        self._logger.info(f"Calling external URL {agent.config.external_url} for job {job.id}")

        start_time = time.time()
        exit_code = 0
        stdout_str = None
        stderr_str = None

        try:
            response = await self._http_client.post(str(agent.config.external_url), json=request_body, timeout=30.0)
            response.raise_for_status()

            try:
                response_body = response.json()
                exit_code = response_body.get('exit_code', 0)
                stdout_str = response_body.get('stdout')
                stderr_str = response_body.get('stderr')
            except Exception:
                self._logger.warning(f"Could not parse response body as JSON for job {job.id}")

        except httpx.TimeoutException as e:
            exit_code = -2  # Timeout exit code
            stderr_str = f"HTTP request timed out after 30 seconds: {str(e)}"
            self._logger.error(f"HTTP timeout calling external URL for job {job.id}: {e}", exc_info=True)
            raise
        except httpx.HTTPStatusError as e:
            exit_code = e.response.status_code
            stderr_str = e.response.text
            self._logger.error(f"HTTP error calling external URL for job {job.id}: {e}", exc_info=True)
            raise
        except Exception as e:
            exit_code = -1
            stderr_str = str(e)
            self._logger.error(f"Error calling external URL for job {job.id}: {e}", exc_info=True)
            raise
        finally:
            elapsed_ms = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            job_log = JobLog(
                job_id=job.id,
                exit_code=exit_code,
                stdout=stdout_str,
                stderr=stderr_str,
                elapsed_ms=elapsed_ms,
            )
            await self._job_log_repository.create(job_log)

    async def _process_pr_agent_v0_29(self, job: Job, agent: Agent) -> None:
        if agent.type == AgentType.MR_DESCRIBER:
            await self._run_mr_describer(job, agent)
        elif agent.type == AgentType.MR_REVIEWER:
            await self._run_mr_reviewer(job, agent)
        else:
            self._logger.error(f"Unknown agent type {agent.type} for job {job.id}")

    async def _process_job(self, job: Job) -> None:
        agent = await self._agent_service.get_agent_with_raw_token(job.agent_id)

        if not agent.enabled:
            self._logger.info(f"Agent {agent.id} is disabled, skipping job {job.id}")
            return

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
