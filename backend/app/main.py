# FastAPI is async, so an async HTTP client fits naturally.
# requests works with FastAPI.
# But inside an async def, it blocks the event loop while waiting for the network.
import asyncio
import httpx

from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.config import Settings
from backend.routes.github import router as github_router
from backend.webhooks.router import router as webhook_router
from backend.workers.incident_worker import run_incident_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: launch the worker as a background task.
    worker_task = asyncio.create_task(run_incident_worker())
    app.state.worker_task = worker_task

    yield

    # Shutdown: cancel the worker and wait for it to stop.
    worker_task.cancel()

    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

# Load settings once when the application starts.
settings = Settings()

# Register routers.
app.include_router(github_router)
app.include_router(webhook_router)


@app.get("/")
def get_root():
    return {
        "message": f"Welcome to {settings.app_name}!",
        "status": "running",
    }


@app.get("/get_github_data")
async def get_github_response():
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.github_api_url)

        if response.status_code != 200:
            return {
                "error": (
                    "Failed to fetch data from github_api_url, "
                    f"returned with status code {response.status_code}"
                )
            }

        return response.json()