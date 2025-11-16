from typing import Optional

from pydantic import BaseModel

__all__ = ["Project"]


class Project(BaseModel):
    id: int
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    description: Optional[str] = None
    visibility: str
    web_url: str
    created_at: str
    last_activity_at: str
    avatar_url: Optional[str] = None
