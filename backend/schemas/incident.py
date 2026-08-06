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

from pydantic import BaseModel, Field

class Incident(BaseModel):
    id : UUID = Field(..., description="Unique identifier for the incident")   #Internal SpriteSRE identifier (don't depend on GitHub IDs)
    source: str = Field(..., description="Source of the incident (e.g., 'GitHub', 'GitLab', 'Azure DevOps')")
    repository: str = Field(..., description="GitHub repository associated with the incident")
    workflow_name: str = Field(..., description="Name of the GitHub Actions workflow associated with the incident")
    run_id: int = Field(..., description="GitHub Actions run ID associated with the incident")
    status: enumerate = Field(..., description="Status of the incident (e.g., 'Detected', 'queued', 'diagnosing', 'patch_generated', 'testing', 'pr_created', 'resolved')")
    failure_reason: str = Field(..., description="Reason for the failure of the workflow run") | None  
    created_at: str = Field(..., description="Timestamp when the incident was created")
    

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

