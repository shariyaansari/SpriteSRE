from backend.diagnosis.rules import SIGNAL_RULES
from backend.schemas.signal import FailureSignal


def extract_signals(failure_reason: str) -> list[FailureSignal]:
    """
    Run all registered signal rules against the failure evidence.

    Returns:
        A list of signals detected in the failure.
    """

    if not failure_reason:
        return []

    signals: list[FailureSignal] = []

    for rule in SIGNAL_RULES:
        signal = rule(failure_reason)

        if signal is not None:
            signals.append(signal)

    return signals