from pathlib import Path

from dotenv import load_dotenv
from vedro.config import Section, env

__all__ = ("Config",)


# Load .env file from the same directory as this config file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config(Section):
    APP_URL: str = env("APP_URL")
    APP_API_URL: str = env("APP_API_URL")

    CODEAIR_BOT_TOKEN: str = env("CODEAIR_BOT_TOKEN")

    GITLAB_URL: str = env("GITLAB_API_BASE_URL")
    GITLAB_ADMIN_TOKEN: str = env("GITLAB_ADMIN_TOKEN")

    GITLAB_OAUTH_CLIENT_ID: str = env("GITLAB_OAUTH_CLIENT_ID")
    GITLAB_OAUTH_REDIRECT_URI: str = env("GITLAB_OAUTH_REDIRECT_URI")


Config.prefetch()
