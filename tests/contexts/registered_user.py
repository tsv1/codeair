from dataclasses import dataclass
from typing import Optional

from helpers import generate_monotonic_id, generate_password
from interfaces.gitlab_api import GitLabAPI
from vedro import context

__all__ = ["registered_user", "GitLabUser"]


@dataclass
class GitLabUser:
    username: str
    name: str
    password: str
    user_id: int
    avatar_url: Optional[str] = None


async def _register_user(username: str, name: str, email: str, password: str) -> int:
    response = await GitLabAPI().create_user(
        username=username,
        name=name,
        email=email,
        password=password,
        skip_confirmation=True
    )
    response.raise_for_status()

    body = response.json()
    return body["id"]


@context
async def registered_user() -> GitLabUser:
    name = username = f"user_{generate_monotonic_id()}"
    email = f"{username}@example.com"
    password = generate_password(12)

    user_id = await _register_user(username, name, email, password)

    return GitLabUser(
        username=username,
        name=name,
        password=password,
        user_id=user_id,
        avatar_url=None,
    )
