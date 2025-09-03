# Architecture Overview

This document provides a high-level overview of the Kyros Dashboard application architecture.

## 1. System Components

The application is composed of two main components:

- **Frontend**: A React single-page application (SPA) built with Vite and styled with Tailwind CSS.
- **Backend**: A FastAPI server that provides a RESTful API for the frontend.

## 2. Technology Stack

- **Frontend**: React 18, Vite, Tailwind CSS, TanStack Query, Axios, React Router
- **Backend**: FastAPI, PostgreSQL, Redis, Celery, Pydantic, JWT

## 3. Data Models

The core data models are:

- `User`: Represents a user of the application.
- `ContentJob`: Represents a content generation job.
- `ContentVariant`: Represents a single piece of generated content.
- `Preset`: Represents a user-defined preset for content generation.
- `ScheduledJob`: Represents a job scheduled for future execution.

## 4. Data Flow

1.  The user interacts with the frontend to create a content generation job.
2.  The frontend sends a request to the backend API.
3.  The backend creates a `ContentJob` and uses a Celery worker to generate the content variants asynchronously.
4.  The generated variants are stored in the PostgreSQL database.
5.  The frontend polls the backend for the status of the job and displays the variants when they are ready.
6.  The user can schedule a variant for future posting, which creates a `ScheduledJob` in the database.
7.  A Celery beat scheduler periodically checks for due jobs and posts them to the appropriate channel.
