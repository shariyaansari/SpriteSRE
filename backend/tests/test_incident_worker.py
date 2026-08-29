import pytest

from backend.schemas.diagnosis import Diagnosis
from backend.schemas.incident import Incident
from backend.schemas.status import IncidentStatus
from backend.workers import incident_worker
from backend.config import Settings


class FakeDiagnosisPipeline:

    async def diagnose(self, failure_reason: str):
        return Diagnosis(
            category="MISSING_DEPENDENCY",
            root_cause="A required package is missing.",
            explanation="The logs contain a ModuleNotFoundError.",
            suggested_fix="Install the missing package.",
            confidence=0.95,
        )


@pytest.mark.asyncio
async def test_diagnose_incident_stores_diagnosis(monkeypatch):

    incident = Incident(
        id="123e4567-e89b-12d3-a456-426614174000",
        source="GitHub",
        repository="owner/repo",
        workflow_name="CI",
        run_id=123,
        status=IncidentStatus.DIAGNOSING,
        failure_reason="ModuleNotFoundError: No module named 'requests'",
        created_at="2026-08-29T10:00:00Z",
    )

    monkeypatch.setattr(
        incident_worker,
        "diagnosis_pipeline",
        FakeDiagnosisPipeline(),
    )

    await incident_worker.diagnose_incident(incident)

    assert incident.diagnosis is not None
    assert incident.diagnosis.category == "MISSING_DEPENDENCY"
    assert incident.diagnosis.confidence == 0.95
    
@pytest.mark.asyncio
async def test_diagnose_incident_without_failure_reason():

    incident = Incident(
        id="123e4567-e89b-12d3-a456-426614174000",
        source="GitHub",
        repository="owner/repo",
        workflow_name="CI",
        run_id=123,
        status=IncidentStatus.DIAGNOSING,
        failure_reason=None,
        created_at="2026-08-29T10:00:00Z",
    )

    await incident_worker.diagnose_incident(incident)

    assert incident.diagnosis is None