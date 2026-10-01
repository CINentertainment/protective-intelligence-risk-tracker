from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CaseStatus = Literal[
    "Open",
    "Monitoring",
    "Mitigated",
    "Closed",
]

CasePriority = Literal[
    "Routine",
    "Elevated",
    "High",
    "Critical",
]

RiskLevel = Literal[
    "Undetermined",
    "Low",
    "Moderate",
    "High",
    "Critical",
]

CredibilityLevel = Literal[
    "Unassessed",
    "Low",
    "Moderate",
    "High",
    "Confirmed",
]

AssessmentLevel = Literal[
    "Low",
    "Moderate",
    "High",
    "Critical",
]

MitigationStatus = Literal[
    "Planned",
    "In Progress",
    "Completed",
    "Cancelled",
]

MitigationPriority = Literal[
    "Low",
    "Moderate",
    "High",
    "Critical",
]


class CaseBase(BaseModel):
    case_number: str = Field(
        min_length=1,
        max_length=50,
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    summary: str = Field(
        min_length=1,
    )

    status: CaseStatus = "Open"
    priority: CasePriority = "Routine"
    risk_level: RiskLevel = "Undetermined"
    opened_date: date = Field(default_factory=date.today)
    next_review_date: date | None = None

    assigned_analyst: str | None = Field(
        default=None,
        max_length=150,
    )

    responsible_team: str | None = Field(
        default=None,
        max_length=150,
    )


class CaseCreate(CaseBase):
    pass


class CaseUpdate(BaseModel):
    case_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    summary: str | None = Field(
        default=None,
        min_length=1,
    )

    status: CaseStatus | None = None
    priority: CasePriority | None = None
    risk_level: RiskLevel | None = None
    opened_date: date | None = None
    next_review_date: date | None = None

    assigned_analyst: str | None = Field(
        default=None,
        max_length=150,
    )

    responsible_team: str | None = Field(
        default=None,
        max_length=150,
    )


class CaseResponse(CaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_archived: bool
    archived_at: datetime | None
    assigned_at: datetime | None
    created_at: datetime
    updated_at: datetime


class IndicatorBase(BaseModel):
    indicator_type: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str = Field(
        min_length=1,
    )

    source: str | None = Field(
        default=None,
        max_length=200,
    )

    credibility: CredibilityLevel = "Unassessed"
    observed_date: date = Field(default_factory=date.today)


class IndicatorCreate(IndicatorBase):
    pass


class IndicatorResponse(IndicatorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    created_at: datetime


class RiskAssessmentBase(BaseModel):
    threat_level: AssessmentLevel
    vulnerability_level: AssessmentLevel
    impact_level: AssessmentLevel
    overall_risk: AssessmentLevel

    rationale: str = Field(
        min_length=1,
    )

    recommended_action: str | None = None

    assessed_by: str | None = Field(
        default=None,
        max_length=150,
    )

    assessment_date: date = Field(default_factory=date.today)


class RiskAssessmentCreate(RiskAssessmentBase):
    pass


class RiskAssessmentResponse(RiskAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    created_at: datetime


class MitigationActionBase(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str = Field(
        min_length=1,
    )

    owner: str | None = Field(
        default=None,
        max_length=150,
    )

    priority: MitigationPriority = "Moderate"
    status: MitigationStatus = "Planned"
    due_date: date | None = None
    completed_date: date | None = None


class MitigationActionCreate(MitigationActionBase):
    pass


class MitigationActionUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    owner: str | None = Field(
        default=None,
        max_length=150,
    )

    priority: MitigationPriority | None = None
    status: MitigationStatus | None = None
    due_date: date | None = None
    completed_date: date | None = None


class MitigationActionResponse(MitigationActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    created_at: datetime
    updated_at: datetime


class CaseActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: int
    activity_type: str
    description: str
    actor: str | None
    created_at: datetime


class CaseDetailResponse(CaseResponse):
    indicators: list[IndicatorResponse] = Field(
        default_factory=list
    )

    assessments: list[RiskAssessmentResponse] = Field(
        default_factory=list
    )

    mitigation_actions: list[MitigationActionResponse] = Field(
        default_factory=list
    )

    activities: list[CaseActivityResponse] = Field(
        default_factory=list
    )