import pytest

from backend.schemas.diagnosis import Diagnosis
from backend.schemas.incident import Incident
from backend.schemas.status import IncidentStatus
from backend.schemas.file import File
from backend.workers import incident_worker
from backend.config import Settings

class FakeDiagnosisPipeline:
    def __init__(self):
        self.diagnosed_failure_reason = None
        self.diagnosed_signals = None
        self.diagnosed_files = None

    async def diagnose(self, failure_reason: str, signals=None, files=None):
        self.diagnosed_failure_reason = failure_reason
        self.diagnosed_signals = signals
        self.diagnosed_files = files
        return Diagnosis(
            category="MISSING_DEPENDENCY",
            root_cause="A required package is missing.",
            explanation="The logs contain a ModuleNotFoundError.",
            suggested_fix="Install the missing package.",
            confidence=0.95,
        )

class FakeContextBuilder:
    def __init__(self, *args, **kwargs):
        self.called = False

    async def build_context(self, owner, repo, failure_reason, signals):
        self.called = True
        return [File(
            name="requirements.txt",
            path="requirements.txt",
            sha="dummy", url="dummy", html_url="dummy", git_url="dummy", type="file",
            content="pytest", 
            size=6, 
            encoding="utf-8"
        )]


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

    fake_pipeline = FakeDiagnosisPipeline()
    monkeypatch.setattr(
        incident_worker,
        "diagnosis_pipeline",
        fake_pipeline,
    )
    
    monkeypatch.setattr(
        incident_worker,
        "RepositoryContextBuilder",
        FakeContextBuilder,
    )

    await incident_worker.diagnose_incident(incident)

    assert incident.diagnosis is not None
    assert incident.diagnosis.category == "MISSING_DEPENDENCY"
    assert incident.diagnosis.confidence == 0.95
    
    # Verify the pipeline received the signals and context files!
    assert fake_pipeline.diagnosed_signals is not None
    assert len(fake_pipeline.diagnosed_signals) > 0
    assert fake_pipeline.diagnosed_files is not None
    assert len(fake_pipeline.diagnosed_files) == 1
    assert fake_pipeline.diagnosed_files[0].path == "requirements.txt"
    
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