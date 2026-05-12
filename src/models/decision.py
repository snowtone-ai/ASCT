from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import ModelMixin

if TYPE_CHECKING:
    from src.models.event import Event


class AgentDecision(ModelMixin, Base):
    __tablename__ = "agent_decisions"

    agent_name: Mapped[str] = mapped_column(String(120), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    scenarios: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    selected_scenario: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    event: Mapped[Event] = relationship(back_populates="agent_decisions")


class CEODecision(ModelMixin, Base):
    __tablename__ = "ceo_decisions"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False)
    all_scenarios: Mapped[list[dict]] = mapped_column(JSON, nullable=False)
    selected_action: Mapped[dict] = mapped_column(JSON, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    causal_chain: Mapped[dict] = mapped_column(JSON, nullable=False)

    event: Mapped[Event] = relationship(back_populates="ceo_decisions")
