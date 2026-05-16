from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy.orm import Session

from src.database import Base, SessionLocal, engine
from src.models import (
    AgentDecision,
    CEODecision,
    Company,
    EscalationRecord,
    Event,
    EventPriority,
    EventType,
    Inventory,
    InventoryPolicy,
    Location,
    Product,
    Route,
    SalesHistory,
    Signal,
    SignalType,
    Supplier,
)

CONFIG_PATHS = (Path("configs/company_1.yaml"), Path("configs/company_2.yaml"))
RANDOM_SEED = 42
BASE_DATE = date(2026, 5, 12)
PRODUCT_UNITS = {
    "food": "case",
    "electronics": "unit",
}


def load_configs(paths: tuple[Path, ...] = CONFIG_PATHS) -> list[dict[str, Any]]:
    return [yaml.safe_load(path.read_text(encoding="utf-8")) for path in paths]


def reset_seed_data(session: Session) -> None:
    for model in (
        Signal,
        AgentDecision,
        CEODecision,
        EscalationRecord,
        Event,
        SalesHistory,
        InventoryPolicy,
        Inventory,
        Route,
        Supplier,
        Product,
        Location,
        Company,
    ):
        session.query(model).delete()
    session.commit()
    session.expunge_all()


def generate_seed(session: Session, configs: list[dict[str, Any]] | None = None) -> None:
    rng = random.Random(RANDOM_SEED)
    reset_seed_data(session)
    for config in configs or load_configs():
        company = create_company(session, config)
        locations = create_locations(session, company, config)
        products = create_products(session, company, config)
        create_suppliers(session, company, config)
        create_routes(session, locations)
        create_inventory_and_sales(session, rng, company, locations, products, config)
        create_events(session, company, config)
    session.commit()


def create_company(session: Session, config: dict[str, Any]) -> Company:
    company_data = config["company"]
    company = Company(
        name=company_data["name"],
        industry=company_data["industry"],
        currency=company_data["currency"],
    )
    session.add(company)
    session.flush()
    return company


def create_locations(
    session: Session, company: Company, config: dict[str, Any]
) -> list[Location]:
    locations = [
        Location(
            company=company,
            name=item["name"],
            type=item["type"],
            lat=item["lat"],
            lon=item["lon"],
        )
        for item in config["locations"]
    ]
    session.add_all(locations)
    session.flush()
    return locations


def create_products(
    session: Session, company: Company, config: dict[str, Any]
) -> dict[str, Product]:
    unit = PRODUCT_UNITS.get(company.industry, "unit")
    products = {
        category: Product(
            company=company,
            name=category.replace("_", " ").title(),
            category=category,
            unit=unit,
        )
        for category in config["inventory_policies"]
    }
    session.add_all(products.values())
    session.flush()
    return products


def create_suppliers(session: Session, company: Company, config: dict[str, Any]) -> None:
    session.add_all(
        Supplier(
            company=company,
            name=item["name"],
            products=item["products"],
            reliability_score=item["reliability_score"],
            lead_time_hours=item["lead_time_hours"],
        )
        for item in config["suppliers"]
    )


def create_routes(session: Session, locations: list[Location]) -> None:
    routes = []
    for index, origin in enumerate(locations):
        destination = locations[(index + 1) % len(locations)]
        routes.append(
            Route(
                origin=origin,
                destination=destination,
                distance_km=round(350 + index * 180.5, 1),
                typical_hours=round(6 + index * 3.5, 1),
            )
        )
    session.add_all(routes)


def create_inventory_and_sales(
    session: Session,
    rng: random.Random,
    company: Company,
    locations: list[Location],
    products: dict[str, Product],
    config: dict[str, Any],
) -> None:
    for category, policy in config["inventory_policies"].items():
        daily_base = 80 if company.industry == "food" else 18
        daily_base += len(category) % 9
        for location in locations:
            create_product_location_rows(
                session, rng, products[category], location, policy, daily_base
            )


def create_product_location_rows(
    session: Session,
    rng: random.Random,
    product: Product,
    location: Location,
    policy: dict[str, Any],
    daily_base: float,
) -> None:
    total_sold = 0.0
    for offset in range(30):
        sales_date = BASE_DATE - timedelta(days=29 - offset)
        weekend_factor = 0.75 if sales_date.weekday() >= 5 else 1.0
        noise = rng.uniform(0.85, 1.15)
        quantity = round(daily_base * weekend_factor * noise, 2)
        total_sold += quantity
        session.add(
            SalesHistory(
                product=product,
                location=location,
                date=sales_date,
                quantity_sold=quantity,
                revenue=round(quantity * unit_price(product.category), 2),
            )
        )
    avg_daily = total_sold / 30
    session.add(
        InventoryPolicy(
            product=product,
            location=location,
            reorder_point=round(avg_daily * policy["reorder_point_days"], 2),
            reorder_quantity=round(avg_daily * policy["reorder_quantity_days"], 2),
            max_stock=round(avg_daily * policy["max_stock_days"], 2),
            spoilage_rate_per_day=policy["spoilage_rate_per_day"],
        )
    )
    current_quantity = max(avg_daily * policy["reorder_quantity_days"] - total_sold * 0.05, 0)
    session.add(
        Inventory(
            product=product,
            location=location,
            quantity=round(current_quantity, 2),
            last_checked_at=datetime(2026, 5, 12, 9, 0),
        )
    )


def unit_price(category: str) -> float:
    if category in {"semiconductors", "display_modules", "battery_cells"}:
        return 12000.0
    if category in {"passive_components", "connectors"}:
        return 800.0
    return 450.0


def create_events(session: Session, company: Company, config: dict[str, Any]) -> None:
    categories = list(config["inventory_policies"])
    specs = [
        (EventType.DEMAND_SPIKE, EventPriority.EMERGENCY, SignalType.DEMAND_SPIKE, 0.3),
        (EventType.SEASONAL_CHANGE, EventPriority.SCHEDULED, SignalType.SEASONAL_SHIFT, 0.15),
        (EventType.SUPPLY_DISRUPTION, EventPriority.EMERGENCY, SignalType.SUPPLY_GAP, -0.2),
        (EventType.WEATHER_EVENT, EventPriority.EMERGENCY, SignalType.ROUTE_DISRUPTION, 8.0),
        (EventType.INVENTORY_ALERT, EventPriority.SCHEDULED, SignalType.INVENTORY_ALERT, -50.0),
        (EventType.REORDER_TRIGGER, EventPriority.SCHEDULED, SignalType.INVENTORY_ALERT, -20.0),
    ]
    for index, (event_type, priority, signal_type, delta) in enumerate(specs):
        target = categories[index % len(categories)]
        event = Event(
            company=company,
            event_type=event_type,
            description=f"{company.name}: {event_type.value} for {target}",
            priority=priority,
            data={"target": target},
        )
        session.add(event)
        session.flush()
        session.add(
            Signal(
                event=event,
                signal_type=signal_type,
                dimension="demand" if "demand" in signal_type.value else "quantity",
                delta=delta,
                target=target,
                duration_hours=24 + index * 4,
                confidence=round(0.9 - index * 0.04, 2),
            )
        )


def main() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        generate_seed(session)


if __name__ == "__main__":
    main()
