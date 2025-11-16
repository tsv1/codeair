from http import HTTPStatus

from interfaces.gitlab_api import GitLabAPI

__all__ = ["get_project_webhooks"]


async def get_project_webhooks(project_id: int, token: str) -> list[dict]:
    response = await GitLabAPI().get_project_webhooks(project_id, token)
    assert response.status_code == HTTPStatus.OK, response.json()
    return response.json()
