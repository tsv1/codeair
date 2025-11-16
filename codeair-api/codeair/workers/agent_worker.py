import asyncio

from codeair.workers.base_worker import BaseWorker

__all__ = ["AgentWorker"]


class AgentWorker(BaseWorker):
    async def run(self) -> None:
        print("Agent worker processing...")
        await asyncio.sleep(10)

    async def cleanup(self) -> None:
        print("Cleaning up agent worker...")
