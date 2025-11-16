from litestar.di import Provide

from codeair.di.providers import (provide_agent_repository, provide_agent_service, provide_auth_service,
                                  provide_current_user, provide_db_client, provide_gitlab_client, provide_http_client,
                                  provide_project_repository, provide_project_service, provide_token_encryption,
                                  provide_user_repository, provide_user_service, provide_webhook_service)

api_dependencies = {
    # Clients
    "db_client": Provide(provide_db_client),
    "http_client": Provide(provide_http_client, sync_to_thread=False),
    "gitlab_client": Provide(provide_gitlab_client, sync_to_thread=False),
    # Services
    "token_encryption": Provide(provide_token_encryption, sync_to_thread=False),
    # Repositories
    "agent_repository": Provide(provide_agent_repository, sync_to_thread=False),
    "project_repository": Provide(provide_project_repository, sync_to_thread=False),
    "user_repository": Provide(provide_user_repository, sync_to_thread=False),
    # Services
    "agent_service": Provide(provide_agent_service, sync_to_thread=False),
    "auth_service": Provide(provide_auth_service, sync_to_thread=False),
    "project_service": Provide(provide_project_service, sync_to_thread=False),
    "user_service": Provide(provide_user_service, sync_to_thread=False),
    "webhook_service": Provide(provide_webhook_service, sync_to_thread=False),
    # Request-scoped
    "current_user": Provide(provide_current_user),
}


async def create_agent_worker():
    from codeair.workers.agent_worker import AgentWorker

    worker = AgentWorker()

    return worker
