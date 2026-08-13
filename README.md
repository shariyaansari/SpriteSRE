# SpriteSRE

**An autonomous SRE dashboard that catches CI/CD failures, diagnoses them with AI, and applies real fixes — before you even open your laptop.**

SpriteSRE watches your GitHub Actions pipelines, and when something breaks, it doesn't just alert you — it investigates. Named for the "sprite" as a small, autonomous folklore entity that quietly does its work in the background, SpriteSRE aims to be that entity for your CI/CD pipeline.

---

## What it does

1. **Detects** — Listens for CI/CD failures via GitHub webhooks in real time.
2. **Diagnoses** — Sends failure logs to an LLM (Gemini 2.0 Flash, with GPT-4o and Claude as fallbacks) to identify the root cause.
3. **Fixes** — Applies real filesystem patches via PowerShell, based on the AI's diagnosis.
4. **Tests** — Validates the patch in an isolated Docker sandbox before it ever touches your main branch.
5. **Ships** — Raises a pull request automatically via the GitHub REST API, so a human reviews the fix instead of just discovering it.
6. **Remembers** — Uses a RAG pipeline with vector embeddings to recall how similar failures were fixed before, so diagnosis gets faster and more accurate over time.

A Chrome Extension injects a sidebar and "Fix" button directly into the GitHub Actions UI, so the whole workflow is accessible from where you already are.

---

## Architecture

```
GitHub Webhook (CI/CD failure)
        │
        ▼
┌───────────────────┐
│   Ingestion Layer   │  → Captures failure event + logs
└─────────┬──────────┘
          ▼
┌───────────────────┐
│     AI Brain        │  
│  (multi-LLM fallback)│     
│                      │     
└─────────┬──────────┘
          ▼
┌───────────────────┐
│   Fix Memory (RAG)   │  → Vector embeddings of past fixes
└─────────┬──────────┘
          ▼
┌───────────────────┐
│   Action Engine      │  → PowerShell filesystem patches
└─────────┬──────────┘
          ▼
┌───────────────────┐
│  Docker Sandbox Test  │  → Validates patch in isolation
└─────────┬──────────┘
          ▼
┌───────────────────┐
│  Auto PR Raiser       │  → GitHub REST API
└───────────────────┘
```

**Chrome Extension** sits alongside this pipeline, giving a live sidebar view and manual trigger inside the GitHub Actions UI.

---

## Tech Stack

- **Frontend:** React
- **Backend:** Node.js, Express
- **Database:** MongoDB
- **AI/ML:** Gemini 2.0 Flash, GPT-4o, Claude (multi-LLM fallback chain), RAG with vector embeddings
- **Infra:** Docker (sandboxed patch testing), GitHub Webhooks, GitHub REST API
- **Automation:** PowerShell (filesystem patching)
- **Browser Integration:** Chrome Extension (Manifest V3)

---

## Getting Started

### Prerequisites
- Node.js (v18+)
- MongoDB instance (local or Atlas)
- Docker
- A GitHub App/OAuth token with repo + webhook permissions
- API keys for Gemini, OpenAI, and/or Anthropic

### Installation

```bash
git clone https://github.com/shariyaansari/spritesre.git
cd spritesre
npm install
```

### Environment Variables

Create a `.env` file in the root:

```
MONGODB_URI=
GITHUB_WEBHOOK_SECRET=
GITHUB_TOKEN=
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

### Run locally

```bash
npm run dev
```

### Load the Chrome Extension

1. Go to `chrome://extensions`
2. Enable Developer Mode
3. Click "Load unpacked" and select the `/extension` directory

---

## Roadmap

- [ ] Expand input sources beyond GitHub Actions (GitLab CI, Jenkins)
- [ ] Broaden the AI brain layer with local/open-weight model fallback
- [ ] Deeper observability layer — historical failure trends, MTTR tracking
- [ ] Multi-repo fix memory sharing

---

## Why this exists

Most CI/CD failures are repetitive — a flaky test, a missed dependency bump, a config typo — but debugging them still eats developer time one incident at a time. SpriteSRE was built to explore how far an AI system can go in closing that loop autonomously: not just flagging what broke, but understanding it, fixing it, proving the fix works, and handing it to a human for the final call.

---

## License

MIT