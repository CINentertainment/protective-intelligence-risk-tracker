import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
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
    client.cookies.clear()

    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    client.cookies.clear()
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


def sample_mitigation() -> dict:
    return {
        "title": "Increase protective surveillance",
        "description": (
            "Assign additional personnel to monitor the primary entrance "
            "and document suspicious activity."
        ),
        "owner": "Protective Security Team",
        "priority": "High",
        "status": "Planned",
        "due_date": "2026-10-01",
        "completed_date": None,
    }


def create_test_case():
    response = client.post(
        "/cases",
        json=sample_case(),
    )

    assert response.status_code == 201

    return response.json()


def get_activity_types(case_id: int) -> list[str]:
    response = client.get(f"/cases/{case_id}/activities")

    assert response.status_code == 200

    return [
        activity["activity_type"]
        for activity in response.json()
    ]


def test_read_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "application": "Protective Intelligence Risk Tracker",
        "status": "operational",
        "version": "0.6.0",
    }

def test_dashboard():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Protective Intelligence Risk Tracker" in response.text
    assert "Version 0.6.0" in response.text


def test_openapi_version():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["version"] == "0.6.0"

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


def test_create_mitigation():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    assert response.status_code == 201

    mitigation = response.json()

    assert mitigation["case_id"] == case_id
    assert mitigation["title"] == "Increase protective surveillance"
    assert mitigation["owner"] == "Protective Security Team"
    assert mitigation["priority"] == "High"
    assert mitigation["status"] == "Planned"
    assert mitigation["due_date"] == "2026-10-01"
    assert mitigation["completed_date"] is None
    assert isinstance(mitigation["id"], int)


def test_list_mitigations():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    response = client.get(f"/cases/{case_id}/mitigations")

    assert response.status_code == 200

    mitigations = response.json()

    assert len(mitigations) == 1
    assert mitigations[0]["title"] == "Increase protective surveillance"
    assert mitigations[0]["case_id"] == case_id


def test_case_detail_includes_mitigations():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    response = client.get(f"/cases/{case_id}")

    assert response.status_code == 200
    assert len(response.json()["mitigation_actions"]) == 1
    assert (
        response.json()["mitigation_actions"][0]["title"]
        == "Increase protective surveillance"
    )


def test_update_mitigation():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    mitigation_id = create_response.json()["id"]

    response = client.patch(
        f"/cases/{case_id}/mitigations/{mitigation_id}",
        json={
            "owner": "Operations Manager",
            "priority": "Critical",
            "status": "In Progress",
        },
    )

    assert response.status_code == 200

    mitigation = response.json()

    assert mitigation["owner"] == "Operations Manager"
    assert mitigation["priority"] == "Critical"
    assert mitigation["status"] == "In Progress"


def test_complete_mitigation_sets_completed_date():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    mitigation_id = create_response.json()["id"]

    response = client.patch(
        f"/cases/{case_id}/mitigations/{mitigation_id}",
        json={"status": "Completed"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Completed"
    assert response.json()["completed_date"] is not None


def test_delete_mitigation():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    mitigation_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/cases/{case_id}/mitigations/{mitigation_id}"
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = client.get(f"/cases/{case_id}/mitigations")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_create_mitigation_for_missing_case():
    response = client.post(
        "/cases/999/mitigations",
        json=sample_mitigation(),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Case not found."}


def test_case_creation_records_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.get(f"/cases/{case_id}/activities")

    assert response.status_code == 200

    activities = response.json()

    assert len(activities) == 1
    assert activities[0]["case_id"] == case_id
    assert activities[0]["activity_type"] == "case_created"
    assert activities[0]["actor"] == "System"
    assert "PI-2026-TEST-001" in activities[0]["description"]
    assert "created_at" in activities[0]


def test_case_detail_includes_activities():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.get(f"/cases/{case_id}")

    assert response.status_code == 200

    response_data = response.json()

    assert "activities" in response_data
    assert len(response_data["activities"]) == 1
    assert (
        response_data["activities"][0]["activity_type"]
        == "case_created"
    )


def test_case_update_records_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    update_response = client.patch(
        f"/cases/{case_id}",
        json={
            "status": "Monitoring",
            "priority": "High",
        },
    )

    assert update_response.status_code == 200

    activities_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activities_response.status_code == 200

    activities = activities_response.json()

    assert activities[0]["activity_type"] == "case_updated"
    assert "status" in activities[0]["description"]
    assert "priority" in activities[0]["description"]
    assert activities[1]["activity_type"] == "case_created"


def test_indicator_actions_record_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/indicators",
        json=sample_indicator(),
    )

    assert create_response.status_code == 201

    indicator_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/cases/{case_id}/indicators/{indicator_id}"
    )

    assert delete_response.status_code == 204

    activity_types = get_activity_types(case_id)

    assert activity_types == [
        "indicator_deleted",
        "indicator_created",
        "case_created",
    ]


def test_assessment_actions_record_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/assessments",
        json=sample_assessment(),
    )

    assert create_response.status_code == 201

    assessment_id = create_response.json()["id"]

    activities_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activities_response.status_code == 200

    created_activity = activities_response.json()[0]

    assert created_activity["activity_type"] == "assessment_created"
    assert created_activity["actor"] == (
        "Protective Intelligence Analyst"
    )
    assert "Moderate to High" in created_activity["description"]

    delete_response = client.delete(
        f"/cases/{case_id}/assessments/{assessment_id}"
    )

    assert delete_response.status_code == 204

    activity_types = get_activity_types(case_id)

    assert activity_types == [
        "assessment_deleted",
        "assessment_created",
        "case_created",
    ]


def test_mitigation_actions_record_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    create_response = client.post(
        f"/cases/{case_id}/mitigations",
        json=sample_mitigation(),
    )

    assert create_response.status_code == 201

    mitigation_id = create_response.json()["id"]

    complete_response = client.patch(
        f"/cases/{case_id}/mitigations/{mitigation_id}",
        json={"status": "Completed"},
    )

    assert complete_response.status_code == 200

    delete_response = client.delete(
        f"/cases/{case_id}/mitigations/{mitigation_id}"
    )

    assert delete_response.status_code == 204

    activities_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activities_response.status_code == 200

    activities = activities_response.json()

    activity_types = [
        activity["activity_type"]
        for activity in activities
    ]

    assert activity_types == [
        "mitigation_deleted",
        "mitigation_updated",
        "mitigation_created",
        "case_created",
    ]

    assert "Planned to Completed" in (
        activities[1]["description"]
    )

    assert activities[2]["actor"] == (
        "Protective Security Team"
    )


def test_activities_for_missing_case():
    response = client.get("/cases/999/activities")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }


def test_case_report():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.get(f"/cases/{case_id}/report")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert created_case["case_number"] in response.text
    assert created_case["title"] in response.text
    assert "Case Overview" in response.text
    assert "Indicators" in response.text
    assert "Risk Assessments" in response.text
    assert "Mitigation Actions" in response.text
    assert "Activity Timeline" in response.text


def test_case_report_for_missing_case():
    response = client.get("/cases/999/report")

    assert response.status_code == 404
    assert response.json() == {"detail": "Case not found."}

def test_archive_case():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.patch(f"/cases/{case_id}/archive")

    assert response.status_code == 200
    assert response.json()["is_archived"] is True
    assert response.json()["archived_at"] is not None


def test_archived_case_hidden_from_default_list():
    created_case = create_test_case()
    case_id = created_case["id"]

    archive_response = client.patch(
        f"/cases/{case_id}/archive"
    )

    assert archive_response.status_code == 200

    list_response = client.get("/cases")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_include_archived_cases_in_list():
    created_case = create_test_case()
    case_id = created_case["id"]

    archive_response = client.patch(
        f"/cases/{case_id}/archive"
    )

    assert archive_response.status_code == 200

    list_response = client.get(
        "/cases",
        params={"include_archived": True},
    )

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == case_id
    assert list_response.json()[0]["is_archived"] is True


def test_restore_case():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.patch(f"/cases/{case_id}/archive")

    restore_response = client.patch(
        f"/cases/{case_id}/restore"
    )

    assert restore_response.status_code == 200
    assert restore_response.json()["is_archived"] is False
    assert restore_response.json()["archived_at"] is None

    list_response = client.get("/cases")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["id"] == case_id


def test_archive_and_restore_record_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    client.patch(f"/cases/{case_id}/archive")
    client.patch(f"/cases/{case_id}/restore")

    activity_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activity_response.status_code == 200

    activity_types = [
        activity["activity_type"]
        for activity in activity_response.json()
    ]

    assert "case_archived" in activity_types
    assert "case_restored" in activity_types


def test_archive_missing_case():
    response = client.patch("/cases/999/archive")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found."
    }


def test_restore_missing_case():
    response = client.patch("/cases/999/restore")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found."
    }

def test_create_case_with_assignment():
    case_data = sample_case()
    case_data["assigned_analyst"] = "Jordan Lee"
    case_data["responsible_team"] = (
        "Protective Intelligence Unit"
    )

    response = client.post(
        "/cases",
        json=case_data,
    )

    assert response.status_code == 201

    created_case = response.json()

    assert created_case["assigned_analyst"] == "Jordan Lee"
    assert (
        created_case["responsible_team"]
        == "Protective Intelligence Unit"
    )
    assert created_case["assigned_at"] is not None


def test_case_assignment_records_activity():
    case_data = sample_case()
    case_data["assigned_analyst"] = "Jordan Lee"
    case_data["responsible_team"] = (
        "Protective Intelligence Unit"
    )

    create_response = client.post(
        "/cases",
        json=case_data,
    )

    assert create_response.status_code == 201

    case_id = create_response.json()["id"]

    activity_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activity_response.status_code == 200

    activities = activity_response.json()
    activity_types = [
        activity["activity_type"]
        for activity in activities
    ]

    assert "case_created" in activity_types
    assert "case_assigned" in activity_types

    assignment_activity = next(
        activity
        for activity in activities
        if activity["activity_type"] == "case_assigned"
    )

    assert "Jordan Lee" in assignment_activity["description"]
    assert (
        "Protective Intelligence Unit"
        in assignment_activity["description"]
    )
    assert assignment_activity["actor"] == "Jordan Lee"


def test_update_case_assignment():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.patch(
        f"/cases/{case_id}",
        json={
            "assigned_analyst": "Morgan Reyes",
            "responsible_team": "Threat Management Team",
        },
    )

    assert response.status_code == 200

    updated_case = response.json()

    assert (
        updated_case["assigned_analyst"]
        == "Morgan Reyes"
    )
    assert (
        updated_case["responsible_team"]
        == "Threat Management Team"
    )
    assert updated_case["assigned_at"] is not None

    activity_types = get_activity_types(case_id)

    assert "case_updated" in activity_types
    assert "case_assigned" in activity_types


def test_reassign_case_records_activity():
    case_data = sample_case()
    case_data["assigned_analyst"] = "Jordan Lee"
    case_data["responsible_team"] = (
        "Protective Intelligence Unit"
    )

    create_response = client.post(
        "/cases",
        json=case_data,
    )

    assert create_response.status_code == 201

    case_id = create_response.json()["id"]

    update_response = client.patch(
        f"/cases/{case_id}",
        json={
            "assigned_analyst": "Morgan Reyes",
            "responsible_team": "Threat Management Team",
        },
    )

    assert update_response.status_code == 200

    updated_case = update_response.json()

    assert (
        updated_case["assigned_analyst"]
        == "Morgan Reyes"
    )
    assert (
        updated_case["responsible_team"]
        == "Threat Management Team"
    )

    activities_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activities_response.status_code == 200

    activities = activities_response.json()

    reassignment_activity = next(
        activity
        for activity in activities
        if activity["activity_type"] == "case_reassigned"
    )

    assert "Morgan Reyes" in (
        reassignment_activity["description"]
    )
    assert "Threat Management Team" in (
        reassignment_activity["description"]
    )
    assert reassignment_activity["actor"] == "Morgan Reyes"


def test_clear_case_assignment():
    case_data = sample_case()
    case_data["assigned_analyst"] = "Jordan Lee"
    case_data["responsible_team"] = (
        "Protective Intelligence Unit"
    )

    create_response = client.post(
        "/cases",
        json=case_data,
    )

    assert create_response.status_code == 201

    case_id = create_response.json()["id"]

    clear_response = client.patch(
        f"/cases/{case_id}",
        json={
            "assigned_analyst": None,
            "responsible_team": None,
        },
    )

    assert clear_response.status_code == 200

    cleared_case = clear_response.json()

    assert cleared_case["assigned_analyst"] is None
    assert cleared_case["responsible_team"] is None
    assert cleared_case["assigned_at"] is None

    activity_types = get_activity_types(case_id)

    assert "case_unassigned" in activity_types


def test_assignment_fields_enforce_maximum_length():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.patch(
        f"/cases/{case_id}",
        json={
            "assigned_analyst": "A" * 151,
        },
    )

    assert response.status_code == 422

def sample_case_review() -> dict:
    return {
        "review_date": "2026-10-08",
        "reviewed_by": "Jordan Lee",
        "findings": (
            "The case remains active. Existing indicators were reviewed, "
            "and continued monitoring is recommended."
        ),
        "next_review_date": "2026-10-15",
    }


def test_create_case_review():
    created_case = create_test_case()
    case_id = created_case["id"]

    response = client.post(
        f"/cases/{case_id}/reviews",
        json=sample_case_review(),
    )

    assert response.status_code == 201

    review = response.json()

    assert review["id"] == 1
    assert review["case_id"] == case_id
    assert review["review_date"] == "2026-10-08"
    assert review["reviewed_by"] == "Jordan Lee"
    assert review["next_review_date"] == "2026-10-15"
    assert "continued monitoring" in review["findings"]
    assert review["created_at"] is not None


def test_list_case_reviews():
    created_case = create_test_case()
    case_id = created_case["id"]

    first_review = sample_case_review()

    first_response = client.post(
        f"/cases/{case_id}/reviews",
        json=first_review,
    )

    assert first_response.status_code == 201

    second_review = sample_case_review()
    second_review["review_date"] = "2026-10-09"
    second_review["reviewed_by"] = "Morgan Reyes"
    second_review["findings"] = (
        "New information was reviewed. The case should remain open."
    )
    second_review["next_review_date"] = "2026-10-20"

    second_response = client.post(
        f"/cases/{case_id}/reviews",
        json=second_review,
    )

    assert second_response.status_code == 201

    list_response = client.get(
        f"/cases/{case_id}/reviews"
    )

    assert list_response.status_code == 200

    reviews = list_response.json()

    assert len(reviews) == 2
    assert reviews[0]["reviewed_by"] == "Morgan Reyes"
    assert reviews[0]["review_date"] == "2026-10-09"
    assert reviews[1]["reviewed_by"] == "Jordan Lee"
    assert reviews[1]["review_date"] == "2026-10-08"


def test_case_review_updates_next_review_date():
    created_case = create_test_case()
    case_id = created_case["id"]

    review_response = client.post(
        f"/cases/{case_id}/reviews",
        json=sample_case_review(),
    )

    assert review_response.status_code == 201

    case_response = client.get(
        f"/cases/{case_id}"
    )

    assert case_response.status_code == 200

    case_data = case_response.json()

    assert case_data["next_review_date"] == "2026-10-15"
    assert len(case_data["reviews"]) == 1
    assert (
        case_data["reviews"][0]["reviewed_by"]
        == "Jordan Lee"
    )
    assert (
        case_data["reviews"][0]["next_review_date"]
        == "2026-10-15"
    )


def test_case_review_records_activity():
    created_case = create_test_case()
    case_id = created_case["id"]

    review_response = client.post(
        f"/cases/{case_id}/reviews",
        json=sample_case_review(),
    )

    assert review_response.status_code == 201

    activity_response = client.get(
        f"/cases/{case_id}/activities"
    )

    assert activity_response.status_code == 200

    activities = activity_response.json()

    review_activity = next(
        activity
        for activity in activities
        if activity["activity_type"] == "case_reviewed"
    )

    assert review_activity["actor"] == "Jordan Lee"
    assert "2026-10-15" in review_activity["description"]


def test_reject_review_with_invalid_next_review_date():
    created_case = create_test_case()
    case_id = created_case["id"]

    review_data = sample_case_review()
    review_data["review_date"] = "2026-10-08"
    review_data["next_review_date"] = "2026-10-07"

    response = client.post(
        f"/cases/{case_id}/reviews",
        json=review_data,
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": (
            "next_review_date cannot be earlier than "
            "review_date."
        ),
    }


def test_create_review_for_missing_case():
    response = client.post(
        "/cases/999/reviews",
        json=sample_case_review(),
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Case not found.",
    }
def sample_user() -> dict:
    return {
        "username": "test.admin",
        "full_name": "Test Administrator",
        "password": "SecurePassword123!",
        "role": "Read Only",
    }


def bootstrap_test_administrator() -> dict:
    response = client.post(
        "/auth/bootstrap",
        json=sample_user(),
    )

    assert response.status_code == 201

    return response.json()


def login_test_administrator():
    response = client.post(
        "/auth/login",
        json={
            "username": "test.admin",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 200

    return response


def test_bootstrap_administrator():
    response = client.post(
        "/auth/bootstrap",
        json=sample_user(),
    )

    assert response.status_code == 201

    user = response.json()

    assert user["id"] == 1
    assert user["username"] == "test.admin"
    assert user["full_name"] == "Test Administrator"
    assert user["role"] == "Administrator"
    assert user["is_active"] is True
    assert "password" not in user
    assert "hashed_password" not in user


def test_bootstrap_hashes_password():
    bootstrap_test_administrator()

    with TestingSessionLocal() as database:
        user = database.scalar(
            select(models.User)
        )

        assert user is not None
        assert (
            user.hashed_password
            != "SecurePassword123!"
        )
        assert user.hashed_password.startswith("$argon2")


def test_reject_second_bootstrap():
    bootstrap_test_administrator()

    response = client.post(
        "/auth/bootstrap",
        json={
            "username": "second.admin",
            "full_name": "Second Administrator",
            "password": "AnotherSecurePassword123!",
            "role": "Administrator",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "Initial administrator setup has already "
            "been completed."
        ),
    }


def test_login_sets_authentication_cookie():
    bootstrap_test_administrator()

    response = login_test_administrator()

    assert response.json()["message"] == "Login successful."
    assert (
        response.json()["user"]["role"]
        == "Administrator"
    )
    assert "pirt_access_token" in client.cookies


def test_reject_invalid_login():
    bootstrap_test_administrator()

    response = client.post(
        "/auth/login",
        json={
            "username": "test.admin",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid username or password.",
    }


def test_get_authenticated_user():
    bootstrap_test_administrator()
    login_test_administrator()

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["username"] == "test.admin"
    assert response.json()["role"] == "Administrator"


def test_authentication_required_without_cookie():
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required.",
    }


def test_logout_clears_authentication_cookie():
    bootstrap_test_administrator()
    login_test_administrator()

    logout_response = client.post("/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json() == {
        "message": "Logout successful.",
    }

    current_user_response = client.get("/auth/me")

    assert current_user_response.status_code == 401