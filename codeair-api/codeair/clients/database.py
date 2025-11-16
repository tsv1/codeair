from contextlib import asynccontextmanager
from typing import Optional

from asyncpg import Pool, Record, create_pool

__all__ = ["DatabaseClient", "Record"]


class DatabaseClient:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self._pool: Optional[Pool] = None

    async def connect(self) -> None:
        self._pool = await create_pool(self.connection_url)

    async def disconnect(self) -> None:
        if self._pool:
            await self._pool.close()

    @property
    def pool(self) -> Pool:
        if not self._pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
        return self._pool

    @asynccontextmanager
    async def acquire(self):
        async with self.pool.acquire() as conn:
            yield conn

    async def fetch_many(self, query: str, *args) -> list[Record]:
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetch_one(self, query: str, *args) -> Record | None:
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def execute(self, query: str, *args) -> str:
        async with self.acquire() as conn:
            return await conn.execute(query, *args)

    async def healthcheck(self) -> bool:
        await self.execute("SELECT 1")
        return True
