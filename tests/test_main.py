import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


TEST_DATABASE_URL = "sqlite://"


test_engine = create_engine(
    TEST_DATABASE_URL,
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
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)


def sample_case():
    return {
        "case_number": "PI-2026-TEST-001",
        "title": "Suspicious surveillance activity",
        "summary": (
            "Security personnel observed repeated surveillance-like "
            "behavior near a protected facility."
        ),
        "status": "Open",
        "priority": "Elevated",
        "risk_level": "Moderate",
        "opened_date": "2026-09-23",
        "next_review_date": "2026-09-30",
    }


def sample_indicator():
    return {
        "indicator_type": "Surveillance",
        "description": (
            "The same vehicle was observed parked near the primary "
            "entrance on three separate occasions."
        ),
        "source": "Security patrol report",
        "credibility": "High",
        "observed_date": "2026-09-24",
    }


def sample_assessment():
    return {
        "threat_level": "High",
        "vulnerability_level": "Moderate",
        "impact_level": "High",
        "overall_risk": "High",
        "rationale": (
            "Repeated surveillance activity and predictable access "
            "patterns increase the potential threat to the facility."
        ),
        "recommended_action": (
            "Increase patrol frequency and review available camera footage."
        ),
        "assessed_by": "Protective Intelligence Analyst",
        "assessment_date": "2026-09-24",
    }


def create_test_case():
    response = client.post(
        "/cases",
        json=sample_case(),
    )

    assert response.status_code == 201

    return response.json()


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
    response = client.post(
        "/cases",
        json=sample_case(),
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["case_number"] == "PI-2026-TEST-001"
    assert response_data["title"] == "Suspicious surveillance activity"
    assert response_data["status"] == "Open"
    assert response_data["priority"] == "Elevated"
    assert response_data["risk_level"] == "Moderate"
    assert "created_at" in response_data
    assert "updated_at" in response_data


def test_list_cases():
    created_case = create_test_case()

    response = client.get("/cases")

    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 1
    assert response_data[0]["id"] == created_case["id"]
    assert response_data[0]["case_number"] == "PI-2026-TEST-001"


def test_get_case():
    created_case = create_test_case()

    response = client.get(f"/cases/{created_case['id']}")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["id"] == created_case["id"]
    assert response_data["case_number"] == "PI-2026-TEST-001"
    assert response_data["indicators"] == []
    assert response_data["assessments"] == []


def test_get_missing_case():
    response = client.get("/cases/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }


def test_reject_duplicate_case_number():
    client.post(
        "/cases",
        json=sample_case(),
    )

    response = client.post(
        "/cases",
        json=sample_case(),
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A case with this case number already exists.",
    }


def test_update_case():
    created_case = create_test_case()

    response = client.patch(
        f"/cases/{created_case['id']}",
        json={
            "status": "Monitoring",
            "priority": "High",
            "risk_level": "High",
        },
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status"] == "Monitoring"
    assert response_data["priority"] == "High"
    assert response_data["risk_level"] == "High"
    assert response_data["title"] == created_case["title"]


def test_update_missing_case():
    response = client.patch(
        "/cases/999",
        json={
            "status": "Closed",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }


def test_reject_null_required_case_field():
    created_case = create_test_case()

    response = client.patch(
        f"/cases/{created_case['id']}",
        json={
            "title": None,
        },
    )

    assert response.status_code == 422


def test_delete_case():
    created_case = create_test_case()
    case_id = created_case["id"]

    delete_response = client.delete(f"/cases/{case_id}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/cases/{case_id}")

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Case not found.",
    }


def test_delete_missing_case():
    response = client.delete("/cases/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }


def test_create_indicator():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.post(
        f"/cases/{case_id}/indicators",
        json=sample_indicator(),
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["case_id"] == case_id
    assert response_data["indicator_type"] == "Surveillance"
    assert response_data["credibility"] == "High"
    assert response_data["source"] == "Security patrol report"
    assert "created_at" in response_data


def test_list_indicators():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.post(
        f"/cases/{case_id}/indicators",
        json=sample_indicator(),
    )

    response = client.get(
        f"/cases/{case_id}/indicators",
    )

    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data) == 1
    assert response_data[0]["indicator_type"] == "Surveillance"


def test_create_indicator_for_missing_case():
    response = client.post(
        "/cases/999/indicators",
        json=sample_indicator(),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }


def test_delete_indicator():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/indicators",
        json=sample_indicator(),
    )

    indicator_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/cases/{case_id}/indicators/{indicator_id}",
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = client.get(
        f"/cases/{case_id}/indicators",
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_create_risk_assessment():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.post(
        f"/cases/{case_id}/assessments",
        json=sample_assessment(),
    )

    assert response.status_code == 201

    response_data = response.json()

    assert response_data["id"] == 1
    assert response_data["case_id"] == case_id
    assert response_data["threat_level"] == "High"
    assert response_data["overall_risk"] == "High"
    assert response_data["assessed_by"] == "Protective Intelligence Analyst"
    assert "created_at" in response_data


def test_assessment_updates_case_risk_level():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.post(
        f"/cases/{case_id}/assessments",
        json=sample_assessment(),
    )

    response = client.get(f"/cases/{case_id}")

    assert response.status_code == 200
    assert response.json()["risk_level"] == "High"


def test_case_detail_includes_indicators_and_assessments():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.post(
        f"/cases/{case_id}/indicators",
        json=sample_indicator(),
    )

    client.post(
        f"/cases/{case_id}/assessments",
        json=sample_assessment(),
    )

    response = client.get(f"/cases/{case_id}")

    assert response.status_code == 200

    response_data = response.json()

    assert len(response_data["indicators"]) == 1
    assert len(response_data["assessments"]) == 1

    assert (
        response_data["indicators"][0]["indicator_type"]
        == "Surveillance"
    )

    assert (
        response_data["assessments"][0]["overall_risk"]
        == "High"
    )


def test_create_assessment_for_missing_case():
    response = client.post(
        "/cases/999/assessments",
        json=sample_assessment(),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }


def test_delete_assessment_resets_case_risk():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/assessments",
        json=sample_assessment(),
    )

    assessment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/cases/{case_id}/assessments/{assessment_id}",
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    case_response = client.get(f"/cases/{case_id}")

    assert case_response.status_code == 200
    assert case_response.json()["risk_level"] == "Undetermined"
    assert case_response.json()["assessments"] == []