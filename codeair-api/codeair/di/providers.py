import logging
from datetime import timedelta
from typing import Any, AsyncGenerator, Optional

import httpx
from codeair.clients import DatabaseClient, GitLabClient
from codeair.config import Config
from codeair.domain.agents import AgentRepository
from codeair.domain.job_logs import JobLogRepository
from codeair.domain.jobs.repository import JobRepository
from codeair.domain.projects import ProjectRepository
from codeair.domain.users import User, UserRepository
from codeair.services import AgentService, AuthService, UserService, WebhookService
from codeair.services.job_queue_service import JobQueueService
from codeair.services.project_service import ProjectService
from codeair.services.token_encryption import TokenEncryption
from litestar import Request
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import JWTAuth, Token


async def retrieve_user_handler(
    token: Token,
    connection: ASGIConnection[Any, Any, Any, Any],
) -> Optional[User]:
    username = token.extras.get("username")
    name = token.extras.get("name")

    base_url = Config.GitLab.API_BASE_URL.rstrip("/")
    web_url = token.extras.get("web_url", f"{base_url}/{username}")  # backward compatibility

    if not token.sub or not username or not name:
        return None

    return User(
        id=int(token.sub),
        username=str(username),
        name=str(name),
        web_url=web_url,
        avatar_url=token.extras.get("avatar_url"),
    )


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=Config.JWT.SECRET_KEY,
    default_token_expiration=timedelta(seconds=Config.JWT.TOKEN_EXPIRE_SECONDS),
    exclude=[
        "/api/v1/health",
        "/api/v1/health/detailed",
        "/api/v1/auth/gitlab/authorize",
        "/api/v1/auth/gitlab/callback",
        "/api/v1/auth/gitlab/token",
        "/api/v1/webhooks",
        "/assets",
        "/schema",
    ],
    algorithm=Config.JWT.ALGORITHM,
    auth_header="Authorization",
    accepted_issuers=[Config.JWT.ISSUER],
    accepted_audiences=[Config.JWT.AUDIENCE],
)


class DatabaseClientManager:
    _instance: Optional[DatabaseClient] = None

    @classmethod
    async def get_client(cls) -> DatabaseClient:
        if cls._instance is None:
            cls._instance = DatabaseClient(Config.Database.URL)
            await cls._instance.connect()
        return cls._instance

    @classmethod
    async def shutdown(cls) -> None:
        if cls._instance:
            await cls._instance.disconnect()
            cls._instance = None


class HTTPClientManager:
    _instance: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls._instance is None:
            cls._instance = httpx.AsyncClient()
        return cls._instance

    @classmethod
    async def shutdown(cls) -> None:
        if cls._instance:
            await cls._instance.aclose()
            cls._instance = None


async def provide_db_client() -> AsyncGenerator[DatabaseClient, None]:
    client = await DatabaseClientManager.get_client()
    yield client


def provide_http_client() -> httpx.AsyncClient:
    return HTTPClientManager.get_client()


def provide_gitlab_client(http_client: httpx.AsyncClient) -> GitLabClient:
    return GitLabClient(
        api_base_url=Config.GitLab.API_BASE_URL,
        http_client=http_client,
        logger=logging.getLogger("app.clients.gitlab"),
    )


def provide_token_encryption() -> TokenEncryption:
    return TokenEncryption(Config.App.ENCRYPTION_KEY)


def provide_agent_repository(db_client: DatabaseClient) -> AgentRepository:
    return AgentRepository(
        db_client,
        logger=logging.getLogger("app.repositories.agent"),
    )


def provide_project_repository(gitlab_client: GitLabClient, db_client: DatabaseClient) -> ProjectRepository:
    return ProjectRepository(
        gitlab_client,
        db_client,
        logger=logging.getLogger("app.repositories.project"),
    )


def provide_user_repository(db_client: DatabaseClient) -> UserRepository:
    return UserRepository(
        db_client,
        logger=logging.getLogger("app.repositories.user"),
    )


def provide_agent_service(
        agent_repository: AgentRepository,
        token_encryption: TokenEncryption
) -> AgentService:
    return AgentService(
        agent_repository=agent_repository,
        token_encryption=token_encryption,
        logger=logging.getLogger("app.services.agent"),
        default_provider=Config.AI.DEFAULT_PROVIDER,
        default_model=Config.AI.DEFAULT_MODEL,
        default_token=Config.AI.DEFAULT_TOKEN,
    )


def provide_auth_service(
    gitlab_client: GitLabClient,
    user_service: UserService,
) -> AuthService:
    return AuthService(
        jwt_auth=jwt_auth,
        jwt_issuer=Config.JWT.ISSUER,
        jwt_audience=Config.JWT.AUDIENCE,
        gitlab_client=gitlab_client,
        gitlab_base_url=Config.GitLab.API_BASE_URL,
        oauth_client_id=Config.GitLab.OAUTH_CLIENT_ID,
        oauth_client_secret=Config.GitLab.OAUTH_CLIENT_SECRET,
        oauth_redirect_uri=Config.GitLab.OAUTH_REDIRECT_URI,
        oauth_authorize_url=Config.GitLab.OAUTH_AUTHORIZE_URL,
        user_service=user_service,
        logger=logging.getLogger("app.services.auth"),
    )


def provide_user_service(
    gitlab_client: GitLabClient,
    user_repository: UserRepository,
) -> UserService:
    return UserService(
        user_repository=user_repository,
        gitlab_client=gitlab_client,
        bot_token=Config.GitLab.BOT_TOKEN,
        logger=logging.getLogger("app.services.user"),
    )


def provide_project_service(project_repository: ProjectRepository) -> ProjectService:
    return ProjectService(
        project_repository=project_repository,
        bot_token=Config.GitLab.BOT_TOKEN,
        logger=logging.getLogger("app.services.project"),
    )


def provide_webhook_service(
    gitlab_client: GitLabClient,
    project_repository: ProjectRepository,
) -> WebhookService:
    return WebhookService(
        gitlab_client=gitlab_client,
        project_repository=project_repository,
        webhook_base_url=Config.App.WEBHOOK_BASE_URL,
        bot_token=Config.GitLab.BOT_TOKEN,
        logger=logging.getLogger("app.services.webhook"),
    )


def provide_job_repository(db_client: DatabaseClient) -> JobRepository:
    return JobRepository(
        db_client,
        logger=logging.getLogger("app.repositories.job"),
    )


def provide_job_log_repository(db_client: DatabaseClient) -> JobLogRepository:
    return JobLogRepository(
        db_client,
        logger=logging.getLogger("app.repositories.job_log"),
    )


def provide_job_queue_service(
    job_repository: JobRepository,
    agent_repository: AgentRepository,
) -> JobQueueService:
    return JobQueueService(
        job_repository=job_repository,
        agent_repository=agent_repository,
        logger=logging.getLogger("app.services.job_queue"),
    )


async def provide_current_user(request: Request[User, Token, Any]) -> User:
    if not request.user:
        raise NotAuthorizedException("User not authenticated")
    return request.user
