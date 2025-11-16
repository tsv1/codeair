from config import Config as cfg
from d42 import schema

__all__ = ["WebhookSchema"]

WebhookSchema = schema.dict({
    "id": schema.int.min(1),
    "url": schema.str.contains(f"{cfg.APP_API_URL}/api/v1/webhooks/"),
    "name": schema.str("CodeAir Webhook"),
    "description": schema.str("Webhook for CodeAir merge request events",),
    "merge_requests_events": schema.bool(True),
    "enable_ssl_verification": schema.bool(False),
    ...: ...
})
