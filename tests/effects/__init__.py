from d42 import schema
from helpers import get_project_webhooks
from schemas.webhooks import WebhookSchema
from vedro import effect

__all__ = ["token_is_hashed", "webhook_exists"]


@effect
def token_is_hashed(hashed_token: str, original_token: str) -> bool:
    assert hashed_token != original_token
    assert len(hashed_token) == 64, hashed_token


@effect
async def webhook_exists(project_id: int, user_token: str) -> bool:
    webhooks = await get_project_webhooks(project_id, user_token)
    assert webhooks == schema.list([..., WebhookSchema, ...])
