🚀 Phase 1 — GitHub Foundation

Objective: SpriteSRE can securely communicate with GitHub.
# SpriteSRE Roadmap

This document describes the planned phases and milestones for SpriteSRE.
Each phase has a short objective and concrete milestones. Completed milestones are marked ✅.

## Table of contents
- Phase 1 — GitHub Foundation
- Phase 2 — Incident Detection
- Phase 3 — Persistence Layer
- Phase 4 — Queue Architecture
- Phase 5 — AI Diagnosis Engine
- Phase 6 — RAG Memory
- Phase 7 — Patch Engine
- Phase 8 — Verification Engine
- Phase 9 — GitHub Automation
- Phase 10 — Chrome Extension
- Phase 11 — Dashboard
- Phase 12 — Production Ready

---

## Phase 1 — GitHub Foundation
Objective: Allow SpriteSRE to authenticate with GitHub and read repository data.

Milestones:
- 1.1 Project setup: FastAPI, configuration, environment variables, project layout ✅
- 1.2 GitHub authentication: fine-grained PATs, REST API auth, `/user` test ✅
- 1.3 Repository API: `GitHubClient`, repository schema, metadata fetching, error handling (in progress)
- 1.4 Repository contents: read workflows, package.json, requirements.txt, Dockerfile, README
- 1.5 Actions surface: list workflows, runs, jobs; download logs

phase One completed and now looks like this : 
```
                   GitHubClient
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   get_repository()  get_contents()  get_workflows()
        │                │                │
        └───────┬────────┴────────┬───────┘
                ▼
            _request()
                │
                ▼
        GitHub REST API
                │
                ▼
        JSON Response
                │
     ┌──────────┼──────────┐
     ▼          ▼          ▼
_map_repository() _map_file() _map_workflow()
     │          │          │
     ▼          ▼          ▼
 Repository     File     Workflow 

```

## Phase 2 — Incident Detection
Objective: Detect and surface failing workflows automatically.

Milestones:
- 2.1 Webhooks: endpoint, signature verification, payload parsing
- 2.2 Failure extraction: identify failed workflow and failed jobs; store incident (in-memory initially)
- 2.3 Incident lifecycle: basic state machine (Detected → Queued → Diagnosing → Patch Generated → Testing → PR Created → Resolved)

GitHub
  │
  │ workflow_run webhook
  ▼
router.py
  │
  ├── get raw body
  ├── verify signature
  ├── parse JSON
  └── get X-GitHub-Event
          │
          ▼
      parser.py
          │
          ├── workflow_run?
          ├── completed?
          └── failure?
                 │
                 ▼
             Incident


## Phase 3 — Persistence Layer
Objective: Persist repositories, workflows, runs, jobs, and incidents.

Milestones:
- 3.1 Database: PostgreSQL + SQLAlchemy + Alembic
- 3.2 Models: Repository, Workflow, WorkflowRun, Job, Incident
- 3.3 Relationships and migrations

## Phase 4 — Queue Architecture
Objective: Add reliable background processing.

Milestones:
- 4.1 Redis for broker
- 4.2 Celery workers (or equivalent) for async tasks
- 4.3 Job queue flows: webhook → queue → worker → diagnosis
- 4.4 Robustness: retries, timeouts, dead-letter queue

## Phase 5 — AI Diagnosis Engine
Objective: Generate candidate fixes and root-cause analysis for failures.

Milestones:
- 5.1 Prompt builder and prompt engineering
- 5.2 Repository context builder (read workflow YAML, package.json, Dockerfile, requirements)
- 5.3 Integrate LLM provider (e.g., Gemini or chosen model)
- 5.4 Structured JSON output: root cause, confidence, affected files, suggested fix, explanation
```
Incident
   │
   ▼
Failure evidence
   │
   ▼
Signal extraction
   │
   ├── known signals ──────┐
   │                       │
   └── no/weak signals     │
           │               │
           └──────┬────────┘
                  ▼
             LLM Adapter
                  │
                  ▼
             Diagnosis
                  │
                  ▼
             Validation
                  │
                  ▼
         Structured Diagnosis
```


## Phase 6 — RAG Memory
Objective: Store past failures and fixes to improve diagnostics.

Milestones:
- 6.1 Embeddings pipeline
- 6.2 Store fixes: failure → patch → verification result
- 6.3 Semantic retrieval for similar past failures

## Phase 7 — Patch Engine
Objective: Generate and apply repository patches programmatically.

Milestones:
- 7.1 Repository clone and safe workspace handling
- 7.2 Patch generation (diffs) from AI suggestions
- 7.3 Apply patch locally and run quick checks
- 7.4 Produce diffs suitable for commits/PRs

## Phase 8 — Verification Engine
Objective: Verify candidate fixes in an isolated environment.

Milestones:
- 8.1 Docker sandbox / ephemeral runners
- 8.2 Run tests and commands declared by the repo
- 8.3 Collect logs and artifacts
- 8.4 Decide pass/fail and report results

## Phase 9 — GitHub Automation
Objective: Automate branch/PR creation for suggested fixes.

Milestones:
- 9.1 Create branch
- 9.2 Commit changes
- 9.3 Push branch
- 9.4 Open pull request
- 9.5 Comment AI analysis and verification results on the PR

## Phase 10 — Chrome Extension
Objective: Provide a lightweight UI on GitHub for „Fix with SpriteSRE”.

Milestones:
- 10.1 Detect Actions pages and failures
- 10.2 Sidebar / UI to show analysis
- 10.3 One-click failure detection and fix flow
- 10.4 Fix button to start diagnosis
- 10.5 Live status and progress updates

## Phase 11 — Dashboard
Objective: Provide monitoring and historical insights.

Milestones / metrics:
- Repository health overview
- Incident history and MTTR
- Failure categories and PR history
- Patch success rate and model confidence

## Phase 12 — Production Ready
Objective: Harden for production use.

Milestones:
- 12.1 Authentication, authorization, and secrets management
- 12.2 Rate limiting and API quotas
- 12.3 Centralized logging and monitoring
- 12.4 Deployment: Docker Compose / Kubernetes manifests
- 12.5 CI/CD, backups, and recovery
- 12.6 GitHub App distribution and compliance

---

## Final product (overview)

Chrome Extension → GitHub Actions Page → FastAPI backend (webhooks + API) → Queue + Workers → AI Diagnosis → Verification → PR

---