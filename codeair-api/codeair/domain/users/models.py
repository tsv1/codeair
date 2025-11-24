from datetime import datetime
from typing import Optional

from pydantic import BaseModel

__all__ = ["User", "UserLoginRecord"]

class User(BaseModel):
    id: int
    username: str
    name: str
    web_url: str
    avatar_url: Optional[str] = None


class UserLoginRecord(BaseModel):
    user_id: int
    created_at: datetime
    last_login_at: datetime
