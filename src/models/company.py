from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import ModelMixin

if TYPE_CHECKING:
    from src.models.event import Event
    from src.models.inventory import Inventory, InventoryPolicy, SalesHistory
    from src.models.product import Product, Supplier


class Company(ModelMixin, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    industry: Mapped[str] = mapped_column(String(80), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    locations: Mapped[list[Location]] = relationship(back_populates="company")
    products: Mapped[list[Product]] = relationship(back_populates="company")
    suppliers: Mapped[list[Supplier]] = relationship(back_populates="company")
    events: Mapped[list[Event]] = relationship(back_populates="company")


class Location(ModelMixin, Base):
    __tablename__ = "locations"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    company: Mapped[Company] = relationship(back_populates="locations")
    inventory: Mapped[list[Inventory]] = relationship(back_populates="location")
    inventory_policies: Mapped[list[InventoryPolicy]] = relationship(back_populates="location")
    sales_history: Mapped[list[SalesHistory]] = relationship(back_populates="location")
    outgoing_routes: Mapped[list[Route]] = relationship(
        back_populates="origin", foreign_keys="Route.origin_id"
    )
    incoming_routes: Mapped[list[Route]] = relationship(
        back_populates="destination", foreign_keys="Route.destination_id"
    )


class Route(ModelMixin, Base):
    __tablename__ = "routes"

    origin_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    destination_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    typical_hours: Mapped[float] = mapped_column(Float, nullable=False)

    origin: Mapped[Location] = relationship(
        back_populates="outgoing_routes", foreign_keys=[origin_id]
    )
    destination: Mapped[Location] = relationship(
        back_populates="incoming_routes", foreign_keys=[destination_id]
    )
