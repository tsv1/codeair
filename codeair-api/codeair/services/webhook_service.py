from logging import Logger
from typing import Any
from uuid import UUID

from codeair.clients.gitlab import GitLabClient, WebhookData
from codeair.domain.projects.repository import ProjectRepository

__all__ = ["WebhookService"]


class WebhookService:
    def __init__(
        self,
        gitlab_client: GitLabClient,
        project_repository: ProjectRepository,
        webhook_base_url: str,
        bot_token: str,
        logger: Logger,
    ) -> None:
        self._gitlab_client = gitlab_client
        self._project_repository = project_repository
        self._webhook_base_url = webhook_base_url
        self._bot_token = bot_token
        self._logger = logger

    async def create_or_update_webhook(self, project_id: int, webhook_id: UUID) -> None:
        webhook_url = f"{self._webhook_base_url}/api/v1/webhooks/{webhook_id}"
        config = self._get_webhook_config()

        existing_webhook = await self._find_existing_webhook(project_id, webhook_url)

        if not existing_webhook:
            await self._gitlab_client.create_project_webhook(
                project_id=project_id,
                webhook_url=webhook_url,
                access_token=self._bot_token,
                **config
            )
        elif self._webhook_needs_update(existing_webhook):
            await self._gitlab_client.update_project_webhook(
                project_id=project_id,
                webhook_id=existing_webhook["id"],
                webhook_url=webhook_url,
                access_token=self._bot_token,
                **config
            )

    def _get_webhook_config(self) -> dict[str, Any]:
        return {
            "name": "CodeAir Webhook",
            "description": "Webhook for CodeAir merge request events",
            "merge_requests_events": True,
            "enable_ssl_verification": False,
        }

    async def _find_existing_webhook(self, project_id: int, webhook_url: str) -> WebhookData | None:
        webhooks = await self._gitlab_client.get_project_webhooks(project_id, self._bot_token)

        normalized_url = webhook_url.rstrip("/")
        for webhook in webhooks:
            if webhook["url"].rstrip("/") == normalized_url:
                return webhook
        return None

    def _webhook_needs_update(self, webhook: WebhookData) -> bool:
        config = self._get_webhook_config()
        for field, expected_value in config.items():
            if webhook.get(field) != expected_value:
                return True
        return False

    async def get_webhook_id_by_project_id(self, project_id: int) -> UUID | None:
        return await self._project_repository.get_webhook_id_project_id(project_id)
