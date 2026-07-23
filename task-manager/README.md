# Task Management System

A FastAPI-based Task Management System with JWT Authentication, Role-Based Access Control (RBAC), Projects, Tasks, Comments, Audit Logging, and an AI-powered asynchronous error logging and analysis system.

---

## Features

### Core Features

- JWT Authentication
- Role-Based Access Control (Viewer, Editor, Admin)
- Project Management
- Task Creation & Assignment
- Task Comments
- Audit Logging
- Async SQLAlchemy
- PostgreSQL
- Alembic Migrations
- Pytest Test Suite

### AI-Powered Error Analysis

- Global exception handling
- Structured error logging
- Asynchronous AI analysis using Celery
- Redis message broker
- Google Gemini integration
- AI-generated:
  - Error summary
  - Root cause analysis
  - Suggested fix
  - Severity classification
  - Confidence score
- SHA-256 error fingerprinting
- Automatic error grouping
- Traceback shortening
- Regex-based sanitization
- Shannon entropy-based secret detection
- Pydantic validation of AI responses
- Automatic retries for failed AI analysis

---

## Architecture

```text
                Client Request
                      │
                      ▼
               FastAPI Endpoint
                      │
             Exception Occurs
                      │
                      ▼
        Global Exception Handler
                      │
      Save ErrorLog to PostgreSQL
                      │
                      ▼
      Queue Celery Task (Redis)
                      │
                      ▼
             Celery Worker
                      │
         Fetch Error From Database
                      │
     Generate SHA-256 Fingerprint
                      │
      Find/Create ErrorGroup
                      │
   Sanitize & Shorten Traceback
                      │
                      ▼
          Google Gemini Analysis
                      │
      Validate Response (Pydantic)
                      │
                      ▼
      Update ErrorLog with Analysis
```

---

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy (Async)
- Alembic
- Celery
- Redis
- Google Gemini API
- Pydantic
- JWT Authentication
- Pytest

---

## Installation

Clone the repository

```bash
git clone <your-github-repo>
cd task-manager
```

Install dependencies

```bash
uv sync
```

---

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=<your_database_url>

SECRET_KEY=<your_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

GEMINI_API_KEY=<your_gemini_api_key>
GEMINI_MODEL=<your_model_name>

REDIS_URL=redis://localhost:6379/0
```

---

## Database

Run migrations

```bash
uv run alembic upgrade head
```

---

## Running the Application

Start Redis

```bash
redis-server
```

Start Celery

```bash
uv run celery -A app.core.celery worker --loglevel=info
```

Start FastAPI

```bash
uv run uvicorn app.main:app --reload
```

Swagger UI

```
http://127.0.0.1:8000/docs
```

---

## Error Processing Workflow

When an unhandled exception occurs:

1. Global exception handler captures the error.
2. Error is stored in PostgreSQL.
3. SHA-256 fingerprint is generated.
4. Error is assigned to an ErrorGroup.
5. Celery task is queued using Redis.
6. API returns immediately.
7. Celery worker:
   - retrieves the error
   - sanitizes sensitive data
   - shortens the traceback
   - sends it to Gemini
8. Gemini returns:
   - Summary
   - Root Cause
   - Suggested Fix
   - Severity
   - Confidence
9. Response is validated using Pydantic.
10. Database is updated with the AI analysis.

---

## Security

Before sending an error to Gemini:

- Regex-based sanitization removes passwords, tokens and API keys.
- Shannon entropy detection identifies high-entropy strings that may contain secrets.
- Sensitive information is redacted before analysis.

---

## Error Fingerprinting

Each error generates a deterministic SHA-256 fingerprint.

Identical errors are automatically grouped together, enabling:

- Duplicate error detection
- Frequency tracking
- Error grouping
- Foundation for future AI result caching

---

## Running Tests

```bash
uv run pytest -v
```

Coverage

```bash
uv run pytest --cov=app
```