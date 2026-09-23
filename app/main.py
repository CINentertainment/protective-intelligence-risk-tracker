from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db


# Create the database tables.
Base.metadata.create_all(bind=engine)


# Locate the frontend files.
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Protective Intelligence Risk Tracker",
    description=(
        "A case-management API for tracking protective intelligence cases, "
        "indicators, assessments, and mitigation actions."
    ),
    version="0.1.0",
)


# Make the CSS and JavaScript files available.
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


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
    response_model=schemas.CaseResponse,
)
def get_case(
    case_id: int,
    database: Session = Depends(get_db),
):
    case = database.get(models.Case, case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    return case


@app.patch(
    "/cases/{case_id}",
    response_model=schemas.CaseResponse,
)
def update_case(
    case_id: int,
    case_data: schemas.CaseUpdate,
    database: Session = Depends(get_db),
):
    case = database.get(models.Case, case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

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
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
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
    case = database.get(models.Case, case_id)

    if case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found.",
        )

    database.delete(case)
    database.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)