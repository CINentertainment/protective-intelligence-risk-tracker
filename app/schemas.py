from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


CaseStatus = Literal["Open", "Monitoring", "Mitigated", "Closed"]
CasePriority = Literal["Routine", "Elevated", "High", "Critical"]
RiskLevel = Literal["Undetermined", "Low", "Moderate", "High", "Critical"]


class CaseBase(BaseModel):
    case_number: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1)
    status: CaseStatus = "Open"
    priority: CasePriority = "Routine"
    risk_level: RiskLevel = "Undetermined"
    opened_date: date = Field(default_factory=date.today)
    next_review_date: date | None = None


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
    summary: str | None = Field(default=None, min_length=1)
    status: CaseStatus | None = None
    priority: CasePriority | None = None
    risk_level: RiskLevel | None = None
    opened_date: date | None = None
    next_review_date: date | None = None


class CaseResponse(CaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime