import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def override_get_db():
    database = TestingSessionLocal()

    try:
        yield database
    finally:
        database.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield


def sample_case(case_number: str = "PI-2026-001"):
    return {
        "case_number": case_number,
        "title": "Suspicious surveillance activity",
        "summary": (
            "Repeated surveillance-like behavior was reported near a "
            "protected facility."
        ),
        "status": "Open",
        "priority": "Elevated",
        "risk_level": "Moderate",
        "opened_date": "2026-09-23",
        "next_review_date": "2026-09-30",
    }


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "application": "Protective Intelligence Risk Tracker",
        "status": "operational",
        "version": "0.1.0",
    }


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_case():
    response = client.post("/cases", json=sample_case())

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["case_number"] == "PI-2026-001"
    assert response_data["title"] == "Suspicious surveillance activity"
    assert response_data["priority"] == "Elevated"
    assert response_data["risk_level"] == "Moderate"
    assert "created_at" in response_data
    assert "updated_at" in response_data


def test_list_cases():
    client.post("/cases", json=sample_case("PI-2026-001"))
    client.post("/cases", json=sample_case("PI-2026-002"))

    response = client.get("/cases")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["case_number"] == "PI-2026-001"
    assert response.json()[1]["case_number"] == "PI-2026-002"


def test_get_case():
    create_response = client.post("/cases", json=sample_case())
    case_id = create_response.json()["id"]

    response = client.get(f"/cases/{case_id}")

    assert response.status_code == 200
    assert response.json()["id"] == case_id
    assert response.json()["case_number"] == "PI-2026-001"


def test_get_missing_case():
    response = client.get("/cases/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Case not found."}


def test_reject_duplicate_case_number():
    client.post("/cases", json=sample_case())

    response = client.post("/cases", json=sample_case())

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A case with this case number already exists."
    }