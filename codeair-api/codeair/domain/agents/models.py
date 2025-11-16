from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl, model_validator

__all__ = ["Agent", "AgentConfig", "AgentType", "AgentEngine", "AgentProvider"]


class AgentType(StrEnum):
    MR_DESCRIBER = "mr-describer"
    MR_REVIEWER = "mr-reviewer"


class AgentEngine(StrEnum):
    PR_AGENT_V0_29 = "pr_agent_v0.29"  # Apache 2.0 license
    EXTERNAL = "external"


class AgentProvider(StrEnum):
    ANTHROPIC = "anthropic"


class AgentConfig(BaseModel):
    provider: AgentProvider = Field(default=AgentProvider.ANTHROPIC)
    model: str = Field(default="", min_length=1)
    token: str = Field(default="", min_length=1)
    prompt: str | None = Field(default=None)
    external_url: HttpUrl | None = Field(default=None)


class Agent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: AgentType = Field(default=AgentType.MR_DESCRIBER)
    engine: AgentEngine = Field(default=AgentEngine.PR_AGENT_V0_29)
    name: str = Field(default="", min_length=1)
    description: str = Field(default="", min_length=1)
    enabled: bool = Field(default=True)
    config: AgentConfig = Field(default_factory=AgentConfig)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_external_url(self):
        if self.engine == AgentEngine.EXTERNAL and not self.config.external_url:
            raise ValueError("external_url required for external engine")
        return self
