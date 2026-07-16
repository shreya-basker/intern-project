# Task Management System

A FastAPI-based Task Management System with JWT authentication, Role-Based Access Control (RBAC), Projects, Tasks, Comments, and Audit Logging.

## Features

- JWT Authentication
- Viewer, Editor, and Admin roles
- Project management
- Task creation and assignment
- Comments on tasks
- Audit logging
- Async SQLAlchemy
- PostgreSQL
- Alembic migrations
- Pytest test suite

## Installation

Clone the repository:

```bash
git clone <your-github-repo>
cd intern-project/task-manager
```

Install dependencies:

```bash
uv sync
```

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=<your_database_url>
SECRET_KEY=<your_secret_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Database

Run migrations:

```bash
uv run alembic upgrade head
```

## Run the application

```bash
uv run uvicorn app.main:app --reload
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

## Run Tests

```bash
uv run pytest -v
```

Coverage:

```bash
uv run pytest --cov=app
```