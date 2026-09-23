from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Protective Intelligence Risk Tracker",
    description=(
        "A portfolio application for documenting protective intelligence "
        "cases, indicators, assessments, and mitigation actions."
    ),
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "application": "Protective Intelligence Risk Tracker",
        "status": "operational",
        "version": "0.1.0",
    }


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
    new_case = models.Case(**case_data.model_dump())

    database.add(new_case)

    try:
        database.commit()
        database.refresh(new_case)
    except IntegrityError:
        database.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A case with this case number already exists.",
        )

    return new_case


@app.get(
    "/cases",
    response_model=list[schemas.CaseResponse],
)
def list_cases(database: Session = Depends(get_db)):
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

    update_data = case_data.model_dump(exclude_unset=True)

    required_fields = {
        "case_number",
        "title",
        "summary",
        "status",
        "priority",
        "risk_level",
        "opened_date",
    }

    invalid_fields = [
        field_name
        for field_name in required_fields
        if field_name in update_data and update_data[field_name] is None
    ]

    if invalid_fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "These fields cannot be null: "
                + ", ".join(sorted(invalid_fields))
            ),
        )

    for field_name, value in update_data.items():
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