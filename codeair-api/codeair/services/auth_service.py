from logging import Logger
from urllib.parse import urlencode

from codeair.clients import GitLabClient
from codeair.clients.gitlab import GitLabAuthError
from codeair.domain.errors import AuthenticationError
from codeair.domain.users import User
from codeair.services.user_service import UserService
from litestar.security.jwt import JWTAuth

__all__ = ["AuthService"]


class AuthService:
    def __init__(
        self,
        jwt_auth: JWTAuth,
        jwt_issuer: str,
        jwt_audience: str,
        gitlab_client: GitLabClient,
        gitlab_base_url: str,
        oauth_client_id: str,
        oauth_client_secret: str,
        oauth_redirect_uri: str,
        oauth_authorize_url: str,
        user_service: UserService,
        logger: Logger,
    ) -> None:
        self._jwt_auth = jwt_auth
        self._jwt_issuer = jwt_issuer
        self._jwt_audience = jwt_audience
        self._gitlab_base_url = gitlab_base_url
        self._oauth_client_id = oauth_client_id
        self._oauth_client_secret = oauth_client_secret
        self._oauth_redirect_uri = oauth_redirect_uri
        self._oauth_authorize_url = oauth_authorize_url
        self._gitlab_client = gitlab_client
        self._user_service = user_service
        self._logger = logger

    def get_gitlab_authorization_url(self) -> str:
        params = {
            "client_id": self._oauth_client_id,
            "redirect_uri": self._oauth_redirect_uri,
            "response_type": "code",
            "scope": "read_user",
        }
        if self._oauth_authorize_url:
            return f"{self._oauth_authorize_url}?{urlencode(params)}"
        return f"{self._gitlab_base_url}/oauth/authorize?{urlencode(params)}"

    async def authenticate_with_oauth_code(self, code: str) -> tuple[str, User]:
        try:
            access_token = await self._gitlab_client.exchange_oauth_code(
                code=code,
                client_id=self._oauth_client_id,
                client_secret=self._oauth_client_secret,
                redirect_uri=self._oauth_redirect_uri,
            )
            user = await self._get_user_from_gitlab_token(access_token)
        except GitLabAuthError as e:
            raise AuthenticationError("Invalid or expired authorization code") from e

        await self._user_service.save_user_login(user.id)

        token = self._create_token(user)
        return token, user

    async def authenticate_with_gitlab_token(self, gitlab_token: str) -> tuple[str, User]:
        try:
            user = await self._get_user_from_gitlab_token(gitlab_token)
        except GitLabAuthError as e:
            raise AuthenticationError("Invalid or expired GitLab token") from e

        await self._user_service.save_user_login(user.id)

        token = self._create_token(user)
        return token, user

    async def _get_user_from_gitlab_token(self, access_token: str) -> User:
        user_data = await self._gitlab_client.get_user_by_token(access_token)
        return User(
            id=user_data["id"],
            username=user_data["username"],
            name=user_data["name"],
            web_url=user_data["web_url"],
            avatar_url=user_data.get("avatar_url"),
        )

    def _create_token(self, user: User) -> str:
        return self._jwt_auth.create_token(
            identifier=str(user.id),
            token_issuer=self._jwt_issuer,
            token_audience=self._jwt_audience,
            token_extras={
                "username": user.username,
                "name": user.name,
                "avatar_url": user.avatar_url,
            },
        )
