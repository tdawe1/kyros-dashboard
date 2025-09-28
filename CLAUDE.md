# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Development Commands

### Quick Start (Both Frontend + Backend)
```bash
./scripts/start-both.sh  # Starts both servers concurrently
```

### Backend (FastAPI + Poetry)
```bash
cd backend
poetry install                                    # Install dependencies
poetry run alembic upgrade head                   # Run database migrations
poetry run uvicorn main:app --reload --port 8000  # Start development server
```

### Frontend (React + Vite)
```bash
cd frontend
npm install        # Install dependencies
npm run dev        # Start development server (port 3001)
npm run build      # Production build
```

## Testing Commands

### Run All Tests
```bash
./scripts/run-tests.sh  # Runs backend, frontend, and E2E tests
```

### Backend Tests
```bash
cd backend
poetry run pytest                  # Run all tests
poetry run pytest -q               # Quiet mode
poetry run pytest -k test_name     # Run specific test
poetry run pytest tests/test_healthz.py  # Run specific test file
```

### Frontend Tests
```bash
cd frontend
npm run test              # Run Vitest in watch mode
npm run test:run          # Run once
npm run test:coverage     # With coverage
npm run test:e2e          # Playwright E2E tests
```

## Linting and Code Quality

### Backend
```bash
cd backend
poetry run ruff check .           # Linting
poetry run black --check .        # Format check
poetry run black .                # Auto-format
poetry run bandit -r .            # Security scan
```

### Frontend
```bash
cd frontend
npm run lint              # ESLint check
npm run lint:fix          # Auto-fix linting issues
npm run format            # Prettier format
npm run format:check      # Format check
npm run type-check        # TypeScript check
```

## Architecture Overview

### Project Structure
- **backend/**: FastAPI application with Poetry dependency management
  - `core/`: Core business logic (auth, database, services)
  - `scheduler/`: Job scheduling and automated tasks
  - `tools/`: Extensible plugin system for content generation
  - `utils/`: Shared utilities (rate limiting, quotas, observability)
  - `tests/`: Pytest test suite with 70% coverage requirement
  
- **frontend/**: React 18 app with Vite bundler on port 3001
  - Pages: Dashboard, Studio, Scheduler, Jobs, Settings
  - TanStack Query for API state management
  - Tailwind CSS for styling
  
- **collaboration/**: Task management and workflow system
  - Tasks organized by ID (T-xxx format)
  - State management in `collaboration/state/`
  - Board tracking in `collaboration/board.md`

### Key Technical Details
- **Authentication**: JWT-based with refresh tokens
- **Database**: PostgreSQL with SQLAlchemy ORM, Alembic migrations
- **Caching**: Redis for rate limiting and session storage
- **Background Jobs**: Celery with Redis broker
- **API Documentation**: Auto-generated at http://localhost:8000/docs
- **Error Tracking**: Sentry integration
- **Testing**: pytest (backend), Vitest + Playwright (frontend)

### Development Workflow
1. Branch naming: `feat/<task-id>-description` or `fix/<issue>-description`
2. Commit style: Conventional commits (feat, fix, docs, test, chore, etc.)
3. PRs must be <300 lines, target 1-3 modules
4. All tests must pass, including linting and type checking
5. Main branch is protected with required status checks

### Environment Configuration
- Backend: Copy `backend/env.example` to `backend/.env`
- Frontend: Uses `VITE_API_BASE_URL=http://localhost:8000`
- Required services: PostgreSQL, Redis
- OpenAI API key needed for content generation

## MCP Servers (Model Context Protocol)

### Installation
```bash
# Install the MCP package in editable mode
python -m pip install -e ./mcp

# Or with system packages override (if needed)
python -m pip install -e ./mcp --break-system-packages
```

### Available Servers
- **kyros-collab-mcp**: Collaboration server (tasks/locks/agents/events/logs)
- **mcp-linear**: Linear integration stub
- **mcp-coderabbit**: CodeRabbit integration stub  
- **mcp-railway**: Railway deployment stub
- **mcp-vercel**: Vercel deployment stub

### Usage
```bash
# Run via console scripts (recommended)
kyros-collab-mcp
mcp-linear
mcp-railway
mcp-vercel
mcp-coderabbit

# Or run via Python module
python -m mcp.kyros_collab_server
python -m mcp.linear_server
python -m mcp.railway_server
python -m mcp.vercel_server
python -m mcp.coderabbit_server
```

### Running MCP Servers
```bash
# Direct module execution
python -m mcp.kyros_collab_server
python -m mcp.linear_server
python -m mcp.coderabbit_server
python -m mcp.railway_server
python -m mcp.vercel_server

# Command-line entry points (after installation)
kyros-collab-mcp
mcp-linear
mcp-coderabbit
mcp-railway
mcp-vercel
```

### Testing MCP Servers
```bash
# Run comprehensive test suite
./scripts/test-mcp-servers.sh

# Quick JSON-RPC test
printf '{"jsonrpc":"2.0","id":1,"method":"initialize"}\n' | python -m mcp.kyros_collab_server
printf '{"jsonrpc":"2.0","id":2,"method":"collab.list_tasks","params":{}}\n' | python -m mcp.kyros_collab_server
```

### MCP Configuration
- Servers auto-load `.env` and `collaboration/.env` files
- Cursor IDE can inject environment from `.cursor/environment.json`
- See `mcp/mcp.config.example.json` for MCP client configuration

### Troubleshooting

#### MCP Server Issues
- **Server won't start**: Check Python path and dependencies with `python -m pip list`
- **JSON-RPC errors**: Ensure proper JSON formatting and method names
- **Permission denied**: Run `chmod +x scripts/test-mcp-servers.sh`
- **Module not found**: Install with `cd mcp && python -m pip install -e .`
- **Environment variables**: Check `.env` files and `COLLAB_ROOT` setting

#### Common MCP Commands
```bash
# Verify installation
python -m pip show kyros-mcp

# Test individual server
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python -m mcp.kyros_collab_server

# Check server capabilities
echo '{"jsonrpc":"2.0","id":1,"method":"linear.capabilities"}' | python -m mcp.linear_server
```

### Important Rules
- Never edit files under `collaboration/state/**` directly
- Follow existing code patterns and conventions
- Use Poetry for Python dependencies (backend)
- Run tests and linting before committing
- Keep PRs small and focused
- Document API changes