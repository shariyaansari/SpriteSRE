from backend.diagnosis.signals import extract_signals


def test_command_not_found_signal():
    failure_reason = """
    Job 'build' failed at step 'Try to run a fake command':
    ##[error]Process completed with exit code 127.
    """

    signals = extract_signals(failure_reason)

    assert len(signals) == 1
    assert signals[0].name == "COMMAND_NOT_FOUND"
    assert signals[0].evidence == "exit code 127"


def test_unknown_failure_returns_no_signals():
    failure_reason = """
    Something completely unexpected happened.
    """

    signals = extract_signals(failure_reason)

    assert signals == []