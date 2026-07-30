# FastAPI is async, so an async HTTP client fits naturally.
# requests works with FastAPI.
# But inside an async def, it blocks the event loop while waiting for the network.
import httpx;  
from fastapi import FastAPI
from config import Settings
from functools import lru_cache

app = FastAPI()

@lru_cache()
# settings = Settings()

def get_Settings():
    return settings

@app.get("/")
def get_root():
    try:
        settings = Settings()
        return {"message": f"Welcome to {settings.app_name}!"}
    except Exception as e:
        return {"error": f"Failed to load settings: {str(e)}"}
   
    
@app.get("/get_github_data")
async def get_github_response():
    async with httpx.AsyncClient() as client: 
        settings = Settings()
        response = await client.get(settings.github_api_url)
        if response.status_code != 200:
            return {"error": f"Failed to fetch data from github_api_url, returned with a status code of {response.status_code}"}
        return response.json()
