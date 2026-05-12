import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column


class SourceType(enum.StrEnum):
    SENSOR = "sensor"
    API = "api"
    MANUAL = "manual"


def enum_values(enum_class: type[enum.Enum]) -> list[str]:
    return [member.value for member in enum_class]


class ModelMixin:
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    source: Mapped[SourceType] = mapped_column(
        Enum(SourceType, values_callable=enum_values), default=SourceType.MANUAL, nullable=False
    )
