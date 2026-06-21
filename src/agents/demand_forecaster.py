from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import ClassVar

from sqlalchemy import func

from src.agents.base import BaseAgent, Scenario
from src.models import Event, Inventory, InventoryPolicy, SalesHistory
from src.orchestrator.confidence import calculate_confidence


class DemandForecaster(BaseAgent):
    TRIGGERS: ClassVar[list[str]] = ["demand_spike", "seasonal_change"]

    def evaluate(self, context: dict) -> list[Scenario]:
        event: Event = context["event"]
        config: dict = context["config"]
        target = event.data.get("target")
        policies = query_policies(self.session, event.company_id, target)
        scenarios = [self.build_scenario(policy, config) for policy in policies]
        return scenarios[:2]

    def build_scenario(self, policy: InventoryPolicy, config: dict) -> Scenario:
        recent, previous = sales_windows(self.session, policy)
        trend = (recent - previous) / max(previous, 1.0)
        inventory = query_inventory(self.session, policy)
        gap = max(policy.reorder_point - inventory.quantity, 0.0)
        trend_pressure = max(trend, 0.0) * max(recent, 1.0)
        stockout_cost = round((gap + trend_pressure) * 1500, 2)
        holding_cost = round(max(inventory.quantity - policy.max_stock, 0.0) * 120, 2)
        confidence = calculate_policy_confidence(policy, inventory, config)
        return {
            "name": f"forecast_{policy.product.category}_{policy.location.name}",
            "stockout_cost": stockout_cost,
            "holding_cost": holding_cost,
            "transport_cost": 0.0,
            "total_cost": round(stockout_cost + holding_cost, 2),
            "confidence": confidence,
        }


def query_policies(session, company_id: int, target: str | None) -> list[InventoryPolicy]:
    query = session.query(InventoryPolicy).join(InventoryPolicy.product)
    query = query.filter_by(company_id=company_id)
    if target:
        query = query.filter_by(category=target)
    return query.limit(5).all()


def sales_windows(session, policy: InventoryPolicy) -> tuple[float, float]:
    today = date(2026, 5, 12)
    recent_start = today - timedelta(days=6)
    previous_start = today - timedelta(days=13)
    recent = sales_sum(session, policy, recent_start, today)
    previous = sales_sum(session, policy, previous_start, recent_start)
    return recent, previous


def sales_sum(session, policy: InventoryPolicy, start: date, end: date) -> float:
    value = (
        session.query(func.coalesce(func.sum(SalesHistory.quantity_sold), 0.0))
        .filter(
            SalesHistory.product_id == policy.product_id,
            SalesHistory.location_id == policy.location_id,
            SalesHistory.date >= start,
            SalesHistory.date < end,
        )
        .scalar()
    )
    return float(value)


def query_inventory(session, policy: InventoryPolicy) -> Inventory:
    return (
        session.query(Inventory)
        .filter_by(product_id=policy.product_id, location_id=policy.location_id)
        .one()
    )


def calculate_policy_confidence(
    policy: InventoryPolicy, inventory: Inventory, config: dict
) -> float:
    age = (datetime(2026, 5, 12, 12, 0) - inventory.last_checked_at).total_seconds() / 3600
    perishability = 1.0 - min(policy.spoilage_rate_per_day * 2, 0.25)
    return calculate_confidence(0.95, age, inventory.source.value, perishability, 0.9, config)
