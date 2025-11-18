from logging import Logger
from typing import Any, TypedDict

import httpx
from codeair.clients.git_provider import GitProvider

__all__ = ["GitLabClient", "UserData", "ProjectData", "WebhookData", "GitLabAPIError", "GitLabAuthError",
           "GitlabNotFoundError"]


class UserData(TypedDict):
    id: int
    username: str
    name: str
    avatar_url: str | None


class ProjectData(TypedDict):
    id: int
    name: str
    name_with_namespace: str
    path: str
    path_with_namespace: str
    description: str | None
    visibility: str
    web_url: str
    created_at: str
    last_activity_at: str
    avatar_url: str | None


class WebhookData(TypedDict):
    id: int
    url: str
    name: str
    description: str
    merge_requests_events: bool
    enable_ssl_verification: bool


class GitLabAPIError(Exception):
    pass


class GitLabAuthError(GitLabAPIError):
    pass


class GitlabNotFoundError(GitLabAPIError):
    pass


class GitLabClient(GitProvider):
    def __init__(self, api_base_url: str, http_client: httpx.AsyncClient, logger: Logger) -> None:
        self._api_base_url = api_base_url
        self._client = http_client
        self._logger = logger

    async def exchange_oauth_code(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ) -> str:
        response = await self._client.post(
            f"{self._api_base_url}/oauth/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri,
            },
        )

        if response.status_code in (400, 401):
            self._logger.error(f"OAuth exchange failed: Invalid or expired authorization code")
            raise GitLabAuthError("Invalid or expired authorization code")
        elif response.status_code != 200:
            self._logger.error(f"OAuth token exchange failed with status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"OAuth token exchange failed: {response.status_code}")

        token_data = response.json()
        self._logger.debug("OAuth token exchange successful")
        return token_data["access_token"]

    async def get_user_by_token(self, access_token: str) -> UserData:
        response = await self._client.get(
            f"{self._api_base_url}/api/v4/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 401:
            self._logger.error("Failed to get user: Invalid or expired GitLab token")
            raise GitLabAuthError("Invalid or expired GitLab token")
        elif response.status_code != 200:
            self._logger.error(f"Failed to fetch user data with status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"Failed to fetch user data: {response.status_code}")

        user_data = response.json()
        self._logger.debug(f"Successfully fetched user data for user_id={user_data['id']}")
        return {
            "id": user_data["id"],
            "username": user_data["username"],
            "name": user_data["name"],
            "avatar_url": user_data.get("avatar_url"),
        }

    async def get_project(self, project_id: int, access_token: str) -> ProjectData:
        response = await self._client.get(
            f"{self._api_base_url}/api/v4/projects/{project_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 404:
            self._logger.warning(f"Project not found: project_id={project_id}")
            raise GitlabNotFoundError("Project not found")
        elif response.status_code == 401:
            self._logger.error(f"Failed to get project {project_id}: Invalid or expired GitLab token")
            raise GitLabAuthError("Invalid or expired GitLab token")
        elif response.status_code != 200:
            self._logger.error(f"Failed to fetch project {project_id} with status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"Failed to fetch project: {response.status_code}")

        project_data = response.json()
        self._logger.debug(f"Successfully fetched project: id={project_id}, name={project_data['name']}")
        return {
            "id": project_data["id"],
            "name": project_data["name"],
            "name_with_namespace": project_data["name_with_namespace"],
            "path": project_data["path"],
            "path_with_namespace": project_data["path_with_namespace"],
            "description": project_data.get("description"),
            "visibility": project_data["visibility"],
            "web_url": project_data["web_url"],
            "created_at": project_data["created_at"],
            "last_activity_at": project_data["last_activity_at"],
            "avatar_url": project_data.get("avatar_url"),
        }

    async def search_projects(self, query: str, access_token: str) -> list[ProjectData]:
        response = await self._client.get(
            f"{self._api_base_url}/api/v4/projects",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "search": query.strip(),
                "membership": True,
                "simple": True,
                "per_page": 10,
            },
        )

        if response.status_code == 401:
            self._logger.error(f"Failed to search projects with query '{query}': Invalid or expired GitLab token")
            raise GitLabAuthError("Invalid or expired GitLab token")
        elif response.status_code != 200:
            self._logger.error(f"Failed to search projects with query '{query}', status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"Failed to search projects: {response.status_code}")

        projects_data = response.json()
        self._logger.debug(f"Project search successful: query='{query}', found {len(projects_data)} projects")
        return [
            {
                "id": project["id"],
                "name": project["name"],
                "name_with_namespace": project["name_with_namespace"],
                "path": project["path"],
                "path_with_namespace": project["path_with_namespace"],
                "description": project.get("description"),
                "visibility": project["visibility"],
                "web_url": project["web_url"],
                "created_at": project["created_at"],
                "last_activity_at": project["last_activity_at"],
                "avatar_url": project.get("avatar_url"),
            }
            for project in projects_data
        ]

    async def healthcheck(self) -> bool:
        try:
            response = await self._client.get(f"{self._api_base_url}")
            if response.status_code != 302:
                self._logger.error(f"GitLab healthcheck failed: expected 302, got {response.status_code}")
                raise GitLabAPIError(f"GitLab healthcheck failed: {response.status_code}")
            self._logger.debug("GitLab healthcheck successful")
            return True
        except httpx.RequestError as e:
            self._logger.error(f"GitLab healthcheck failed with network error: {e}")
            raise GitLabAPIError(f"GitLab healthcheck failed: {str(e)}")

    async def get_project_webhooks(self, project_id: int, access_token: str) -> list[WebhookData]:
        """Get all webhooks for a GitLab project."""
        response = await self._client.get(
            f"{self._api_base_url}/api/v4/projects/{project_id}/hooks",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if response.status_code == 401:
            self._logger.error(f"Failed to get webhooks for project {project_id}: Invalid or expired GitLab token")
            raise GitLabAuthError("Invalid or expired GitLab token")
        elif response.status_code == 404:
            self._logger.warning(f"Project not found: project_id={project_id}")
            raise GitlabNotFoundError("Project not found")
        elif response.status_code != 200:
            self._logger.error(f"Failed to fetch webhooks for project {project_id}, status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"Failed to fetch webhooks: {response.status_code}")

        webhooks_data = response.json()
        self._logger.debug(f"Successfully fetched {len(webhooks_data)} webhooks for project {project_id}")
        return [
            {
                "id": webhook["id"],
                "url": webhook["url"],
                "name": webhook.get("name", ""),
                "description": webhook.get("description", ""),
                "merge_requests_events": webhook.get("merge_requests_events", False),
                "enable_ssl_verification": webhook.get("enable_ssl_verification", True),
            }
            for webhook in webhooks_data
        ]

    async def create_project_webhook(
        self,
        project_id: int,
        webhook_url: str,
        name: str,
        description: str,
        access_token: str,
        merge_requests_events: bool = True,
        enable_ssl_verification: bool = False,
    ) -> WebhookData:
        """Create a webhook for a GitLab project."""
        response = await self._client.post(
            f"{self._api_base_url}/api/v4/projects/{project_id}/hooks",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "url": webhook_url,
                "name": name,
                "description": description,
                "merge_requests_events": merge_requests_events,
                "enable_ssl_verification": enable_ssl_verification,
            },
        )

        if response.status_code == 401:
            self._logger.error(f"Failed to create webhook for project {project_id}: Invalid or expired GitLab token")
            raise GitLabAuthError("Invalid or expired GitLab token")
        elif response.status_code == 404:
            self._logger.warning(f"Project not found: project_id={project_id}")
            raise GitlabNotFoundError("Project not found")
        elif response.status_code != 201:
            self._logger.error(f"Failed to create webhook for project {project_id}, status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"Failed to create webhook: {response.status_code}")

        webhook_data = response.json()
        self._logger.debug(f"Successfully created webhook {webhook_data['id']} for project {project_id}")
        return {
            "id": webhook_data["id"],
            "url": webhook_data["url"],
            "name": webhook_data.get("name", ""),
            "description": webhook_data.get("description", ""),
            "merge_requests_events": webhook_data.get("merge_requests_events", False),
            "enable_ssl_verification": webhook_data.get("enable_ssl_verification", True),
        }

    async def update_project_webhook(
        self,
        project_id: int,
        webhook_id: int,
        webhook_url: str,
        name: str,
        description: str,
        access_token: str,
        merge_requests_events: bool = True,
        enable_ssl_verification: bool = False,
    ) -> WebhookData:
        """Update a webhook for a GitLab project."""
        response = await self._client.put(
            f"{self._api_base_url}/api/v4/projects/{project_id}/hooks/{webhook_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "url": webhook_url,
                "name": name,
                "description": description,
                "merge_requests_events": merge_requests_events,
                "enable_ssl_verification": enable_ssl_verification,
            },
        )

        if response.status_code == 401:
            self._logger.error(f"Failed to update webhook {webhook_id} for project {project_id}: Invalid or expired GitLab token")
            raise GitLabAuthError("Invalid or expired GitLab token")
        elif response.status_code == 404:
            self._logger.warning(f"Webhook {webhook_id} not found for project {project_id}")
            raise GitlabNotFoundError("Webhook not found")
        elif response.status_code != 200:
            self._logger.error(f"Failed to update webhook {webhook_id} for project {project_id}, status {response.status_code}: {response.text}")
            raise GitLabAPIError(f"Failed to update webhook: {response.status_code}")

        webhook_data = response.json()
        self._logger.debug(f"Successfully updated webhook {webhook_id} for project {project_id}")
        return {
            "id": webhook_data["id"],
            "url": webhook_data["url"],
            "name": webhook_data.get("name", ""),
            "description": webhook_data.get("description", ""),
            "merge_requests_events": webhook_data.get("merge_requests_events", False),
            "enable_ssl_verification": webhook_data.get("enable_ssl_verification", True),
        }
