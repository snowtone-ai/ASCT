from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Enum, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import ModelMixin, enum_values

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.decision import AgentDecision, CEODecision
    from src.models.escalation import EscalationRecord


class EventType(enum.StrEnum):
    DEMAND_SPIKE = "demand_spike"
    SEASONAL_CHANGE = "seasonal_change"
    SUPPLY_DISRUPTION = "supply_disruption"
    WEATHER_EVENT = "weather_event"
    ROUTE_DISRUPTION = "route_disruption"
    INVENTORY_ALERT = "inventory_alert"
    REORDER_TRIGGER = "reorder_trigger"


class EventPriority(enum.StrEnum):
    SCHEDULED = "scheduled"
    EMERGENCY = "emergency"


class SignalType(enum.StrEnum):
    SUPPLY_GAP = "SupplyGap"
    DEMAND_SPIKE = "DemandSpike"
    ROUTE_DISRUPTION = "RouteDisruption"
    INVENTORY_ALERT = "InventoryAlert"
    SEASONAL_SHIFT = "SeasonalShift"


class Event(ModelMixin, Base):
    __tablename__ = "events"

    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, values_callable=enum_values), nullable=False
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    priority: Mapped[EventPriority] = mapped_column(
        Enum(EventPriority, values_callable=enum_values), nullable=False
    )
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    company: Mapped[Company] = relationship(back_populates="events")
    signals: Mapped[list[Signal]] = relationship(back_populates="event")
    agent_decisions: Mapped[list[AgentDecision]] = relationship(back_populates="event")
    ceo_decisions: Mapped[list[CEODecision]] = relationship(back_populates="event")
    escalations: Mapped[list[EscalationRecord]] = relationship(back_populates="event")


class Signal(ModelMixin, Base):
    __tablename__ = "signals"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    signal_type: Mapped[SignalType] = mapped_column(
        Enum(SignalType, values_callable=enum_values), nullable=False
    )
    dimension: Mapped[str] = mapped_column(String(80), nullable=False)
    delta: Mapped[float] = mapped_column(Float, nullable=False)
    target: Mapped[str] = mapped_column(String(160), nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    event: Mapped[Event] = relationship(back_populates="signals")
