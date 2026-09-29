from datetime import date, datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, reporting, schemas
from app.database import (
    Base,
    engine,
    ensure_case_archive_columns,
    get_db,
)


Base.metadata.create_all(bind=engine)
ensure_case_archive_columns()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Protective Intelligence Risk Tracker",
    description=(
        "A case-management API for tracking protective intelligence cases, "
        "indicators, assessments, mitigation actions, and case activity."
    ),
    version="0.6.0",
)

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


def get_case_or_404(
    case_id: int,
    database: Session,
) -> models.Case:
    case = database.get(models.Case, case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return case


def get_mitigation_or_404(
    case_id: int,
    mitigation_id: int,
    database: Session,
) -> models.MitigationAction:
    mitigation = database.get(
        models.MitigationAction,
        mitigation_id,
    )

    if mitigation is None or mitigation.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mitigation action not found.",
        )

    return mitigation


def record_activity(
    database: Session,
    case_id: int,
    activity_type: str,
    description: str,
    actor: str | None = None,
) -> models.CaseActivity:
    activity = models.CaseActivity(
        case_id=case_id,
        activity_type=activity_type,
        description=description,
        actor=actor,
    )

    database.add(activity)

    return activity


@app.get("/")
def read_root():
    return {
        "application": "Protective Intelligence Risk Tracker",
        "status": "operational",
        "version": "0.6.0",
    }


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get(
    "/cases/{case_id}/report",
    response_class=HTMLResponse,
    include_in_schema=False,
)
def case_report(
    case_id: int,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    return HTMLResponse(
        content=reporting.build_case_report(case),
        status_code=status.HTTP_200_OK,
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/cases",
    response_model=schemas.CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case(
    case_data: schemas.CaseCreate,
    database: Session = Depends(get_db),
):
    case = models.Case(**case_data.model_dump())

    database.add(case)

    try:
        database.flush()

        record_activity(
            database=database,
            case_id=case.id,
            activity_type="case_created",
            description=(
                f"Case {case.case_number} was created with "
                f"{case.priority} priority."
            ),
            actor="System",
        )

        database.commit()
        database.refresh(case)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A case with this case number already exists.",
        )

    return case


@app.get(
    "/cases",
    response_model=list[schemas.CaseResponse],
)
def list_cases(
    include_archived: bool = False,
    database: Session = Depends(get_db),
):
    statement = select(models.Case)

    if not include_archived:
        statement = statement.where(
            models.Case.is_archived.is_(False)
        )

    statement = statement.order_by(models.Case.id)

    return database.scalars(statement).all()


@app.get(
    "/cases/{case_id}",
    response_model=schemas.CaseDetailResponse,
)
def get_case(
    case_id: int,
    database: Session = Depends(get_db),
):
    return get_case_or_404(case_id, database)


@app.patch(
    "/cases/{case_id}",
    response_model=schemas.CaseResponse,
)
def update_case(
    case_id: int,
    case_data: schemas.CaseUpdate,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)
    changes = case_data.model_dump(exclude_unset=True)

    required_fields = {
        "case_number",
        "title",
        "summary",
        "status",
        "priority",
        "risk_level",
        "opened_date",
    }

    for field_name in required_fields:
        if field_name in changes and changes[field_name] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{field_name} cannot be null.",
            )

    changed_fields = []

    for field_name, value in changes.items():
        if getattr(case, field_name) != value:
            changed_fields.append(field_name)

        setattr(case, field_name, value)

    if changed_fields:
        readable_fields = ", ".join(
            field_name.replace("_", " ")
            for field_name in changed_fields
        )

        record_activity(
            database=database,
            case_id=case.id,
            activity_type="case_updated",
            description=(
                "Case record updated. Changed fields: "
                f"{readable_fields}."
            ),
            actor="System",
        )

    try:
        database.commit()
        database.refresh(case)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A case with this case number already exists.",
        )

    return case


@app.patch(
    "/cases/{case_id}/archive",
    response_model=schemas.CaseResponse,
)
def archive_case(
    case_id: int,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    if not case.is_archived:
        case.is_archived = True
        case.archived_at = datetime.now()

        record_activity(
            database=database,
            case_id=case.id,
            activity_type="case_archived",
            description=(
                f"Case {case.case_number} was archived."
            ),
            actor="System",
        )

        database.commit()
        database.refresh(case)

    return case


@app.patch(
    "/cases/{case_id}/restore",
    response_model=schemas.CaseResponse,
)
def restore_case(
    case_id: int,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    if case.is_archived:
        case.is_archived = False
        case.archived_at = None

        record_activity(
            database=database,
            case_id=case.id,
            activity_type="case_restored",
            description=(
                f"Case {case.case_number} was restored."
            ),
            actor="System",
        )

        database.commit()
        database.refresh(case)

    return case


@app.delete(
    "/cases/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_case(
    case_id: int,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    database.delete(case)
    database.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get(
    "/cases/{case_id}/activities",
    response_model=list[schemas.CaseActivityResponse],
)
def list_case_activities(
    case_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    statement = (
        select(models.CaseActivity)
        .where(models.CaseActivity.case_id == case_id)
        .order_by(
            models.CaseActivity.created_at.desc(),
            models.CaseActivity.id.desc(),
        )
    )

    return database.scalars(statement).all()


@app.post(
    "/cases/{case_id}/indicators",
    response_model=schemas.IndicatorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_indicator(
    case_id: int,
    indicator_data: schemas.IndicatorCreate,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    indicator = models.Indicator(
        case_id=case_id,
        **indicator_data.model_dump(),
    )

    database.add(indicator)

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="indicator_created",
        description=(
            f"A {indicator.indicator_type} indicator was added "
            f"with {indicator.credibility} credibility."
        ),
        actor="System",
    )

    database.commit()
    database.refresh(indicator)

    return indicator


@app.get(
    "/cases/{case_id}/indicators",
    response_model=list[schemas.IndicatorResponse],
)
def list_indicators(
    case_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    statement = (
        select(models.Indicator)
        .where(models.Indicator.case_id == case_id)
        .order_by(
            models.Indicator.observed_date.desc(),
            models.Indicator.id.desc(),
        )
    )

    return database.scalars(statement).all()


@app.delete(
    "/cases/{case_id}/indicators/{indicator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_indicator(
    case_id: int,
    indicator_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    indicator = database.get(models.Indicator, indicator_id)

    if indicator is None or indicator.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicator not found.",
        )

    indicator_type = indicator.indicator_type

    database.delete(indicator)

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="indicator_deleted",
        description=(
            f"The {indicator_type} indicator was deleted."
        ),
        actor="System",
    )

    database.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/cases/{case_id}/assessments",
    response_model=schemas.RiskAssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    case_id: int,
    assessment_data: schemas.RiskAssessmentCreate,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    assessment = models.RiskAssessment(
        case_id=case_id,
        **assessment_data.model_dump(),
    )

    previous_risk = case.risk_level
    case.risk_level = assessment_data.overall_risk

    database.add(assessment)

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="assessment_created",
        description=(
            "A risk assessment was recorded. Case risk changed "
            f"from {previous_risk} to "
            f"{assessment_data.overall_risk}."
        ),
        actor=assessment_data.assessed_by or "System",
    )

    database.commit()
    database.refresh(assessment)

    return assessment


@app.get(
    "/cases/{case_id}/assessments",
    response_model=list[schemas.RiskAssessmentResponse],
)
def list_assessments(
    case_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    statement = (
        select(models.RiskAssessment)
        .where(models.RiskAssessment.case_id == case_id)
        .order_by(
            models.RiskAssessment.assessment_date.desc(),
            models.RiskAssessment.id.desc(),
        )
    )

    return database.scalars(statement).all()


@app.delete(
    "/cases/{case_id}/assessments/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assessment(
    case_id: int,
    assessment_id: int,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    assessment = database.get(
        models.RiskAssessment,
        assessment_id,
    )

    if assessment is None or assessment.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found.",
        )

    deleted_risk = assessment.overall_risk

    database.delete(assessment)
    database.flush()

    latest_statement = (
        select(models.RiskAssessment)
        .where(models.RiskAssessment.case_id == case_id)
        .order_by(
            models.RiskAssessment.assessment_date.desc(),
            models.RiskAssessment.id.desc(),
        )
    )

    latest_assessment = database.scalars(
        latest_statement
    ).first()

    if latest_assessment is None:
        case.risk_level = "Undetermined"
    else:
        case.risk_level = latest_assessment.overall_risk

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="assessment_deleted",
        description=(
            f"A {deleted_risk} risk assessment was deleted. "
            f"Current case risk is {case.risk_level}."
        ),
        actor="System",
    )

    database.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/cases/{case_id}/mitigations",
    response_model=schemas.MitigationActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_mitigation(
    case_id: int,
    mitigation_data: schemas.MitigationActionCreate,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    action_data = mitigation_data.model_dump()

    if (
        action_data["status"] == "Completed"
        and action_data["completed_date"] is None
    ):
        action_data["completed_date"] = date.today()

    mitigation = models.MitigationAction(
        case_id=case_id,
        **action_data,
    )

    database.add(mitigation)

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="mitigation_created",
        description=(
            f'Mitigation action "{mitigation.title}" was created '
            f"with {mitigation.priority} priority."
        ),
        actor=mitigation.owner or "System",
    )

    database.commit()
    database.refresh(mitigation)

    return mitigation


@app.get(
    "/cases/{case_id}/mitigations",
    response_model=list[schemas.MitigationActionResponse],
)
def list_mitigations(
    case_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    statement = (
        select(models.MitigationAction)
        .where(models.MitigationAction.case_id == case_id)
        .order_by(models.MitigationAction.id.desc())
    )

    return database.scalars(statement).all()


@app.patch(
    "/cases/{case_id}/mitigations/{mitigation_id}",
    response_model=schemas.MitigationActionResponse,
)
def update_mitigation(
    case_id: int,
    mitigation_id: int,
    mitigation_data: schemas.MitigationActionUpdate,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    mitigation = get_mitigation_or_404(
        case_id,
        mitigation_id,
        database,
    )

    changes = mitigation_data.model_dump(exclude_unset=True)

    required_fields = {
        "title",
        "description",
        "priority",
        "status",
    }

    for field_name in required_fields:
        if field_name in changes and changes[field_name] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"{field_name} cannot be null.",
            )

    previous_status = mitigation.status
    changed_fields = []

    for field_name, value in changes.items():
        if getattr(mitigation, field_name) != value:
            changed_fields.append(field_name)

        setattr(mitigation, field_name, value)

    if "status" in changes:
        if (
            changes["status"] == "Completed"
            and "completed_date" not in changes
        ):
            mitigation.completed_date = date.today()

        if changes["status"] != "Completed":
            mitigation.completed_date = None

    if changed_fields:
        if (
            "status" in changed_fields
            and previous_status != mitigation.status
        ):
            description = (
                f'Mitigation action "{mitigation.title}" changed '
                f"from {previous_status} to {mitigation.status}."
            )
        else:
            readable_fields = ", ".join(
                field_name.replace("_", " ")
                for field_name in changed_fields
            )

            description = (
                f'Mitigation action "{mitigation.title}" was '
                f"updated. Changed fields: {readable_fields}."
            )

        record_activity(
            database=database,
            case_id=case_id,
            activity_type="mitigation_updated",
            description=description,
            actor=mitigation.owner or "System",
        )

    database.commit()
    database.refresh(mitigation)

    return mitigation


@app.delete(
    "/cases/{case_id}/mitigations/{mitigation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_mitigation(
    case_id: int,
    mitigation_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    mitigation = get_mitigation_or_404(
        case_id,
        mitigation_id,
        database,
    )

    mitigation_title = mitigation.title
    mitigation_owner = mitigation.owner

    database.delete(mitigation)

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="mitigation_deleted",
        description=(
            f'Mitigation action "{mitigation_title}" was deleted.'
        ),
        actor=mitigation_owner or "System",
    )

    database.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)