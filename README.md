# SpriteSRE

> AI-powered SRE automation for diagnosing and fixing failed CI/CD workflows.

SpriteSRE is an event-driven SRE automation platform that detects failed GitHub Actions workflows, analyzes their failures, tests potential fixes in an isolated sandbox, and eventually creates a pull request with the validated patch.

The project is being built incrementally, with the backend developed first.

---

## 🚧 Project Status

SpriteSRE is currently under active development.

### Completed

- GitHub REST API integration
- Fine-grained GitHub Personal Access Token authentication
- Repository metadata retrieval
- GitHub webhook endpoint
- Webhook signature verification using HMAC-SHA256
- GitHub `workflow_run` event handling
- Failed workflow detection
- Incident schema and lifecycle states
- GitHub payload → Incident mapping

### In Progress

- Failed job and log extraction
- Incident storage
- Incident lifecycle management
- Queue-based processing
- Automated diagnosis

### Planned

- RAG-based failure/solution memory
- AI-powered patch generation
- Sandbox-based patch testing
- Automated PR creation
- GitHub UI integration through a Chrome Extension

---

# Architecture

```text
                         GitHub
                            │
             ┌──────────────┴──────────────┐
             │                             │
        REST API                       Webhooks
             │                             │
             ▼                             ▼
      GitHubClient                    FastAPI
             │                             │
             │                     Signature Verification
             │                             │
             │                         Payload Parser
             │                             │
             │                             ▼
             │                         Incident
             │                             │
             └──────────────►      Queue / Processing
                                           │
                                           ▼
                                      Diagnosis
                                           │
                                           ▼
                                    Patch Generation
                                           │
                                           ▼
                                       Sandbox
                                           │
                                           ▼
                                      Re-testing
                                           │
                                           ▼
                                    Pull Request