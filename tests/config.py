from vedro.config import Section, env

__all__ = ("Config",)


class Config(Section):
    APP_URL: str = env("APP_URL")
    APP_API_URL: str = env("APP_API_URL")

    CODEAIR_BOT_TOKEN: str = env("CODEAIR_BOT_TOKEN")

    GITLAB_URL: str = env("GITLAB_API_BASE_URL")
    GITLAB_ADMIN_TOKEN: str = env("GITLAB_ADMIN_TOKEN")

    GITLAB_OAUTH_CLIENT_ID: str = env("GITLAB_OAUTH_CLIENT_ID")
    GITLAB_OAUTH_REDIRECT_URI: str = env("GITLAB_OAUTH_REDIRECT_URI")


Config.prefetch()
