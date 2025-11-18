from datetime import datetime

from pydantic import BaseModel, Field

__all__ = ["JobLog"]


class JobLog(BaseModel):
    job_id: int
    exit_code: int
    stdout: str | None = Field(default=None)
    stderr: str | None = Field(default=None)
    elapsed_ms: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
