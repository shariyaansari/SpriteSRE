from backend.schemas.diagnosis import Diagnosis
from backend.schemas.signal import Signal


# Deterministic diagnosis lookup table.
# Each signal type maps to a single, high-confidence diagnosis.
DIAGNOSIS_TABLE: dict[str, Diagnosis] = {
    "COMMAND_NOT_FOUND": Diagnosis(
        category="COMMAND_NOT_FOUND",
        root_cause="Required command is not available in the runner environment.",
        explanation="The workflow exited with code 127 (exit code for 'command not found'). The shell could not resolve the command being invoked.",
        suggested_fix="Install the missing command or ensure it is available on PATH in the workflow environment.",
        confidence=0.98,
    ),
    "MISSING_DEPENDENCY": Diagnosis(
        category="MISSING_DEPENDENCY",
        root_cause="A required Python package is not installed.",
        explanation="A ModuleNotFoundError was raised — an import failed because the package is not present in the environment.",
        suggested_fix="Add the missing package to requirements.txt or pyproject.toml, then reinstall dependencies.",
        confidence=0.95,
    ),
    "SYNTAX_ERROR": Diagnosis(
        category="SYNTAX_ERROR",
        root_cause="The source file contains invalid Python syntax.",
        explanation="The Python interpreter raised a SyntaxError while parsing the file. Execution never started.",
        suggested_fix="Fix the invalid syntax at the reported line number.",
        confidence=0.97,
    ),
    "PERMISSION_ERROR": Diagnosis(
        category="PERMISSION_ERROR",
        root_cause="The process lacks permission to access a file or resource.",
        explanation="A 'Permission denied' error was reported, indicating a filesystem or execution permission issue.",
        suggested_fix="Check file permissions or run the workflow with the correct user/permissions.",
        confidence=0.9,
    ),
    "GENERIC_COMMAND_FAILURE": Diagnosis(
        category="GENERIC_COMMAND_FAILURE",
        root_cause="A command in the workflow exited with a non-zero status.",
        explanation="The workflow exited with code 1 — a generic failure that doesn't match any known pattern.",
        suggested_fix="Inspect the full job logs around the failing step for the underlying error.",
        confidence=0.5,
    ),
}


class RuleDiagnoser:
    """
    Signal -> Diagnosis via static lookup.

    Only returns a deterministic diagnosis when the
    confidence is greater than 0.5.

    Otherwise, the caller should escalate to the LLM.
    """

    def diagnose(self, signal: Signal) -> Diagnosis | None:
        diagnosis = DIAGNOSIS_TABLE.get(signal.type)

        if diagnosis is None:
            return None

        if diagnosis.confidence <= 0.5:
            return None

        return diagnosis