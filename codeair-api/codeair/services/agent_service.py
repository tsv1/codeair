from logging import Logger
from uuid import UUID

from codeair.domain.agents import Agent, AgentProvider, AgentRepository, AgentType
from codeair.domain.errors import EntityNotFoundError, ValidationError
from codeair.services.token_encryption import TokenEncryption

__all__ = ["AgentService"]


class AgentService:
    def __init__(
        self,
        agent_repository: AgentRepository,
        token_encryption: TokenEncryption,
        logger: Logger,
        default_provider: str = "",
        default_model: str = "",
        default_token: str = ""
    ):
        self._agent_repository = agent_repository
        self._token_encryption = token_encryption
        self._logger = logger
        self._default_provider = default_provider
        self._default_model = default_model
        self._default_token = default_token

    async def create_agent(self, project_id: int, agent: Agent, user_id: int) -> Agent:
        if not agent.name:
            if agent.type is AgentType.MR_DESCRIBER:
                agent.name = "MR Description Writer"
            else:
                agent.name = "MR Code Reviewer"

        if not agent.description:
            if agent.type is AgentType.MR_DESCRIBER:
                agent.description = "Automatically generates and adds descriptions to merge requests"
            else:
                agent.description = "Reviews merge requests and adds comments with suggestions"

        if agent.config.provider is None:
            if not self._default_provider:
                raise ValidationError("provider is required")
            agent.config.provider = AgentProvider(self._default_provider)

        if agent.config.model is None:
            if not self._default_model:
                raise ValidationError("model is required")
            agent.config.model = self._default_model

        if agent.config.token is None:
            if not self._default_token:
                raise ValidationError("token is required")
            agent.config.token = self._default_token

        agent.config.token = self._token_encryption.encrypt(agent.config.token)

        return await self._agent_repository.save(project_id, agent, user_id)

    async def list_agents(self, project_id: int) -> list[Agent]:
        return await self._agent_repository.find_by_project_id(project_id)

    async def get_agent(self, project_id: int, agent_id: UUID) -> Agent:
        agent: Agent | None = await self._agent_repository.find_by_id(project_id, agent_id)

        if agent is None:
            raise EntityNotFoundError("Agent not found")

        return agent

    async def update_agent(self, project_id: int, agent_id: UUID, agent: Agent, user_id: int) -> Agent:
        existing_agent: Agent | None = await self._agent_repository.find_by_id(project_id, agent_id)

        if existing_agent is None:
            raise EntityNotFoundError("Agent not found")

        agent.id = existing_agent.id  # Ensure the ID remains the same

        return await self._agent_repository.save(project_id, agent, user_id)
