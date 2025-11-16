from dataclasses import dataclass

from interfaces.codeair_api import CodeAirAPI
from interfaces.gitlab_api import GitLabAPI
from vedro import context

from .registered_user import GitLabUser, registered_user

__all__ = ["logged_in_user", "LoggedInUser"]


@dataclass
class LoggedInUser:
    username: str
    name: str
    password: str
    user_id: int
    token: str
    jwt_token: str
    avatar_url: str | None = None


async def _create_personal_access_token(user: GitLabUser) -> str:
    response = await GitLabAPI().create_personal_access_token(
        user_id=user.user_id,
        name=f"test_token_{user.username}",
        scopes=["api"]
    )
    response.raise_for_status()

    body = response.json()
    return body["token"]


async def _get_jwt_token(gitlab_token: str) -> str:
    response = await CodeAirAPI().exchange_token(token=gitlab_token)

    response.raise_for_status()

    body = response.json()
    return body["token"]


@context
async def logged_in_user(user: GitLabUser | None = None) -> LoggedInUser:
    if user is None:
        user = await registered_user()

    # Get GitLab personal access token
    gitlab_token = await _create_personal_access_token(user)

    # Exchange GitLab token for JWT token from application
    jwt_token = await _get_jwt_token(gitlab_token)

    return LoggedInUser(
        username=user.username,
        name=user.name,
        password=user.password,
        user_id=user.user_id,
        token=gitlab_token,
        jwt_token=jwt_token,
        avatar_url=user.avatar_url,
    )
