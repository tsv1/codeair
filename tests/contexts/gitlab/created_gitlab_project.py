from dataclasses import dataclass
from typing import Optional

from contexts.logged_in_user import LoggedInUser
from helpers import generate_monotonic_id
from interfaces.gitlab_api import GitLabAPI
from libs.gitlab import ProjectVisibility

__all__ = ["created_gitlab_project", "GitLabProject"]


@dataclass
class GitLabProject:
    id: int
    name: str
    path: str
    web_url: str
    namespace_id: int
    visibility: ProjectVisibility
    description: Optional[str] = None


async def created_gitlab_project(
    user: LoggedInUser,
    name: Optional[str] = None,
    visibility: ProjectVisibility = ProjectVisibility.PRIVATE
) -> GitLabProject:
    if name is None:
        name = f"project_{generate_monotonic_id()}"

    response = await GitLabAPI().create_project(
        name=name,
        user_token=user.token,
        visibility=visibility
    )

    response.raise_for_status()

    body = response.json()
    return GitLabProject(
        id=body["id"],
        name=body["name"],
        path=body["path"],
        web_url=body["web_url"],
        namespace_id=body["namespace"]["id"],
        visibility=ProjectVisibility(body["visibility"]),
        description=body["description"],
    )
