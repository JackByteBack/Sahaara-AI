"""Database models — schema mirrors ai/database-schema-sql.md and build/tech-specs.md §2."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import JSONType, Base


class UTCDateTime(TypeDecorator):
    """SQLite returns naive datetimes; normalize everything to UTC-aware."""
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(self, value, dialect):
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Feature 1.11 — role-based access: admin / operator / supervisor / counsellor."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), default="")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="operator"
    )  # admin | operator | supervisor | counsellor
    language: Mapped[str] = mapped_column(String(8), default="en")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=_now)


class Case(Base):
    """Feature 1.7 — case management lifecycle + AI analysis artifacts."""

    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    case_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )  # active | reviewing | referred | closed
    created_by: Mapped[str | None] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)

    # Feature 1.4 — operational queue score (never a clinical measure)
    review_priority_score: Mapped[float] = mapped_column(Float, default=0.0)
    # Feature 2.5 — safety override flag beats the weighted score
    safety_override: Mapped[bool] = mapped_column(Boolean, default=False)
    safety_override_reason: Mapped[str] = mapped_column(Text, default="")

    # Feature 1.5 — explainable AI flags (indicator, evidence, excerpt, ts, confidence, source)
    ai_flags: Mapped[list] = mapped_column(JSONType, default=list)
    # Feature 2.2 — Victim Safety & Wellbeing Profile (multidimensional)
    victim_safety_profile: Mapped[dict] = mapped_column(JSONType, default=dict)
    # Feature 2.10 — uncertainty-aware assessment
    uncertainty: Mapped[dict] = mapped_column(JSONType, default=dict)
    # Feature 1.3 / 2.9 — detected language + code-switching info
    language_info: Mapped[dict] = mapped_column(JSONType, default=dict)

    transcript: Mapped[list] = mapped_column(JSONType, default=list)  # segments w/ timestamps
    # Feature 1.9 — structured summary separating person's words vs AI inference
    summary: Mapped[dict] = mapped_column(JSONType, default=dict)
    # Feature 1.6 — final human decision (AI never decides autonomously)
    final_decision: Mapped[dict | None] = mapped_column(JSONType, nullable=True)

    consent: Mapped[dict] = mapped_column(JSONType, default=dict)  # Feature 1.7 consent info
    notes: Mapped[list] = mapped_column(JSONType, default=list)
    followups: Mapped[list] = mapped_column(JSONType, default=list)  # Feature 2.17 longitudinal
    # Ops — case assignment workflow (supervisor assigns, audit-logged)
    assigned_to: Mapped[str | None] = mapped_column(
        String(32), ForeignKey("users.id"), nullable=True, default=None
    )
    session_mode: Mapped[str] = mapped_column(String(20), default="text")  # voice | text | demo
    trauma_mode: Mapped[bool] = mapped_column(Boolean, default=False)  # Feature 2.13
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)  # Feature 1.15
    anonymized: Mapped[bool] = mapped_column(Boolean, default=False)  # Feature 1.10
    assessment_confidence: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime, default=_now, onupdate=_now)

    referrals = relationship("Referral", back_populates="case", cascade="all, delete-orphan")
    audits = relationship("AuditLog", back_populates="case", cascade="all, delete-orphan")
    assignee = relationship("User", primaryjoin="Case.assigned_to == User.id", viewonly=True)


class Referral(Base):
    """Feature 1.8 / 2.16 — human-confirmed support & intervention pathways."""

    __tablename__ = "referrals"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(String(32), ForeignKey("cases.id", ondelete="CASCADE"))
    referral_type: Mapped[str] = mapped_column(String(50))  # counselling | medical | legal_aid | ...
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | confirmed | completed
    ai_suggested: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str | None] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    confirmed_by: Mapped[str | None] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime, default=_now)

    case = relationship("Case", back_populates="referrals")


class AuditLog(Base):
    """Feature 1.13 — auditability of login, access, AI analysis, changes, escalation, export, deletion."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    case_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("cases.id"), nullable=True)
    user_id: Mapped[str | None] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str] = mapped_column(Text, default="")
    timestamp: Mapped[datetime] = mapped_column(UTCDateTime, default=_now, index=True)

    case = relationship("Case", back_populates="audits")


class RateLimit(Base):
    """Persistent counter for API rate limiting on session start."""

    __tablename__ = "rate_limits"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    count: Mapped[int] = mapped_column(Integer, default=0)
    window_start: Mapped[datetime] = mapped_column(UTCDateTime, default=_now)
