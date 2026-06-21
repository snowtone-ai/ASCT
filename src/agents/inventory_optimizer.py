from __future__ import annotations

from typing import ClassVar

from src.agents.base import BaseAgent, Scenario
from src.models import Event, Inventory, InventoryPolicy


class InventoryOptimizer(BaseAgent):
    TRIGGERS: ClassVar[list[str]] = ["inventory_alert", "demand_spike"]

    def evaluate(self, context: dict) -> list[Scenario]:
        event: Event = context["event"]
        target = event.data.get("target")
        policies = query_policies(self.session, event.company_id, target)
        return [build_inventory_scenario(self.session, policy) for policy in policies[:2]]


def query_policies(session, company_id: int, target: str | None) -> list[InventoryPolicy]:
    query = session.query(InventoryPolicy).join(InventoryPolicy.product)
    query = query.filter_by(company_id=company_id)
    if target:
        query = query.filter_by(category=target)
    return query.order_by(InventoryPolicy.reorder_point.desc()).all()


def build_inventory_scenario(session, policy: InventoryPolicy) -> Scenario:
    inventory = query_inventory(session, policy)
    shortage = max(policy.reorder_point - inventory.quantity, 0.0)
    excess = max(inventory.quantity - policy.max_stock, 0.0)
    reorder_units = policy.reorder_quantity if shortage > 0 else 0.0
    stockout_cost = round(shortage * 1800, 2)
    holding_cost = round(excess * 150, 2)
    transport_cost = round(reorder_units * 35, 2)
    action = "reorder" if shortage > 0 else "rebalance"
    total_cost = round(stockout_cost + holding_cost + transport_cost, 2)
    return {
        "name": f"{action}_{policy.product.category}_{policy.location.name}",
        "stockout_cost": stockout_cost,
        "holding_cost": holding_cost,
        "transport_cost": transport_cost,
        "total_cost": total_cost,
        "confidence": inventory_confidence(inventory, policy),
    }


def query_inventory(session, policy: InventoryPolicy) -> Inventory:
    return (
        session.query(Inventory)
        .filter_by(product_id=policy.product_id, location_id=policy.location_id)
        .one()
    )


def inventory_confidence(inventory: Inventory, policy: InventoryPolicy) -> float:
    ratio = min(inventory.quantity / max(policy.max_stock, 1.0), 1.0)
    confidence = 0.7 + ratio * 0.2
    return round(min(max(confidence, 0.0), 1.0), 4)
