from config import Config as cfg
from libs.gitlab import GitLabAccessLevel, ProjectVisibility
from vedro_httpx import AsyncHTTPInterface, Response

__all__ = ("GitLabAPI",)


class GitLabAPI(AsyncHTTPInterface):
    def __init__(self, base_url: str = cfg.GITLAB_URL, admin_token: str = cfg.GITLAB_ADMIN_TOKEN) -> None:
        super().__init__(base_url)
        self._admin_token = admin_token

    async def create_user(self, username: str, name: str, email: str, password: str,
                         skip_confirmation: bool = True) -> Response:
        payload = {
            "username": username,
            "name": name,
            "email": email,
            "password": password,
            "skip_confirmation": skip_confirmation,
        }
        headers = {"PRIVATE-TOKEN": self._admin_token}
        return await self._request("POST", "/api/v4/users", json=payload, headers=headers)

    async def create_personal_access_token(self,
                                           user_id: int,
                                           name: str,
                                           scopes: list[str]) -> Response:
        payload = {
            "name": name,
            "scopes": scopes,
        }
        headers = {"PRIVATE-TOKEN": self._admin_token}
        return await self._request("POST", f"/api/v4/users/{user_id}/personal_access_tokens",
                                   json=payload, headers=headers)

    async def create_project(self,
                             name: str,
                             user_token: str,
                             visibility: ProjectVisibility = ProjectVisibility.PRIVATE) -> Response:
        payload = {
            "name": name,
            "visibility": visibility.value,
        }
        headers = {"PRIVATE-TOKEN": user_token}
        return await self._request("POST", "/api/v4/projects", json=payload, headers=headers)

    async def add_project_member(self,
                                 project_id: int,
                                 user_id: int,
                                 access_level: GitLabAccessLevel,
                                 user_token: str) -> Response:
        payload = {
            "user_id": user_id,
            "access_level": access_level.value,
        }
        headers = {"PRIVATE-TOKEN": user_token}
        return await self._request("POST", f"/api/v4/projects/{project_id}/members",
                                  json=payload, headers=headers)

    async def remove_project_member(self,
                                    project_id: int,
                                    user_id: int,
                                    user_token: str) -> Response:
        headers = {"PRIVATE-TOKEN": user_token}
        return await self._request("DELETE", f"/api/v4/projects/{project_id}/members/{user_id}",
                                   headers=headers)

    async def get_project(self, project_id: int, token: str) -> Response:
        headers = {"PRIVATE-TOKEN": token}
        return await self._request("GET", f"/api/v4/projects/{project_id}", headers=headers)

    async def get_current_user(self, token: str) -> Response:
        headers = {"PRIVATE-TOKEN": token}
        return await self._request("GET", "/api/v4/user", headers=headers)

    async def get_project_webhooks(self, project_id: int, token: str) -> Response:
        headers = {"PRIVATE-TOKEN": token}
        return await self._request("GET", f"/api/v4/projects/{project_id}/hooks", headers=headers)
