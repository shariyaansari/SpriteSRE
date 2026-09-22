# SpriteSRE Project Phase Checklist

Based on `Phases.md` and an inspection of the current `backend` directory, here is the current status of each phase.

## Phase 1 — GitHub Foundation  (Mostly Complete)
Objective: Allow SpriteSRE to authenticate with GitHub and read repository data.
- [x] **1.1 Project setup:** FastAPI, configuration, environment variables, project layout
- [x] **1.2 GitHub authentication:** fine-grained PATs, REST API auth
- [x] **1.3 Repository API:** `GitHubClient`, repository schema, metadata fetching, error handling (`github/client.py`)
- [x] **1.4 Repository contents:** Methods exist for getting file contents (`get_contents` in `github/client.py`)
- [x] **1.5 Actions surface:** Implemented methods to list workflows, runs, jobs, and extract job logs (`github/client.py`)

## Phase 2 — Incident Detection  (Mostly Complete)
Objective: Detect and surface failing workflows automatically.
- [x] **2.1 Webhooks:** Endpoint, signature verification, payload parsing (`webhooks/router.py`, `webhooks/parser.py`, `webhooks/verifier.py`)
- [x] **2.2 Failure extraction:** Extract error lines and identify failed jobs/steps (`github/client.py`, `workers/incident_worker.py`)
- [x] **2.3 Incident lifecycle:** Basic state machine mapping (Detected → Queued → Diagnosing → Failed/Processed) via the `IncidentStatus` model and `incident_worker.py`

## Phase 3 — Persistence Layer 
Objective: Persist repositories, workflows, runs, jobs, and incidents.
- [ ] **3.1 Database:** PostgreSQL + SQLAlchemy + Alembic integration
- [ ] **3.2 Models:** Repository, Workflow, WorkflowRun, Job, Incident models in DB
- [ ] **3.3 Relationships and migrations:** Setup Alembic environment and initial migrations

## Phase 4 — Queue Architecture (Partially Complete)
Objective: Add reliable background processing.
- [ ] **4.1 Redis for broker:** Still using `asyncio.Queue` (in-memory) instead of Redis.
- [ ] **4.2 Celery workers:** Still using asyncio background tasks instead of Celery.
- [x] **4.3 Job queue flows:** Webhook → queue → worker → diagnosis flow is working via `queue/incident_queue.py` and `workers/incident_worker.py`.
- [x] **4.4 Robustness:** Retries and exponential backoff are implemented in `incident_worker.py`.

## Phase 5 — AI Diagnosis Engine  (Complete)
Objective: Generate candidate fixes and root-cause analysis for failures.
- [x] **5.1 Prompt builder & Prompt engineering:** Setup in `diagnosis/gemini_adapter.py`.
- [x] **5.2 Repository context builder:** Reading and injecting `package.json`, `Dockerfile`, etc., into prompts requires more fleshing out.
- [x] **5.3 Integrate LLM provider:** Integrated with `GeminiAdapter` using `google-genai`.
- [x] **5.4 Structured JSON output:** Output formatting and JSON parsing validation in `GeminiAdapter`.

## Phase 6 — RAG Memory  (Not Started)
Objective: Store past failures and fixes to improve diagnostics.
- [ ] **6.1 Embeddings pipeline**
- [ ] **6.2 Store fixes:** failure → patch → verification result
- [ ] **6.3 Semantic retrieval** for similar past failures

## Phase 7 — Patch Engine  (Not Started)
Objective: Generate and apply repository patches programmatically.
- [ ] **7.1 Repository clone:** Safe workspace handling
- [ ] **7.2 Patch generation (diffs):** From AI suggestions
- [ ] **7.3 Apply patch locally:** Run quick checks
- [ ] **7.4 Produce diffs:** Suitable for commits/PRs

## Phase 8 — Verification Engine  (Not Started)
Objective: Verify candidate fixes in an isolated environment.
- [ ] **8.1 Docker sandbox:** Ephemeral runners
- [ ] **8.2 Run tests & commands:** As declared by the repo
- [ ] **8.3 Collect logs and artifacts**
- [ ] **8.4 Decide pass/fail** and report results

## Phase 9 — GitHub Automation  (Not Started)
Objective: Automate branch/PR creation for suggested fixes.
- [ ] **9.1 Create branch**
- [ ] **9.2 Commit changes**
- [ ] **9.3 Push branch**
- [ ] **9.4 Open pull request**
- [ ] **9.5 Comment:** Post AI analysis and verification results on the PR

## Phase 10 — Chrome Extension  (Not Started)
Objective: Provide a lightweight UI on GitHub for "Fix with SpriteSRE".
- [ ] **10.1 Detect Actions pages and failures**
- [ ] **10.2 Sidebar / UI:** To show analysis
- [ ] **10.3 One-click failure detection and fix flow**
- [ ] **10.4 Fix button:** To start diagnosis
- [ ] **10.5 Live status and progress updates**

## Phase 11 — Dashboard  (Not Started)
Objective: Provide monitoring and historical insights.
- [ ] **11.1 Repository health overview**
- [ ] **11.2 Incident history and MTTR**
- [ ] **11.3 Failure categories and PR history**
- [ ] **11.4 Patch success rate and model confidence**

## Phase 12 — Production Ready  (Not Started)
Objective: Harden for production use.
- [ ] **12.1 Authentication & authorization:** Secrets management
- [ ] **12.2 Rate limiting and API quotas**
- [ ] **12.3 Centralized logging and monitoring**
- [ ] **12.4 Deployment:** Docker Compose / Kubernetes manifests
- [ ] **12.5 CI/CD:** Backups, and recovery
- [ ] **12.6 GitHub App distribution and compliance**
