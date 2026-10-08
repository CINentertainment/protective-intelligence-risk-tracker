from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Open",
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Routine",
    )

    risk_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Undetermined",
    )

    opened_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )

    next_review_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    assigned_analyst: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    responsible_team: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
        index=True,
    )

    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        index=True,
    )

    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    indicators: Mapped[list["Indicator"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    assessments: Mapped[
        list["RiskAssessment"]
    ] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    mitigation_actions: Mapped[
        list["MitigationAction"]
    ] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    activities: Mapped[
        list["CaseActivity"]
    ] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseActivity.created_at.desc()",
    )

    reviews: Mapped[
        list["CaseReview"]
    ] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseReview.review_date.desc()",
    )


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    indicator_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    source: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    credibility: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Unassessed",
    )

    observed_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    case: Mapped["Case"] = relationship(
        back_populates="indicators",
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    threat_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    vulnerability_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    impact_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    overall_risk: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    rationale: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    recommended_action: Mapped[
        str | None
    ] = mapped_column(
        Text,
        nullable=True,
    )

    assessed_by: Mapped[
        str | None
    ] = mapped_column(
        String(150),
        nullable=True,
    )

    assessment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    case: Mapped["Case"] = relationship(
        back_populates="assessments",
    )


class MitigationAction(Base):
    __tablename__ = "mitigation_actions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    owner: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    priority: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Moderate",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Planned",
    )

    due_date: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
    )

    completed_date: Mapped[
        date | None
    ] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    case: Mapped["Case"] = relationship(
        back_populates="mitigation_actions",
    )


class CaseActivity(Base):
    __tablename__ = "case_activities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    activity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    actor: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    case: Mapped["Case"] = relationship(
        back_populates="activities",
    )


class CaseReview(Base):
    __tablename__ = "case_reviews"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    case_id: Mapped[int] = mapped_column(
        ForeignKey(
            "cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    review_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today,
        index=True,
    )

    reviewed_by: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    findings: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    next_review_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    case: Mapped["Case"] = relationship(
        back_populates="reviews",
    )