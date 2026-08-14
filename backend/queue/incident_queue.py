# TODO: Own the asyncio.Queue

#?  producer -> put incidents in queue
#?  consumer -> get incidents from queue and process them


# Asynchronous I/o -> a library to write concurrent code using the async/await syntax.
# asyncio.Queue is not thread-safe but is coroutine-safe, which is exactly what you want since both your webhook handler and worker will run inside the same asyncio event loop under FastAPI (Uvicorn).

import asyncio

from backend.schemas.incident import Incident

# to get one shared instance of the queue across the application, we can use a module level singleton pattern  -> create the queue once only at the import time and every other file gets that from importing rather than construction it's own asyncio.Queue instance.
# ! Python caches modules after first import, so this instance is genuinely shared everywhere.


incident_queue: asyncio.Queue[Incident] = asyncio.Queue(maxsize=0)

async def enqueue_incident(incident: Incident) -> None:
    await incident_queue.put(incident)


async def dequeue_incident() -> Incident:
    return await incident_queue.get()