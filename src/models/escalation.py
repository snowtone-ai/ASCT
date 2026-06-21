from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import ModelMixin, enum_values

if TYPE_CHECKING:
    from src.models.event import Event


class EscalationTrigger(enum.StrEnum):
    LOW_CONFIDENCE = "low_confidence"
    NO_VIABLE_ACTION = "no_viable_action"
    AMBIGUOUS_RECOMMENDATION = "ambiguous_recommendation"


class EscalationPriority(enum.StrEnum):
    HIGH = "high"
    MEDIUM = "medium"


class EscalationStatus(enum.StrEnum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    OVERRIDDEN = "overridden"
    AUTO_EXPIRED = "auto_expired"


class EscalationRecord(ModelMixin, Base):
    __tablename__ = "escalation_records"

    trigger_type: Mapped[EscalationTrigger] = mapped_column(
        Enum(EscalationTrigger, values_callable=enum_values), nullable=False
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    scenarios_considered: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    priority: Mapped[EscalationPriority] = mapped_column(
        Enum(EscalationPriority, values_callable=enum_values), nullable=False
    )
    status: Mapped[EscalationStatus] = mapped_column(
        Enum(EscalationStatus, values_callable=enum_values),
        default=EscalationStatus.PENDING,
        nullable=False,
    )
    resolution: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(120), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    event: Mapped[Event] = relationship(back_populates="escalations")
