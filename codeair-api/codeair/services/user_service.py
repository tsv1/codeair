from logging import Logger

from codeair.clients import GitLabClient
from codeair.domain.users import User, UserLoginRecord, UserRepository

__all__ = ["UserService"]


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        gitlab_client: GitLabClient,
        bot_token: str,
        logger: Logger,
    ) -> None:
        self._user_repository = user_repository
        self._gitlab_client = gitlab_client
        self._bot_token = bot_token
        self._logger = logger

    async def get_user_info(self, user_token: str) -> User:
        user_data = await self._gitlab_client.get_user_by_token(user_token)
        return User(**user_data)

    async def get_bot_user_info(self) -> User:
        return await self.get_user_info(self._bot_token)

    async def save_user_login(self, user_id: int) -> UserLoginRecord:
        return await self._user_repository.save_login(user_id)
