from __future__ import annotations

from typing import ClassVar

from src.agents.base import BaseAgent, Scenario
from src.models import Event, Inventory, Route


class LogisticsPlanner(BaseAgent):
    TRIGGERS: ClassVar[list[str]] = ["route_disruption", "reorder_trigger"]

    def evaluate(self, context: dict) -> list[Scenario]:
        event: Event = context["event"]
        routes = query_routes(self.session, event.company_id)
        return [build_route_scenario(self.session, route, event) for route in routes[:2]]


def query_routes(session, company_id: int) -> list[Route]:
    return (
        session.query(Route)
        .join(Route.origin)
        .filter_by(company_id=company_id)
        .order_by(Route.typical_hours)
        .all()
    )


def build_route_scenario(session, route: Route, event: Event) -> Scenario:
    delay_hours = float(event.data.get("delay_hours", 6.0))
    disrupted = event.event_type.value == "route_disruption"
    delay_multiplier = 1.0 + (delay_hours / max(route.typical_hours, 1.0) if disrupted else 0.0)
    transport_cost = round(route.distance_km * 180 * delay_multiplier, 2)
    stockout_cost = round(estimate_delay_risk(session, route) * delay_hours, 2)
    holding_cost = 0.0
    total_cost = round(stockout_cost + holding_cost + transport_cost, 2)
    confidence = round(max(0.55, 0.92 - delay_hours * 0.02), 4)
    return {
        "name": f"route_{route.origin.name}_to_{route.destination.name}",
        "stockout_cost": stockout_cost,
        "holding_cost": holding_cost,
        "transport_cost": transport_cost,
        "total_cost": total_cost,
        "confidence": confidence,
    }


def estimate_delay_risk(session, route: Route) -> float:
    rows = (
        session.query(Inventory)
        .filter_by(location_id=route.destination_id)
        .order_by(Inventory.quantity)
        .limit(5)
        .all()
    )
    return sum(max(100 - row.quantity, 0) * 250 for row in rows)
