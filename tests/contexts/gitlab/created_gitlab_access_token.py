from contexts.registered_user import GitLabUser
from interfaces.gitlab_api import GitLabAPI

__all__ = ["created_gitlab_access_token"]


async def created_gitlab_access_token(user: GitLabUser) -> str:
    response = await GitLabAPI().create_personal_access_token(
        user_id=user.user_id,
        name=f"test_token_{user.username}",
        scopes=["api"]
    )

    response.raise_for_status()

    body = response.json()
    return body["token"]
