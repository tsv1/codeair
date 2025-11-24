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
                agent.name = "📝 MR Description Writer"
            else:
                agent.name = "🔍 MR Code Reviewer"

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
        saved_agent = await self._agent_repository.save(project_id, agent, user_id)
        return self._hash_agent_token(saved_agent)

    async def list_agents(self, project_id: int) -> list[Agent]:
        agents = await self._agent_repository.find_by_project_id(project_id)
        return [self._hash_agent_token(agent) for agent in agents]

    async def get_agent(self, agent_id: UUID) -> Agent:
        agent: Agent | None = await self._agent_repository.find_by_id(agent_id)
        if agent is None:
            raise EntityNotFoundError("Agent not found")
        return self._hash_agent_token(agent)

    async def get_agent_with_raw_token(self, agent_id: UUID) -> Agent:
        agent: Agent | None = await self._agent_repository.find_by_id(agent_id)
        if agent is None:
            raise EntityNotFoundError("Agent not found")

        # Decrypt the token
        agent.config.token = self._token_encryption.decrypt(agent.config.token)
        return agent

    async def update_agent(self, project_id: int, agent_id: UUID, agent: Agent, user_id: int) -> Agent:
        existing_agent: Agent | None = await self._agent_repository.find_by_id(agent_id)

        if existing_agent is None:
            raise EntityNotFoundError("Agent not found")

        agent.id = existing_agent.id  # Ensure the ID remains the same

        if agent.config.token == self._token_encryption.hash_token(existing_agent.config.token):
            agent.config.token = existing_agent.config.token
        else:
            agent.config.token = self._token_encryption.encrypt(agent.config.token)

        saved_agent = await self._agent_repository.save(project_id, agent, user_id)
        return self._hash_agent_token(saved_agent)

    def _hash_agent_token(self, agent: Agent) -> Agent:
        agent.config.token = self._token_encryption.hash_token(agent.config.token)
        return agent
