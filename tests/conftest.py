from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import hash_password


TEST_DATABASE_URL = "sqlite://"


engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def create_user(db):
    def _create_user(
        name,
        email,
        role="USER",
        password="password123"
    ):
        user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=role
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    return _create_user

@pytest.fixture
def get_token(client):
    def _get_token(email, password="password123"):
        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password
            }
        )

        return response.json()["access_token"]

    return _get_token

