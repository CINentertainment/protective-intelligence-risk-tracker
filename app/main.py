from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Protective Intelligence Risk Tracker",
    description=(
        "A case-management API for tracking protective intelligence cases, "
        "indicators, assessments, and mitigation actions."
    ),
    version="0.2.0",
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


@app.get("/")
def read_root():
    return {
        "application": "Protective Intelligence Risk Tracker",
        "status": "operational",
        "version": "0.1.0",
    }


@app.get("/dashboard", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


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
    database: Session = Depends(get_db),
):
    statement = select(models.Case).order_by(models.Case.id)

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

    for field_name, value in changes.items():
        setattr(case, field_name, value)

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

    database.delete(indicator)
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

    # Keep the case's displayed risk level synchronized with
    # the latest formal risk assessment.
    case.risk_level = assessment_data.overall_risk

    database.add(assessment)
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
    assessment = database.get(models.RiskAssessment, assessment_id)

    if assessment is None or assessment.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk assessment not found.",
        )

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

    latest_assessment = database.scalars(latest_statement).first()

    if latest_assessment is None:
        case.risk_level = "Undetermined"
    else:
        case.risk_level = latest_assessment.overall_risk

    database.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)