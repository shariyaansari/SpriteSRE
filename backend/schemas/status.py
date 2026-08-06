# DETECTED
#     │
#     ▼
# QUEUED
#     │
#     ▼
# DIAGNOSING
#     │
#     ▼
# PATCH_GENERATED
#     │
#     ▼
# TESTING
#     │
#     ▼
# PR_CREATED
#     │
#     ▼
# RESOLVED

from enum import Enum

class IncidentStatus(str, Enum):
    DETECTED = "DETECTED"
    QUEUED = "QUEUED"
    DIAGNOSING = "DIAGNOSING"
    PATCH_GENERATED = "PATCH_GENERATED"
    TESTING = "TESTING"
    PR_CREATED = "PR_CREATED"
    RESOLVED = "RESOLVED"
    FAILED = "FAILED"