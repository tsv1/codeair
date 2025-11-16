import asyncio

from config import Config as cfg
from contexts.gitlab.created_gitlab_project import GitLabProject
from interfaces.gitlab_api import GitLabAPI
from libs.gitlab import GitLabAccessLevel

__all__ = ("added_project_member",)


async def added_project_member(
    project: GitLabProject,
    user_id: int,
    access_level: GitLabAccessLevel,
    user_token: str,
) -> None:
    response = await GitLabAPI().add_project_member(
        project_id=project.id,
        user_id=user_id,
        access_level=access_level,
        user_token=user_token,
    )
    response.raise_for_status()

    # Verify bot can access the project (retry with exponential backoff)
    # This prevents race conditions where GitLab hasn't fully propagated the membership
    max_attempts = 10
    delay = 0.1  # Start with 100ms

    for attempt in range(max_attempts):
        try:
            # Try to fetch project with bot token to verify access
            verify_response = await GitLabAPI().get_project(project.id, cfg.CODEAIR_BOT_TOKEN)
            if verify_response.status_code == 200:
                # Success - bot can access the project
                return
        except Exception:
            # Ignore exceptions and retry
            pass

        if attempt < max_attempts - 1:
            await asyncio.sleep(delay)
            delay = min(delay * 1.5, 1.0)  # Exponential backoff, max 1 second

    raise TimeoutError(
        f"Bot member access to project {project.id} not available after {max_attempts} attempts"
    )
