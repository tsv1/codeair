from http import HTTPStatus

from interfaces.gitlab_api import GitLabAPI

__all__ = ["get_project_webhooks", "delete_project_webhook", "update_project_webhook"]


async def get_project_webhooks(project_id: int, token: str) -> list[dict]:
    response = await GitLabAPI().get_project_webhooks(project_id, token)
    assert response.status_code == HTTPStatus.OK, response.json()
    return response.json()


async def delete_project_webhook(project_id: int, webhook_id: int, token: str) -> None:
    response = await GitLabAPI().delete_project_webhook(project_id, webhook_id, token)
    assert response.status_code == HTTPStatus.NO_CONTENT, response.json()


async def delete_project_webhooks(project_id: int, token: str) -> None:
    webhooks = await get_project_webhooks(project_id, token)
    for webhook in webhooks:
        await delete_project_webhook(project_id, webhook["id"], token)


async def update_project_webhook(project_id: int, webhook_id: int, token: str,
                                 merge_requests_events: bool | None = None) -> None:
    response = await GitLabAPI().update_project_webhook(project_id, webhook_id, token,
                                                         merge_requests_events=merge_requests_events)
    assert response.status_code == HTTPStatus.OK, response.json()
