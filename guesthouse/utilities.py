import asyncio
from typing import Any


async def gather_with_concurrency(n: int, *tasks: Any) -> Any:
    # https://stackoverflow.com/a/61478547
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task: Any) -> Any:
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in tasks))
