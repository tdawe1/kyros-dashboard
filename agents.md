# Kyros Dashboard: Coding Agent Instructions

This document provides a comprehensive guide for AI coding agents working on the Kyros Dashboard project. Please read it carefully to understand the project structure, conventions, and your role in development.

## 1. Project Overview

**Purpose:** The Kyros Dashboard is an AI-powered content generation and scheduling platform designed to help users create and manage marketing campaigns across multiple social media channels.

**Architecture:** The project follows a standard monolithic architecture with a React frontend and a FastAPI backend. It is designed to be modular and extensible, allowing new tools and agents to be added easily.

**Technology Stack:**
- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL
- **Testing:** Pytest (backend), Vitest/Playwright (frontend)
- **CI/CD:** GitHub Actions

## 2. Codebase Navigation

The repository is organized into two main directories: `frontend` and `backend`.

- **`frontend/`**: Contains the React application.
  - `src/`: Main source code directory.
    - `components/`: Reusable UI components.
    - `pages/`: Top-level page components.
    - `hooks/`: Custom React hooks.
    - `lib/`: API clients and utility functions.
- **`backend/`**: Contains the FastAPI application.
  - `core/`: Core application logic, including security, database, and configuration.
  - `tools/`: Self-contained modules for different AI generation tools.
  - `models/`: SQLAlchemy database models.
  - `tests/`: Pytest tests for the backend.
- **`scripts/`**: Contains utility scripts for development and deployment.

## 3. Development Workflow

**Branch Naming:**
- **Features:** `feature/<description>` (e.g., `feature/add-linkedin-tool`)
- **Bugfixes:** `fix/<description>` (e.g., `fix/redis-connection-issue`)
- **Chores/Refactoring:** `chore/<description>` (e.g., `chore/update-dependencies`)

**Commit Messages:**
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.
- `feat:` for new features.
- `fix:` for bug fixes.
- `chore:` for maintenance tasks.
- `docs:` for documentation changes.
- `test:` for adding or improving tests.

**Testing:**
- All new backend code must be accompanied by unit or integration tests.
- Frontend changes should be tested with component tests where applicable.
- Before submitting, run all relevant tests to ensure no regressions were introduced.

## 4. Agent-Specific Guidelines

**Safety:**
- **Do not commit API keys or other secrets.** Use environment variables as configured by `setup.sh`.
- **Work in "demo mode" by default.** This mode uses mocked data and does not require live API keys.
- **Always verify your changes before submitting.** Use `read_file` and run tests to confirm your changes are correct.

**Environment:**
- Use the `setup.sh` script to create a consistent development environment.
- The script will configure environment variables for you. Do not modify `.env` files directly unless instructed.

**Database Migrations:**
- If you change a SQLAlchemy model, you will need to create a new database migration.
- Use the following command to generate a migration script:
  ```bash
  alembic revision --autogenerate -m "Your migration description"
  ```
- Review the generated script before committing.

## 5. Common Tasks

**Adding a New Tool:**
1.  Create a new directory in `backend/tools/`.
2.  Follow the structure of existing tools (e.g., `backend/tools/hello/`).
3.  Implement the tool's logic, schemas, and router.
4.  Register the new tool in `backend/tools/registry.py`.
5.  Add a corresponding UI component in the `frontend/src/tools/` directory.

**Updating an API Endpoint:**
1.  Locate the relevant router in the `backend/` directory.
2.  Modify the endpoint function.
3.  Update the corresponding Pydantic schemas if necessary.
4.  Update any frontend code that uses the endpoint.
5.  Ensure tests are updated to reflect the changes.

## 6. Troubleshooting

**"Redis connection refused" error:**
- This means the tests are trying to connect to a real Redis instance.
- This issue should be solved by the patch in `backend/tests/conftest.py`. If you see this error, it means the patch is not working correctly.

**`ModuleNotFoundError` during tests:**
- This means the test environment is not set up correctly.
- Make sure you have run `pip install -r backend/requirements.txt` and `npm install` in the `frontend` directory.
- If the issue persists, it may be a `PYTHONPATH` problem. Try running the tests and installation in the same command: `pip install -r backend/requirements.txt && pytest`.
