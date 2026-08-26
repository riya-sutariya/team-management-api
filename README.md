# team-management-api

A production-style Team Management REST API built with FastAPI, PostgreSQL, SQLAlchemy, JWT authentication, RBAC, project membership, task management, and automated testing.

## Features

- User registration and authentication
- JWT access-token authentication
- Secure password hashing
- Refresh-token support
- Refresh-token hashing and rotation
- Role-based access control (RBAC)
- Permission-based authorization
- User management
- Project CRUD operations
- Project membership management
- Task creation and management
- Task ownership and assignment
- Task status and priority management
- Pagination and filtering
- PostgreSQL database
- SQLAlchemy ORM
- Alembic database migrations
- Service and repository layers
- Automated API tests with Pytest

## Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Authentication:** JWT
- **Password Hashing:** pwdlib
- **Testing:** Pytest
- **API Documentation:** Swagger / OpenAPI

## Project Structure

```text
team-management-api/
│
├── alembic/
│   └── versions/
│
├── app/
│   ├── routers/
│   ├── services/
│   ├── repositories/
│   ├── dependencies.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── main.py
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── README.md
└── requirements.txt