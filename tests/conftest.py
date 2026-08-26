from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db


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