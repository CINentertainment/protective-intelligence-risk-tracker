from fastapi import Depends, FastAPI, HTTPException, status
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