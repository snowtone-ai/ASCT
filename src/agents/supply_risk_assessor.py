from __future__ import annotations

from typing import ClassVar

from src.agents.base import BaseAgent, Scenario
from src.models import Event, Inventory, Supplier


class SupplyRiskAssessor(BaseAgent):
    TRIGGERS: ClassVar[list[str]] = ["supply_disruption", "weather_event"]

    def evaluate(self, context: dict) -> list[Scenario]:
        event: Event = context["event"]
        config: dict = context["config"]
        target = event.data.get("target")
        suppliers = query_suppliers(self.session, event.company_id, target)
        return [
            build_supplier_scenario(self.session, supplier, config)
            for supplier in suppliers[:2]
        ]


def query_suppliers(session, company_id: int, target: str | None) -> list[Supplier]:
    suppliers = session.query(Supplier).filter_by(company_id=company_id).all()
    if target:
        matching = [supplier for supplier in suppliers if target in supplier.products]
        return matching or suppliers
    return suppliers


def build_supplier_scenario(session, supplier: Supplier, config: dict) -> Scenario:
    reliability_gap = max(1.0 - supplier.reliability_score, 0.0)
    lead_limit = config["constraints"]["max_lead_time_hours"]
    lead_penalty = max(supplier.lead_time_hours - lead_limit, 0.0)
    inventory_value = estimate_inventory_value(session, supplier.company_id)
    stockout_cost = round(inventory_value * reliability_gap, 2)
    transport_cost = round(lead_penalty * 20000 + reliability_gap * 500000, 2)
    holding_cost = round(inventory_value * 0.01, 2)
    total_cost = round(stockout_cost + transport_cost + holding_cost, 2)
    confidence = round(min(max(supplier.reliability_score, 0.0), 1.0), 4)
    return {
        "name": f"assess_supply_{supplier.name}",
        "stockout_cost": stockout_cost,
        "holding_cost": holding_cost,
        "transport_cost": transport_cost,
        "total_cost": total_cost,
        "confidence": confidence,
    }


def estimate_inventory_value(session, company_id: int) -> float:
    rows = (
        session.query(Inventory)
        .join(Inventory.product)
        .filter_by(company_id=company_id)
        .limit(20)
        .all()
    )
    return sum(row.quantity * 1000 for row in rows)
