"""
Gemini 2.0 Flash Adapter

Free tier: 15 calls/min, 1.5M tokens/day. No credit card required.
Suitable for hobby/learning projects and CI/CD diagnosis.

When rate-limited, fall back to local Ollama (see ollama_adapter.py).
"""

import json
import os

import httpx

from backend.diagnosis.llm_adapter import LLMAdapter
from backend.schemas.diagnosis import Diagnosis
from backend.schemas.signal import Signal
from backend.config import settings


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

class GeminiAdapter(LLMAdapter):
    """
    Diagnose CI/CD failures using Google Gemini 2.0 Flash.
    
    Attributes:
        api_key: Google AI Studio API key (from env or passed in)
        model: Model name (fixed to gemini-2.0-flash)
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.gemini_api_key

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not set."
            )

        self.model = "gemini-2.0-flash"
    async def diagnose(
        self,
        failure_reason: str,
        signals: list[Signal] | None = None,
    ) -> Diagnosis:
        """
        Call Gemini API to diagnose a failure.
        
        Args:
            failure_reason: Raw error text from CI/CD logs
            signals: Optional list of Signal objects to hint at the problem
        
        Returns:
            A Diagnosis with all fields validated
        
        Raises:
            ValueError: If the response doesn't contain valid JSON
            httpx.HTTPError: If the API call fails
        """
        prompt = self._build_prompt(failure_reason, signals)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GEMINI_API_URL,
                params={"key": self.api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,  # Lower = more deterministic
                        "topP": 0.9,
                    },
                },
                timeout=30.0,
            )
            response.raise_for_status()
        
        data = response.json()
        
        # Extract text from Gemini's nested response structure
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"Unexpected Gemini response structure: {data}") from e
        
        return self._parse_diagnosis(text)

    def _build_prompt(self, failure_reason: str, signals: list[Signal] | None) -> str:
        """
        Build a structured prompt for Gemini.
        
        Asks for JSON output to make parsing deterministic.
        Hints at signals if provided.
        """
        signal_hint = ""
        if signals:
            signal_types = ", ".join(s.type for s in signals)
            signal_hint = f"\n\nThe rule engine detected possible signal types: {signal_types}. Use these as hints, but feel free to override if the logs suggest otherwise."
        
        return f"""You are a CI/CD failure diagnostic assistant. Analyze the following workflow failure and return a structured diagnosis as JSON.

        FAILURE LOGS:
        {failure_reason}
        {signal_hint}

        Return ONLY a JSON object (no markdown, no preamble) with these exact fields:
        {{
        "category": "The failure category (e.g., COMMAND_NOT_FOUND, MISSING_DEPENDENCY)",
        "root_cause": "One sentence explaining why this failure occurred",
        "explanation": "Detailed explanation referencing specific evidence from the logs",
        "suggested_fix": "Actionable next step to resolve or debug the failure",
        "confidence": 0.85
        }}

        Be concise. Confidence should be 0.0–1.0, reflecting how sure you are."""

    def _parse_diagnosis(self, response_text: str) -> Diagnosis:
        """
        Parse Gemini's response into a Diagnosis.
        
        Extracts JSON, validates all fields, raises ValueError if malformed.
        """
        # Strip markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {response_text}") from e
        
        # Validate required fields
        required_fields = {"category", "root_cause", "explanation", "suggested_fix", "confidence"}
        missing = required_fields - set(data.keys())
        if missing:
            raise ValueError(f"LLM response missing fields: {missing}. Got: {data}")
        
        # Coerce and validate confidence
        try:
            confidence = float(data["confidence"])
            if not (0.0 <= confidence <= 1.0):
                raise ValueError(f"Confidence out of range: {confidence}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid confidence value: {data['confidence']}") from e
        
        suggested_fix = data.get("suggested_fix")

        if suggested_fix is not None:
            suggested_fix = str(suggested_fix)
            
        return Diagnosis(
            category=str(data["category"]),
            root_cause=str(data["root_cause"]),
            explanation=str(data["explanation"]),
            suggested_fix=suggested_fix,
            confidence=confidence,
        )