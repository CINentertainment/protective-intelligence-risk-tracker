from datetime import date, datetime
from pathlib import Path

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Response,
    status,
)
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import auth, models, reporting, schemas
from app.database import (
    Base,
    engine,
    ensure_case_archive_columns,
    ensure_case_assignment_columns,
    get_db,
)


Base.metadata.create_all(bind=engine)
ensure_case_archive_columns()
ensure_case_assignment_columns()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Protective Intelligence Risk Tracker",
    description=(
        "A case-management API for tracking protective intelligence cases, "
        "indicators, assessments, mitigation actions, case reviews, and "
        "case activity."
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
    "/auth/bootstrap",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def bootstrap_administrator(
    user_data: schemas.UserCreate,
    database: Session = Depends(get_db),
):
    existing_user = database.scalar(
        select(models.User.id).limit(1)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Initial administrator setup has already "
                "been completed."
            ),
        )

    user = models.User(
        username=user_data.username.lower(),
        full_name=user_data.full_name.strip(),
        hashed_password=auth.hash_password(
            user_data.password
        ),
        role="Administrator",
        is_active=True,
    )

    database.add(user)

    try:
        database.commit()
        database.refresh(user)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username is already in use.",
        )

    return user


@app.post(
    "/auth/login",
    response_model=schemas.AuthenticationResponse,
)
def login(
    login_data: schemas.LoginRequest,
    response: Response,
    database: Session = Depends(get_db),
):
    statement = select(models.User).where(
        models.User.username
        == login_data.username.lower()
    )

    user = database.scalar(statement)

    if (
        user is None
        or not user.is_active
        or not auth.verify_password(
            login_data.password,
            user.hashed_password,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    access_token = auth.create_access_token(user)

    response.set_cookie(
        key=auth.AUTH_COOKIE_NAME,
        value=access_token,
        max_age=auth.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,
        samesite="strict",
        path="/",
    )

    return {
        "message": "Login successful.",
        "user": user,
    }


@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(
        key=auth.AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=False,
        samesite="strict",
    )

    return {"message": "Logout successful."}


@app.get(
    "/auth/me",
    response_model=schemas.UserResponse,
)
def get_authenticated_user(
    current_user: auth.CurrentUser,
):
    return current_user
@app.post(
    "/users",
    response_model=schemas.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: schemas.UserCreate,
    current_user: models.User = Depends(
        auth.require_roles("Administrator")
    ),
    database: Session = Depends(get_db),
):
    user = models.User(
        username=user_data.username.lower(),
        full_name=user_data.full_name.strip(),
        hashed_password=auth.hash_password(
            user_data.password
        ),
        role=user_data.role,
        is_active=True,
    )

    database.add(user)

    try:
        database.commit()
        database.refresh(user)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="That username is already in use.",
        )

    return user


@app.get(
    "/users",
    response_model=list[schemas.UserResponse],
)
def list_users(
    current_user: models.User = Depends(
        auth.require_roles("Administrator")
    ),
    database: Session = Depends(get_db),
):
    statement = select(models.User).order_by(
        models.User.full_name,
        models.User.id,
    )

    return database.scalars(statement).all()
@app.post(
    "/cases",
    response_model=schemas.CaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case(
    case_data: schemas.CaseCreate,
    database: Session = Depends(get_db),
):
    case_values = case_data.model_dump()

    if (
        case_values["assigned_analyst"]
        or case_values["responsible_team"]
    ):
        case_values["assigned_at"] = datetime.now()

    case = models.Case(**case_values)

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

        if case.assigned_analyst or case.responsible_team:
            assignment_parts = []

            if case.assigned_analyst:
                assignment_parts.append(
                    f"analyst {case.assigned_analyst}"
                )

            if case.responsible_team:
                assignment_parts.append(
                    f"team {case.responsible_team}"
                )

            assignment_description = " and ".join(
                assignment_parts
            )

            record_activity(
                database=database,
                case_id=case.id,
                activity_type="case_assigned",
                description=(
                    f"Case {case.case_number} was assigned to "
                    f"{assignment_description}."
                ),
                actor=case.assigned_analyst or "System",
            )

        database.commit()
        database.refresh(case)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A case with this case number already exists."
            ),
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

    previous_analyst = case.assigned_analyst
    previous_team = case.responsible_team
    changed_fields = []

    for field_name, value in changes.items():
        if getattr(case, field_name) != value:
            changed_fields.append(field_name)

        setattr(case, field_name, value)

    assignment_changed = (
        "assigned_analyst" in changed_fields
        or "responsible_team" in changed_fields
    )

    if assignment_changed:
        if case.assigned_analyst or case.responsible_team:
            case.assigned_at = datetime.now()
        else:
            case.assigned_at = None

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

    if assignment_changed:
        previously_assigned = bool(
            previous_analyst or previous_team
        )

        currently_assigned = bool(
            case.assigned_analyst or case.responsible_team
        )

        if not currently_assigned:
            activity_type = "case_unassigned"
            assignment_description = (
                f"Case {case.case_number} assignment was cleared."
            )
            activity_actor = "System"
        else:
            assignment_parts = []

            if case.assigned_analyst:
                assignment_parts.append(
                    f"analyst {case.assigned_analyst}"
                )

            if case.responsible_team:
                assignment_parts.append(
                    f"team {case.responsible_team}"
                )

            assigned_to = " and ".join(assignment_parts)

            if previously_assigned:
                activity_type = "case_reassigned"
                assignment_description = (
                    f"Case {case.case_number} was reassigned to "
                    f"{assigned_to}."
                )
            else:
                activity_type = "case_assigned"
                assignment_description = (
                    f"Case {case.case_number} was assigned to "
                    f"{assigned_to}."
                )

            activity_actor = (
                case.assigned_analyst or "System"
            )

        record_activity(
            database=database,
            case_id=case.id,
            activity_type=activity_type,
            description=assignment_description,
            actor=activity_actor,
        )

    try:
        database.commit()
        database.refresh(case)
    except IntegrityError:
        database.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "A case with this case number already exists."
            ),
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
    "/cases/{case_id}/reviews",
    response_model=schemas.CaseReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_case_review(
    case_id: int,
    review_data: schemas.CaseReviewCreate,
    database: Session = Depends(get_db),
):
    case = get_case_or_404(case_id, database)

    if (
        review_data.next_review_date is not None
        and review_data.next_review_date < review_data.review_date
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "next_review_date cannot be earlier than "
                "review_date."
            ),
        )

    review = models.CaseReview(
        case_id=case_id,
        **review_data.model_dump(),
    )

    case.next_review_date = review_data.next_review_date

    database.add(review)

    if review_data.next_review_date is None:
        schedule_description = (
            "No next review date was scheduled."
        )
    else:
        schedule_description = (
            "The next review is scheduled for "
            f"{review_data.next_review_date.isoformat()}."
        )

    record_activity(
        database=database,
        case_id=case_id,
        activity_type="case_reviewed",
        description=(
            f"Case review completed by "
            f"{review_data.reviewed_by}. "
            f"{schedule_description}"
        ),
        actor=review_data.reviewed_by,
    )

    database.commit()
    database.refresh(review)

    return review


@app.get(
    "/cases/{case_id}/reviews",
    response_model=list[schemas.CaseReviewResponse],
)
def list_case_reviews(
    case_id: int,
    database: Session = Depends(get_db),
):
    get_case_or_404(case_id, database)

    statement = (
        select(models.CaseReview)
        .where(models.CaseReview.case_id == case_id)
        .order_by(
            models.CaseReview.review_date.desc(),
            models.CaseReview.id.desc(),
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