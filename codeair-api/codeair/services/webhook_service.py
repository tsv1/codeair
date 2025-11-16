from logging import Logger
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

    async def ensure_webhook(self, project_id: int, webhook_id: UUID) -> None:
        webhook_url = f"{self._webhook_base_url}/api/v1/webhooks/{str(webhook_id)}"
        expected_config = {
            "merge_requests_events": True,
            "enable_ssl_verification": False,
        }

        webhooks = await self._gitlab_client.get_project_webhooks(project_id, self._bot_token)

        matching_webhook = None
        for webhook in webhooks:
            if webhook["url"].rstrip("/") == webhook_url.rstrip("/"):
                matching_webhook = webhook
                break

        if not matching_webhook:
            await self._gitlab_client.create_project_webhook(
                project_id=project_id,
                webhook_url=webhook_url,
                name="CodeAir Webhook",
                description="Webhook for CodeAir merge request events",
                access_token=self._bot_token,
                merge_requests_events=True,
                enable_ssl_verification=False,
            )
            return

        config_matches = all(
            matching_webhook.get(key) == value
            for key, value in expected_config.items()
        )

        if config_matches:
            return

        await self._gitlab_client.update_project_webhook(
            project_id=project_id,
            webhook_id=matching_webhook["id"],
            webhook_url=webhook_url,
            name="CodeAir Webhook",
            description="Webhook for CodeAir merge request events",
            access_token=self._bot_token,
            merge_requests_events=True,
            enable_ssl_verification=False,
        )
