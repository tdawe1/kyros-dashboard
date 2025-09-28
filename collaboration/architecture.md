# Architecture Overview

This document provides a high-level overview of the Kyros Dashboard application architecture, including both the traditional content generation system and the advanced multi-agent collaboration framework.

## 1. System Components

The application is composed of multiple interconnected components:

### Core Application
- **Frontend**: A React single-page application (SPA) built with Vite and styled with Tailwind CSS
- **Backend**: A FastAPI server that provides a RESTful API for the frontend
- **Database**: PostgreSQL with Alembic migrations for data persistence

### Multi-Agent Collaboration System
- **Event Store**: Append-only JSON Lines file (`events.jsonl`) for collaboration history
- **State Management**: JSON files for tasks, locks, and agent registry
- **MCP Servers**: Model Context Protocol servers for external integrations
- **CLI Tools**: Command-line interface for agent interaction and event management

## 2. Technology Stack

### Frontend
- React 18, Vite, Tailwind CSS, TanStack Query, Axios, React Router

### Backend
- FastAPI, PostgreSQL, Redis, Celery, Pydantic, JWT

### Collaboration System
- JSON-based state management with optimistic concurrency
- Event-driven architecture with append-only logging
- MCP (Model Context Protocol) for external tool integration
- GitHub Actions for automated workflows

## 3. Multi-Agent Collaboration Architecture

### Agent Roles
The system defines five distinct agent roles that work together:

1. **Planner**: Creates and manages project plans, breaks down tasks
2. **Implementer**: Executes tasks, creates code, and implements features
3. **Critic**: Reviews code, validates quality, and ensures standards
4. **Integrator**: Manages merges, handles conflicts, and maintains codebase integrity
5. **Watchdog**: Monitors system health, detects issues, and enforces policies

### State Management
```
collaboration/
  state/
    tasks.json          # Task lifecycle, dependencies, DoD, priorities
    locks.json          # File/resource leases with TTL + heartbeat
    agents.json         # Known agents, roles, capabilities, status
  events/
    events.jsonl        # Append-only machine log (JSON Lines)
  logs/
    log.md              # Human-readable summary (generated from events)
```

### Event-Driven Workflow
1. **Task Creation**: Planner creates tasks with acceptance criteria
2. **Task Assignment**: Implementer claims tasks using lease-based locks
3. **Implementation**: Code changes are made in feature branches
4. **Review Process**: Critic reviews changes and validates quality
5. **Integration**: Integrator merges approved changes
6. **Monitoring**: Watchdog ensures system health and compliance

## 4. Data Models

### Traditional Content System
- `User`: Represents a user of the application
- `ContentJob`: Represents a content generation job
- `ContentVariant`: Represents a single piece of generated content
- `Preset`: Represents a user-defined preset for content generation
- `ScheduledJob`: Represents a job scheduled for future execution

### Collaboration System
- `Task`: Represents a work item with status, dependencies, and acceptance criteria
- `Lock`: Represents a resource lease with expiration and heartbeat
- `Agent`: Represents a collaboration participant with roles and capabilities
- `Event`: Represents an action in the collaboration timeline

## 5. Data Flow

### Content Generation Flow
1. User interacts with the frontend to create a content generation job
2. Frontend sends a request to the backend API
3. Backend creates a `ContentJob` and uses a Celery worker to generate content variants asynchronously
4. Generated variants are stored in the PostgreSQL database
5. Frontend polls the backend for job status and displays variants when ready
6. User can schedule variants for future posting, creating a `ScheduledJob`
7. Celery beat scheduler periodically checks for due jobs and posts them

### Multi-Agent Collaboration Flow
1. **Plan Import**: GitHub Actions workflow imports plans from Google Drive
2. **Task Generation**: `split_plan.py` script processes plans into individual tasks
3. **Agent Coordination**: Agents use event system to coordinate work
4. **Branch Management**: Each task gets its own feature branch
5. **PR Creation**: Automated PR creation with structured templates
6. **Review Process**: CodeRabbit and human reviewers validate changes
7. **Integration**: Approved changes are merged into develop branch

## 6. External Integrations

### MCP Servers
- **CodeRabbit**: Automated code review and feedback
- **Linear**: Project management and issue tracking
- **Railway**: Deployment and infrastructure management
- **Vercel**: Frontend deployment and hosting

### GitHub Actions
- **Plan Import**: Automated import of plans from Google Drive
- **PR Creation**: Automated PR creation with templates
- **Quality Checks**: Automated testing, linting, and security scanning
- **Deployment**: Automated deployment to staging and production

## 7. Security and Reliability

### Concurrency Control
- **Lease-based locks**: Prevent conflicts with automatic expiration
- **Optimistic concurrency**: ETag/hash-based conflict resolution
- **Atomic operations**: File renames ensure consistency

### Event Sourcing
- **Append-only logs**: Immutable event history
- **Replay capability**: System state can be reconstructed from events
- **Audit trail**: Complete history of all agent actions

### Error Handling
- **Graceful degradation**: System continues operating if components fail
- **Health checks**: Continuous monitoring of system components
- **Recovery mechanisms**: Automatic retry and fallback strategies