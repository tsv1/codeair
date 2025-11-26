from pathlib import Path

import cabina
from cabina import env
from dotenv import load_dotenv

__all__ = ["Config"]

# Load .env file from the same directory as this config file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class Config(cabina.Config):

    class App(cabina.Section):
        HOST: str = env.str("APP_HOST", default="0.0.0.0")
        PORT: int = env.int("APP_PORT", default=8080)
        DEBUG: bool = env.bool("APP_DEBUG", default=False)
        NAME: str = env.str("APP_SERVICE_NAME", default="codeair")
        VERSION: str = env.str("APP_VERSION", default="0.1.0")
        ENCRYPTION_KEY: str = env.str("APP_ENCRYPTION_KEY")
        WEBHOOK_BASE_URL: str = env.str("APP_WEBHOOK_BASE_URL")

        STATIC_DIR: Path = Path(__file__).parent / "static"

    class Logging(cabina.Section):
        LEVEL: str = env.str("LOG_LEVEL", default="ERROR")

    class GitLab(cabina.Section):
        OAUTH_CLIENT_ID: str = env.str("GITLAB_OAUTH_CLIENT_ID")
        OAUTH_CLIENT_SECRET: str = env.str("GITLAB_OAUTH_CLIENT_SECRET")
        OAUTH_REDIRECT_URI: str = env.str("GITLAB_OAUTH_REDIRECT_URI")
        OAUTH_AUTHORIZE_URL: str = env.str("GITLAB_OAUTH_AUTHORIZE_URL", default="")
        API_BASE_URL: str = env.str("GITLAB_API_BASE_URL")
        BOT_TOKEN: str = env.str("CODEAIR_BOT_TOKEN")

    class JWT(cabina.Section):
        SECRET_KEY: str = env.str("JWT_SECRET_KEY")
        ALGORITHM: str = env.str("JWT_ALGORITHM", default="HS256")
        TOKEN_EXPIRE_SECONDS: int = env.int("JWT_TOKEN_EXPIRE_SECONDS", default=3600*24*90)
        ISSUER: str = env.str("JWT_ISSUER", default="codeair")
        AUDIENCE: str = env.str("JWT_AUDIENCE", default="codeair-api")

    class CORS(cabina.Section):
        ALLOW_ORIGINS: tuple[str] = env.tuple("CORS_ALLOW_ORIGINS", default=())

    class AI(cabina.Section):
        DEFAULT_PROVIDER: str = env.str("AI_DEFAULT_PROVIDER", default="anthropic")
        DEFAULT_MODEL: str = env.str("AI_DEFAULT_MODEL", default="anthropic/claude-3-7-sonnet-20250219")
        DEFAULT_TOKEN: str = env.str("AI_DEFAULT_TOKEN", default="-")
        PROVIDER_BASE_URL: str = env.str("PROVIDER_BASE_URL", default="https://api.anthropic.com")

    class Database(cabina.Section):
        URL: str = env.str("DATABASE_URL")


Config.prefetch()
