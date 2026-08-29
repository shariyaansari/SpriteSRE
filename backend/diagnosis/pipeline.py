"""
Diagnosis Pipeline Orchestrator

Flow:
1. Extract signals (regex-driven, fast)
2. Try rule-based diagnosis
3. If no strong deterministic diagnosis exists, fall back to LLM
4. Validate and return
"""

import logging

from backend.diagnosis.gemini_adapter import GeminiAdapter
from backend.diagnosis.llm_adapter import LLMAdapter
from backend.diagnosis.rule_diagnoser import RuleDiagnoser
from backend.diagnosis.signal_extractor import SignalExtractor
from backend.schemas.diagnosis import Diagnosis
from backend.config import Settings



logger = logging.getLogger(__name__)


class DiagnosisPipeline:
    """
    Diagnose a CI/CD failure using a rule engine + LLM fallback.
    """

    def __init__(
        self,
        llm_adapter: LLMAdapter | None = None,
    ):
        self.extractor = SignalExtractor()
        self.rule_diagnoser = RuleDiagnoser()
        self.llm_adapter = llm_adapter or GeminiAdapter()

    async def diagnose(self, failure_reason: str) -> Diagnosis:
        """
        Diagnose a CI/CD failure.

        Flow:
        1. Extract all signals.
        2. Try deterministic diagnosis for each signal.
        3. Return the first strong rule-based diagnosis.
        4. If none are strong enough, use the LLM.
        """

        if not failure_reason or not failure_reason.strip():
            raise ValueError(
                "Cannot diagnose an empty failure reason."
            )

        logger.debug(
            "Diagnosing failure:\n%s",
            failure_reason[:200],
        )

        # 1. Extract signals.
        signals = self.extractor.extract(
            failure_reason
        )

        logger.debug(
            "Extracted %d signal(s): %s",
            len(signals),
            [signal.type for signal in signals],
        )

        # 2. Try every detected signal.
        for signal in signals:
            rule_diagnosis = self.rule_diagnoser.diagnose(
                signal
            )

            if rule_diagnosis is not None:
                logger.info(
                    "Rule-based diagnosis matched: %s "
                    "(confidence: %.2f)",
                    rule_diagnosis.category,
                    rule_diagnosis.confidence,
                )

                return rule_diagnosis

        # 3. No strong deterministic diagnosis.
        logger.info(
            "No strong rule-based diagnosis found. "
            "Escalating to LLM."
        )

        # 4. LLM diagnosis.
        try:
            llm_diagnosis = await self.llm_adapter.diagnose(
                failure_reason,
                signals,
            )

            logger.info(
                "LLM diagnosis: %s "
                "(confidence: %.2f)",
                llm_diagnosis.category,
                llm_diagnosis.confidence,
            )

            return llm_diagnosis

        except Exception as exc:
            logger.exception(
                "LLM diagnosis failed"
            )

            raise ValueError(
                "Diagnosis failed: no strong rule-based "
                "diagnosis was found and the LLM failed."
            ) from exc