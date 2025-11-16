from logging import Logger

from codeair.clients.database import DatabaseClient, Record
from codeair.domain.users.models import UserLoginRecord

__all__ = ["UserRepository"]


class UserRepository:
    def __init__(self, db_client: DatabaseClient, logger: Logger) -> None:
        self._db_client = db_client
        self._logger = logger

    def _row_to_user_login_record(self, row: Record) -> UserLoginRecord:
        return UserLoginRecord(
            user_id=row["id"],
            created_at=row["created_at"],
            last_login_at=row["last_login_at"],
        )

    async def save_login(self, user_id: int) -> UserLoginRecord:
        sql = """
            INSERT INTO users (id, created_at, last_login_at)
            VALUES ($1, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                last_login_at = NOW()
            RETURNING id, created_at, last_login_at
        """

        row = await self._db_client.fetch_one(sql, user_id)
        return self._row_to_user_login_record(row)
