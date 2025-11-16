from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

__all__ = ["Job"]


class Job(BaseModel):
    id: int | None = Field(default=None)
    agent_id: UUID
    payload: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = Field(default=None)
    ended_at: datetime | None = Field(default=None)
