# Kyros Dashboard

A comprehensive AI-powered content generation and scheduling platform with a modern React frontend and robust FastAPI backend. The dashboard provides tools for content repurposing, automated scheduling, and extensible tool management.

## 🚀 Features

### Core Functionality
- **Modern Dashboard**: Clean, responsive UI with dark theme and professional design
- **Content Generation**: Transform source content into multiple channel formats (LinkedIn, Twitter, Newsletter, Blog)
- **Variant Management**: Edit, accept, copy, and export generated content variants
- **Job Monitoring**: Track and manage content repurposing jobs with real-time status updates
- **Preset Management**: Create and manage custom content generation presets

### Advanced Features
- **Scheduler System**: Automated job scheduling with recurrence patterns and timezone support
- **Tool Registry**: Extensible plugin system for custom tools and integrations
- **Authentication**: Secure JWT-based authentication with user management
- **Rate Limiting**: Built-in rate limiting and quota management
- **Database Integration**: PostgreSQL with Alembic migrations
- **Real-time Updates**: Live KPI tracking and job status updates
- **Error Handling**: Comprehensive error handling with Sentry integration

## 🛠️ Tech Stack

**Frontend:** React 18, Vite (port 3001), Tailwind CSS, TanStack Query, TypeScript
**Backend:** FastAPI, PostgreSQL, Redis, Celery, JWT Auth (Poetry-managed)
**Testing:** Playwright, Vitest, pytest
**Deployment:** GitHub Actions, Vercel, Railway/Render

## 📁 Project Structure

```
kyros-dashboard/
├── frontend/          # React app (pages, components, hooks)
├── backend/           # FastAPI app (core, scheduler, tools, utils)
├── docs/              # Documentation
└── scripts/           # Development scripts
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- PostgreSQL (for production)
- Redis (for caching and rate limiting)

### Quick Start

The easiest way to get started is using the provided scripts:

```bash
# Start both frontend and backend
./scripts/start-both.sh

# Or start them separately
./scripts/start-frontend.sh  # Terminal 1
./scripts/start-backend.sh   # Terminal 2
```

### Manual Setup

**Frontend (port 3001):**
```bash
cd frontend && npm install && npm run dev
```

**Backend (Poetry):**
```bash
cd backend
poetry install
cp env.example .env  # Edit with your config
poetry run alembic upgrade head
poetry run uvicorn main:app --reload --port 8000
```

### Environment Variables

**Frontend:** `VITE_API_BASE_URL=http://localhost:8000`
**Backend:** See `backend/env.example` for required variables (database, Redis, OpenAI, JWT, etc.)

## 📱 Key Features

- **Dashboard** - KPIs, recent jobs, quick content generation
- **Studio** - Content repurposing with channel-specific formatting
- **Scheduler** - Automated job scheduling with recurrence patterns
- **Jobs** - Job monitoring, history, and management
- **Settings** - Presets, configuration, and tool management



## 🔌 API

RESTful API with endpoints for authentication, content generation, scheduling, and tool management.
See `http://localhost:8000/docs` for interactive API documentation.

## 🧪 Testing

```bash
# Run all tests (backend, frontend, E2E)
./scripts/run-tests.sh

# Backend (Poetry):
cd backend && poetry run pytest -q

# Frontend (Vitest + Playwright on port 3001):
cd frontend && npm run test && npm run test:e2e
```

## 🧠 MCP Servers & Collaboration

This repo ships MCP servers under `mcp/` and a collaboration model under `collaboration/`.

- Install servers locally:
  - `python -m pip install -e mcp`
  - Start (recommended): `python -m mcp.kyros_collab_server` (collaboration), `python -m mcp.linear_server`, `python -m mcp.railway_server`, `python -m mcp.vercel_server`, `python -m mcp.coderabbit_server`
- Import CodeRabbit/GitHub PR feedback to tasks:
  - `python scripts/import_coderabbit_feedback.py --owner ORG --repo REPO --pr 123 --assign`
    - Creates tasks from review changes/PR comments, links PR number, and (optionally) auto‑assigns.
- Link external IDs to tasks via collab RPC:
  - `collab.link_external({"id": "task-001", "provider": "linear", "value": "LIN-123"})`
  - `collab.link_external({"id": "task-001", "provider": "vercel", "key": "deployment", "value": "dpl_..."})`

See `mcp/README.md` and `agents.md` for details.

## 🔗 Branch Model

**Development:** All PRs target `develop` branch  
**Releases:** Periodically merge `develop` → `main` for production deployment  
**Hotfixes:** Direct PRs to `main` for critical production issues only

## 🚀 Deployment

**Automatic:** GitHub Actions deploys on merge to `main`
**Manual:** Frontend (Vercel), Backend (Railway/Render)
**Setup:** See [Deployment Guide](docs/DEPLOYMENT.md)

## 📝 Status

**Production Ready** with authentication, database integration, and comprehensive testing.
**Extensible** plugin-based architecture with CI/CD pipeline.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature` [[memory:7928543]]
3. Commit frequently with clear messages [[memory:7940605]]
4. Open a Pull Request targeting `develop`

**Requirements:** All code must pass tests, linting, and security checks. PRs require code review approval.

## 📄 License

This project is part of the kyros Repurposer suite. All rights reserved.

## 📚 Documentation

- [Quick Start](docs/QUICK_START.md) - Get running in 2 minutes
- [Deployment](docs/DEPLOYMENT.md) - Complete setup guide
- [Testing](docs/TESTING.md) - Testing strategies
- [User Guide](docs/TEST_USER_GUIDE.md) - End-user documentation
- [Architect Prompt](.codex/context/architect.md) - AI agent planning prompt
- [Governance](CONTRIBUTING.md) - Development process and guidelines
