from backend.diagnosis.engine import diagnose_with_rules


failure_reason = """
Job 'build' failed at step 'Try to run a fake command':
2026-08-28T18:44:31.2419050Z ##[error]Process completed with exit code 127.
"""


diagnosis = diagnose_with_rules(failure_reason)

print("\n===== DIAGNOSIS =====")
print(diagnosis)
print("====================")