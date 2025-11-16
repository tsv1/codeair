from codeair.api.routes.agents import agent_router
from codeair.api.routes.auth import auth_router
from codeair.api.routes.healthcheck import healthcheck_router
from codeair.api.routes.projects import project_router
from codeair.api.routes.static import static_router
from codeair.api.routes.webhooks import webhook_router

__all__ = ["agent_router", "auth_router", "healthcheck_router", "project_router", "static_router", "webhook_router"]
