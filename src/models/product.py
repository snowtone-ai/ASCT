from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.base import ModelMixin

if TYPE_CHECKING:
    from src.models.company import Company
    from src.models.inventory import Inventory, InventoryPolicy, SalesHistory


class Product(ModelMixin, Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    unit: Mapped[str] = mapped_column(String(40), nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    company: Mapped[Company] = relationship(back_populates="products")
    inventory: Mapped[list[Inventory]] = relationship(back_populates="product")
    inventory_policies: Mapped[list[InventoryPolicy]] = relationship(back_populates="product")
    sales_history: Mapped[list[SalesHistory]] = relationship(back_populates="product")


class Supplier(ModelMixin, Base):
    __tablename__ = "suppliers"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    products: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    reliability_score: Mapped[float] = mapped_column(Float, nullable=False)
    lead_time_hours: Mapped[float] = mapped_column(Float, nullable=False)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)

    company: Mapped[Company] = relationship(back_populates="suppliers")
