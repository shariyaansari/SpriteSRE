from collections.abc import Callable

from backend.schemas.signal import FailureSignal


SignalRule = Callable[[str], FailureSignal | None]


def command_not_found_rule(text: str) -> FailureSignal | None:
    """
    Detect the common Unix command-not-found exit code.
    """

    if "exit code 127" not in text.lower():
        return None

    return FailureSignal(
        name="COMMAND_NOT_FOUND",
        evidence="exit code 127",
        confidence=0.98,
    )


SIGNAL_RULES: list[SignalRule] = [
    command_not_found_rule,
]