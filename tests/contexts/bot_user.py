from dataclasses import dataclass

from config import Config as cfg
from interfaces.gitlab_api import GitLabAPI
from vedro import context

__all__ = ["bot_user", "BotUser"]


@dataclass
class BotUser:
    id: int
    username: str
    name: str
    web_url: str
    avatar_url: str | None = None


@context
async def bot_user() -> BotUser:
    bot_response = await GitLabAPI().get_current_user(cfg.CODEAIR_BOT_TOKEN)
    bot_response.raise_for_status()

    body = bot_response.json()
    return BotUser(
        id=body["id"],
        username=body["username"],
        name=body["name"],
        web_url=body["web_url"],
        avatar_url=body.get("avatar_url")
    )
