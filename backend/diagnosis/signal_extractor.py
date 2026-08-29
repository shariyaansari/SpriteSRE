"""
failure_reason
      ↓
SignalExtractor.extract()
      ↓
check RULES one by one
      ↓
matching regex?
   ├── yes → create Signal
   └── no  → continue
      ↓
list[Signal]

for eg -> 
failure_reason:
"pytest: command not found
Process completed with exit code 127"

"""
import re
from dataclasses import dataclass
from typing import Callable

from backend.schemas.signal import Signal


def _line_context(match: re.Match, text: str) -> str:
    """
    Extract the full log line containing the match.
    
    Not just the regex token, but the entire line — this is what
    makes the evidence human-readable and debuggable.
    
    Args:
        match: The regex Match object
        text: The full failure_reason string
    
    Returns:
        The trimmed log line containing the match
    """
    start = text.rfind("\n", 0, match.start()) + 1
    end = text.find("\n", match.end())
    if end == -1:
        end = len(text)
    return text[start:end].strip()


@dataclass
class SignalRule:
    """
    A rule that maps a pattern to a signal type and extracts evidence.
    
    pattern: Compiled regex to search in the failure reason
    signal_type: The name of the signal (e.g., "COMMAND_NOT_FOUND")
    extract_evidence: Function that pulls the evidence string from the match
    """

    pattern: re.Pattern
    signal_type: str
    extract_evidence: Callable[[re.Match, str], str]


# Rules are ordered: more specific patterns before generic ones.
# Only the FIRST match per rule is captured (no duplicates).
RULES: list[SignalRule] = [
    SignalRule(
        re.compile(r"exit code 127"),
        "COMMAND_NOT_FOUND",
        _line_context,
    ),
    SignalRule(
        re.compile(r"ModuleNotFoundError"),
        "MISSING_DEPENDENCY",
        _line_context,
    ),
    SignalRule(
        re.compile(r"SyntaxError"),
        "SYNTAX_ERROR",
        _line_context,
    ),
    SignalRule(
        re.compile(r"Permission denied"),
        "PERMISSION_ERROR",
        _line_context,
    ),
    # Generic catch-all: only matches if nothing else did.
    # Use \b to avoid false positives on "exit code 127" or other codes.
    SignalRule(
        re.compile(r"exit code 1\b"),
        "GENERIC_COMMAND_FAILURE",
        _line_context,
    ),
]


class SignalExtractor:
    """
    failure_reason -> list[Signal]
    
    Deterministic, regex-driven. Runs before any LLM call — cheap, fast,
    and what makes the pipeline work with no API cost for known patterns.
    
    Multiple signals are possible (e.g., a log with both a SyntaxError
    and a missing dependency). Caller decides how to handle ties.
    """

    def extract(self, failure_reason: str) -> list[Signal]:
        """
        Extract all matching signals from a failure reason.
        
        Args:
            failure_reason: Raw error text from CI/CD logs
        
        Returns:
            List of Signal objects, ordered by rule definition.
            Empty list if no patterns match.
        """
        signals: list[Signal] = []
        for rule in RULES:
            match = rule.pattern.search(failure_reason)
            if match:
                signals.append(
                    Signal(
                        type=rule.signal_type,
                        evidence=rule.extract_evidence(match, failure_reason),
                    )
                )
        return signals