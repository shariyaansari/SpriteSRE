# Imagine two repositories.

# Repo A
# Run ID = 123

# Repo B
# Run ID = 123

# GitHub IDs are unique within GitHub, but SpriteSRE may later support:

# GitHub
# GitLab
# Azure DevOps

# Having your own UUID means every incident is uniquely identifiable regardless of the source.
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional

from backend.schemas.status import IncidentStatus
from backend.schemas.diagnosis import Diagnosis

class Incident(BaseModel):
    id: UUID = Field(..., description="Unique identifier for the incident")
    source: str = Field(..., description="Source of the incident (e.g., 'GitHub', 'GitLab', 'Azure DevOps')")
    repository: str = Field(..., description="Repository associated with the incident")
    workflow_name: str = Field(..., description="Name of the workflow associated with the incident")
    run_id: int = Field(..., description="Run ID associated with the incident")
    status: IncidentStatus = Field(..., description="Status of the incident")
    failure_reason: str | None = Field(default=None, description="Reason for the failure of the workflow run")
    diagnosis: Optional[Diagnosis] = Field(default=None, description="Structured diagnosis of the failure")   
    created_at: str = Field(..., description="Timestamp when the incident was created")
    attempts: int = Field(default=0, description="Number of processing attempts made so far")
    
# Status of the incident can be one of the following:
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