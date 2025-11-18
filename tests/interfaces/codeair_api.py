from config import Config as cfg
from vedro_httpx import AsyncHTTPInterface, Response

__all__ = ("CodeAirAPI",)

class CodeAirAPI(AsyncHTTPInterface):
    def __init__(self, base_url: str = cfg.APP_API_URL) -> None:
        super().__init__(base_url)

    async def healthcheck(self) -> Response:
        return await self._request("GET", "/api/v1/healthcheck")

    async def detailed_healthcheck(self) -> Response:
        return await self._request("GET", "/api/v1/healthcheck/detailed")

    async def authorize(self) -> Response:
        return await self._request("GET", "/api/v1/auth/gitlab/authorize")

    async def callback(self, code: str | None = None) -> Response:
        params = {}
        if code is not None:
            params["code"] = code
        return await self._request("GET", "/api/v1/auth/gitlab/callback", params=params)

    async def exchange_token(self, token: str | None = None) -> Response:
        payload = {}
        if token:
            payload["token"] = token
        return await self._request("POST", "/api/v1/auth/gitlab/token", json=payload)

    async def get_user_info(self, jwt_token: str | None = None) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("GET", "/api/v1/auth/me", headers=headers)

    async def logout(self, jwt_token: str | None = None) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("POST", "/api/v1/auth/logout", headers=headers)

    async def search_projects(self, jwt_token: str | None, query: str = "") -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        params = {"q": query}
        return await self._request("GET", "/api/v1/projects/search", headers=headers, params=params)

    async def get_project(self, jwt_token: str | None, project_id: int) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("GET", f"/api/v1/projects/{project_id}", headers=headers)

    async def list_agents(self, jwt_token: str | None, project_id: int) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("GET", f"/api/v1/projects/{project_id}/agents",
                                    headers=headers)

    async def get_agent_placeholders(self, jwt_token: str | None, project_id: int) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("GET", f"/api/v1/projects/{project_id}/agents/placeholders",
                                    headers=headers)

    async def create_agent(self, jwt_token: str | None, project_id: int, agent_data: dict) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("POST", f"/api/v1/projects/{project_id}/agents",
                                    headers=headers, json=agent_data)

    async def get_agent(self, jwt_token: str | None, project_id: int, agent_id: str) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("GET", f"/api/v1/projects/{project_id}/agents/{agent_id}",
                                    headers=headers)

    async def update_agent(self, jwt_token: str | None, project_id: int, agent_id: str,
                          agent_data: dict) -> Response:
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        return await self._request("PATCH", f"/api/v1/projects/{project_id}/agents/{agent_id}",
                                    headers=headers, json=agent_data)
