from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, TypedDict

from sqlalchemy.orm import Session


class Scenario(TypedDict):
    name: str
    stockout_cost: float
    holding_cost: float
    transport_cost: float
    total_cost: float
    confidence: float


class BaseAgent(ABC):
    TRIGGERS: ClassVar[list[str]] = []

    def __init__(self, session: Session):
        self.session = session

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def evaluate(self, context: dict) -> list[Scenario]:
        raise NotImplementedError
