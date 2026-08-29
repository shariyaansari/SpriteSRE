import json

import httpx

from backend.diagnosis.llm_adapter import LLMAdapter
from backend.schemas.diagnosis import Diagnosis
from backend.schemas.signal import Signal
from backend.config import settings


GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-2.0-flash:generateContent"
)


class GeminiAdapter(LLMAdapter):

    def __init__(self, api_key: str | None = None):

        self.model = "gemini-2.0-flash"