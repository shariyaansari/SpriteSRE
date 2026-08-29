"""
LLM Adapter Interface

This defines the contract that any LLM provider must implement.
Concrete implementations (Gemini, Claude, Ollama) inherit from this.

The interface is simple: given a failure reason and an optional list of
signals that the rule engine couldn't diagnose, return a Diagnosis.
"""

from abc import ABC, abstractmethod

from backend.schemas.diagnosis import Diagnosis
from backend.schemas.signal import Signal


class LLMAdapter(ABC):
    """
    Abstract base class for LLM-based diagnosis.
    
    An adapter wraps an LLM API (or local model) and structures
    the response as a Diagnosis object.
    
    Subclasses must implement:
    - diagnose(failure_reason, signals)
    
    The adapter is responsible for:
    - Crafting the prompt
    - Making the API call (or invoking local inference)
    - Parsing the response
    - Validating that all Diagnosis fields are present
    - Handling retries or fallbacks if parsing fails
    """

    @abstractmethod
    async def diagnose(
        self,
        failure_reason: str,
        signals: list[Signal] | None = None,
    ) -> Diagnosis:
        """
        Diagnose a CI/CD failure using the LLM.
        
        Args:
            failure_reason: Raw error text from CI/CD logs
            signals: Optional list of signals from the rule engine.
                     If provided, the LLM can use them as hints.
        
        Returns:
            A Diagnosis object with all fields populated and validated.
        
        Raises:
            ValueError: If the LLM response is malformed or unparseable.
            Exception: If the API call fails after retries.
        """
        pass