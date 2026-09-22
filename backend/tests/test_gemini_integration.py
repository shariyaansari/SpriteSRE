import pytest

from backend.diagnosis.gemini_adapter import GeminiAdapter
from backend.schemas.signal import Signal
from backend.schemas.file import File

def test_prompt_contains_failure_reason():
    adapter = GeminiAdapter(api_key="fake")
    prompt = adapter._build_prompt("MY_FAKE_FAILURE", None, None)
    assert "MY_FAKE_FAILURE" in prompt
    assert "FAILURE LOGS:" in prompt

def test_prompt_contains_signals():
    adapter = GeminiAdapter(api_key="fake")
    signals = [Signal(type="MISSING_DEPENDENCY", evidence="pytest not found")]
    prompt = adapter._build_prompt("FAIL", signals, None)
    assert "DETECTED SIGNALS:" in prompt
    assert "- MISSING_DEPENDENCY: pytest not found" in prompt

def test_prompt_contains_files():
    adapter = GeminiAdapter(api_key="fake")
    files = [
        File(
            name="requirements.txt",
            path="requirements.txt",
            sha="dummy", url="dummy", html_url="dummy", git_url="dummy", type="file",
            content="pytest\nrequests", 
            size=15, 
            encoding="utf-8"
        )
    ]
    prompt = adapter._build_prompt("FAIL", None, files)
    assert "REPOSITORY CONTEXT:" in prompt
    assert "--- requirements.txt ---" in prompt
    assert "pytest\nrequests" in prompt

def test_prompt_contains_all_sections():
    adapter = GeminiAdapter(api_key="fake")
    signals = [Signal(type="MISSING_DEPENDENCY", evidence="evidence here")]
    files = [
        File(
            name="requirements.txt",
            path="requirements.txt",
            sha="dummy", url="dummy", html_url="dummy", git_url="dummy", type="file",
            content="pytest", 
            size=6, 
            encoding="utf-8"
        )
    ]
    prompt = adapter._build_prompt("SOME_FAIL", signals, files)
    
    assert "FAILURE LOGS:" in prompt
    assert "SOME_FAIL" in prompt
    assert "DETECTED SIGNALS:" in prompt
    assert "- MISSING_DEPENDENCY: evidence here" in prompt
    assert "REPOSITORY CONTEXT:" in prompt
    assert "--- requirements.txt ---" in prompt
    assert "pytest" in prompt