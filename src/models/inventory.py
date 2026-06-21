from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import ModelMixin

if TYPE_CHECKING:
    from src.models.company import Location
    from src.models.product import Product


class Inventory(ModelMixin, Base):
    __tablename__ = "inventory"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    product: Mapped[Product] = relationship(back_populates="inventory")
    location: Mapped[Location] = relationship(back_populates="inventory")


class InventoryPolicy(ModelMixin, Base):
    __tablename__ = "inventory_policies"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    reorder_point: Mapped[float] = mapped_column(Float, nullable=False)
    reorder_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    max_stock: Mapped[float] = mapped_column(Float, nullable=False)
    spoilage_rate_per_day: Mapped[float] = mapped_column(Float, nullable=False)

    product: Mapped[Product] = relationship(back_populates="inventory_policies")
    location: Mapped[Location] = relationship(back_populates="inventory_policies")


class SalesHistory(ModelMixin, Base):
    __tablename__ = "sales_history"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    location_id: Mapped[int] = mapped_column(ForeignKey("locations.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_sold: Mapped[float] = mapped_column(Float, nullable=False)
    revenue: Mapped[float] = mapped_column(Float, nullable=False)

    product: Mapped[Product] = relationship(back_populates="sales_history")
    location: Mapped[Location] = relationship(back_populates="sales_history")
