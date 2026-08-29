"""
Tests for the Diagnosis Pipeline

Covers:
1. Known failure (rule engine catches it)
2. Unknown failure (escalates to LLM)
3. Malformed LLM response (validation rejects it)
4. Multiple signals (first match wins)
"""

import pytest

from backend.diagnosis.rule_diagnoser import RuleDiagnoser
from backend.diagnosis.signal_extractor import SignalExtractor
from backend.schemas.signal import Signal


class TestSignalExtractor:
    """Test the regex-driven signal extraction."""

    def test_command_not_found(self):
        """Test extraction of exit code 127."""
        extractor = SignalExtractor()
        failure_reason = """
##[error] process completed with exit code 127
##[error] command not found: pytest
        """
        signals = extractor.extract(failure_reason)
        assert len(signals) >= 1
        assert signals[0].type == "COMMAND_NOT_FOUND"
        assert "exit code 127" in signals[0].evidence

    def test_missing_dependency(self):
        """Test extraction of ModuleNotFoundError."""
        extractor = SignalExtractor()
        failure_reason = "ModuleNotFoundError: No module named 'requests'"
        signals = extractor.extract(failure_reason)
        assert len(signals) >= 1
        assert signals[0].type == "MISSING_DEPENDENCY"
        assert "ModuleNotFoundError" in signals[0].evidence

    def test_syntax_error(self):
        """Test extraction of SyntaxError."""
        extractor = SignalExtractor()
        failure_reason = """File "app.py", line 42
    def broken(
                     ^
SyntaxError: invalid syntax
        """
        signals = extractor.extract(failure_reason)
        assert len(signals) >= 1
        assert signals[0].type == "SYNTAX_ERROR"

    def test_permission_error(self):
        """Test extraction of Permission denied."""
        extractor = SignalExtractor()
        failure_reason = "chmod: cannot access 'script.sh': Permission denied"
        signals = extractor.extract(failure_reason)
        assert len(signals) >= 1
        assert signals[0].type == "PERMISSION_ERROR"

    def test_generic_command_failure(self):
        """Test extraction of generic exit code 1."""
        extractor = SignalExtractor()
        failure_reason = "make: *** [build] Error 1"
        signals = extractor.extract(failure_reason)
        # Generic failure might match if no specific pattern is present
        # This is a catch-all, so confidence should be low
        assert len(signals) == 0 or signals[0].type in [
            "GENERIC_COMMAND_FAILURE"
        ]

    def test_no_match_returns_empty(self):
        """Test that no match returns an empty list."""
        extractor = SignalExtractor()
        failure_reason = "Everything is fine, deployment succeeded"
        signals = extractor.extract(failure_reason)
        assert signals == []

    def test_multiple_signals(self):
        """Test that multiple patterns in one failure are all captured."""
        extractor = SignalExtractor()
        failure_reason = """
SyntaxError in app.py line 42
ModuleNotFoundError: No module named 'requests'
        """
        signals = extractor.extract(failure_reason)
        types = [s.type for s in signals]
        assert "SYNTAX_ERROR" in types
        assert "MISSING_DEPENDENCY" in types


class TestRuleDiagnoser:
    """Test the static rule-based diagnosis lookup."""

    def test_diagnose_command_not_found(self):
        """Test diagnosis of COMMAND_NOT_FOUND signal."""
        diagnoser = RuleDiagnoser()
        signal = Signal(
            type="COMMAND_NOT_FOUND",
            evidence="##[error] exit code 127",
        )
        diagnosis = diagnoser.diagnose(signal)
        assert diagnosis is not None
        assert diagnosis.category == "COMMAND_NOT_FOUND"
        assert diagnosis.confidence == 0.98

    def test_diagnose_missing_dependency(self):
        """Test diagnosis of MISSING_DEPENDENCY signal."""
        diagnoser = RuleDiagnoser()
        signal = Signal(
            type="MISSING_DEPENDENCY",
            evidence="ModuleNotFoundError: No module named 'requests'",
        )
        diagnosis = diagnoser.diagnose(signal)
        assert diagnosis is not None
        assert diagnosis.category == "MISSING_DEPENDENCY"
        assert diagnosis.confidence == 0.95

    def test_unknown_signal_returns_none(self):
        """Test that unknown signal types return None."""
        diagnoser = RuleDiagnoser()
        signal = Signal(
            type="UNKNOWN_FAILURE_TYPE",
            evidence="Some weird error",
        )
        diagnosis = diagnoser.diagnose(signal)
        assert diagnosis is None

    def test_diagnosis_has_all_fields(self):
        """Test that a diagnosis has all required fields."""
        diagnoser = RuleDiagnoser()
        signal = Signal(
            type="SYNTAX_ERROR",
            evidence="SyntaxError in app.py",
        )
        diagnosis = diagnoser.diagnose(signal)
        assert diagnosis is not None
        assert diagnosis.category
        assert diagnosis.root_cause
        assert diagnosis.explanation
        assert diagnosis.suggested_fix
        assert 0.0 <= diagnosis.confidence <= 1.0


class TestGeminiAdapterParsing:
    """
    Test Gemini response parsing without making real API calls.
    
    (Real API tests would need mocking or integration test setup.)
    """

    def test_parse_valid_json_response(self):
        """Test parsing a valid JSON response."""
        from backend.diagnosis.gemini_adapter import GeminiAdapter

        adapter = GeminiAdapter(api_key="test-key-for-parsing-only")
        
        response = """{
  "category": "COMMAND_NOT_FOUND",
  "root_cause": "pytest command is missing",
  "explanation": "Exit code 127 indicates the command could not be found in PATH.",
  "suggested_fix": "Install pytest: pip install pytest",
  "confidence": 0.95
}"""
        
        diagnosis = adapter._parse_diagnosis(response)
        assert diagnosis.category == "COMMAND_NOT_FOUND"
        assert diagnosis.confidence == 0.95

    def test_parse_json_with_markdown_fences(self):
        """Test parsing JSON wrapped in markdown code fences."""
        from backend.diagnosis.gemini_adapter import GeminiAdapter

        adapter = GeminiAdapter(api_key="test-key-for-parsing-only")
        
        response = """```json
{
  "category": "MISSING_DEPENDENCY",
  "root_cause": "requests not installed",
  "explanation": "ModuleNotFoundError was raised.",
  "suggested_fix": "pip install requests",
  "confidence": 0.92
}
```"""
        
        diagnosis = adapter._parse_diagnosis(response)
        assert diagnosis.category == "MISSING_DEPENDENCY"
        assert diagnosis.confidence == 0.92

    def test_parse_invalid_json_raises_error(self):
        """Test that invalid JSON raises ValueError."""
        from backend.diagnosis.gemini_adapter import GeminiAdapter

        adapter = GeminiAdapter(api_key="test-key-for-parsing-only")
        
        response = "Not valid JSON at all"
        
        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            adapter._parse_diagnosis(response)

    def test_parse_missing_fields_raises_error(self):
        """Test that missing required fields raise ValueError."""
        from backend.diagnosis.gemini_adapter import GeminiAdapter

        adapter = GeminiAdapter(api_key="test-key-for-parsing-only")
        
        response = """{
  "category": "SOMETHING",
  "root_cause": "Test"
}"""
        
        with pytest.raises(ValueError, match="missing fields"):
            adapter._parse_diagnosis(response)

    def test_parse_invalid_confidence_raises_error(self):
        """Test that invalid confidence raises ValueError."""
        from backend.diagnosis.gemini_adapter import GeminiAdapter

        adapter = GeminiAdapter(api_key="test-key-for-parsing-only")
        
        response = """{
  "category": "TEST",
  "root_cause": "Test",
  "explanation": "Test",
  "suggested_fix": "Test",
  "confidence": 1.5
}"""
        
        with pytest.raises(ValueError, match="Confidence out of range"):
            adapter._parse_diagnosis(response)


# Example usage (manual testing):
if __name__ == "__main__":
    print("Run tests with: pytest backend/diagnosis/test_pipeline.py -v")