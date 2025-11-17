import asyncio
import logging

from codeair.di import create_agent_worker


async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("CodeAir worker is starting up...")

    worker = await create_agent_worker()
    print("Agent worker created successfully")

    try:
        await worker.run()
    finally:
        await worker.cleanup()
        print("Worker stopped and cleaned up")


if __name__ == "__main__":
    asyncio.run(main())
