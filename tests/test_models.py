from datetime import date

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import (
    AgentDecision,
    CEODecision,
    Company,
    EscalationPriority,
    EscalationRecord,
    EscalationTrigger,
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
from src.models.base import utc_now


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session_local = sessionmaker(bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def build_graph(session):
    company = Company(name="Freshfield Foods", industry="food", currency="JPY")
    origin = Location(name="Tokyo DC", type="warehouse", lat=35.0, lon=139.0, company=company)
    destination = Location(name="Osaka Plant", type="factory", lat=34.0, lon=135.0, company=company)
    product = Product(name="Dairy", category="dairy", unit="case", company=company)
    supplier = Supplier(
        name="Hokkaido Farms",
        products=["dairy"],
        reliability_score=0.92,
        lead_time_hours=24,
        company=company,
    )
    route = Route(origin=origin, destination=destination, distance_km=500, typical_hours=8)
    inventory = Inventory(
        product=product,
        location=origin,
        quantity=100,
        last_checked_at=utc_now(),
    )
    policy = InventoryPolicy(
        product=product,
        location=origin,
        reorder_point=40,
        reorder_quantity=80,
        max_stock=200,
        spoilage_rate_per_day=0.02,
    )
    sales = SalesHistory(
        product=product,
        location=origin,
        date=date.today(),
        quantity_sold=12,
        revenue=36000,
    )
    supply_event = Event(
        event_type=EventType.DEMAND_SPIKE,
        description="Demand spike in Tokyo",
        priority=EventPriority.EMERGENCY,
        data={"target": "dairy"},
        company=company,
    )
    signal = Signal(
        event=supply_event,
        signal_type=SignalType.DEMAND_SPIKE,
        dimension="demand",
        delta=0.3,
        target="dairy@Tokyo DC",
        duration_hours=24,
        confidence=0.9,
    )
    agent_decision = AgentDecision(
        agent_name="DemandForecaster",
        event=supply_event,
        scenarios=[{"name": "reorder"}],
        selected_scenario={"name": "reorder"},
        confidence=0.85,
    )
    ceo_decision = CEODecision(
        event=supply_event,
        all_scenarios=[{"name": "reorder"}],
        selected_action={"type": "reorder"},
        score=1000,
        rationale="Lowest weighted cost",
        causal_chain={"event": "DemandSpike"},
    )
    escalation = EscalationRecord(
        trigger_type=EscalationTrigger.AMBIGUOUS_RECOMMENDATION,
        event=supply_event,
        scenarios_considered=[{"name": "reorder"}],
        priority=EscalationPriority.HIGH,
    )
    session.add_all(
        [
            company,
            origin,
            destination,
            product,
            supplier,
            route,
            inventory,
            policy,
            sales,
            supply_event,
            signal,
            agent_decision,
            ceo_decision,
            escalation,
        ]
    )
    session.commit()
    return company


def test_create_and_query_all_models(session):
    build_graph(session)

    assert session.query(Company).count() == 1
    assert session.query(Location).count() == 2
    assert session.query(Route).count() == 1
    assert session.query(Product).count() == 1
    assert session.query(Supplier).count() == 1
    assert session.query(Inventory).count() == 1
    assert session.query(InventoryPolicy).count() == 1
    assert session.query(SalesHistory).count() == 1
    assert session.query(Event).count() == 1
    assert session.query(Signal).count() == 1
    assert session.query(AgentDecision).count() == 1
    assert session.query(CEODecision).count() == 1
    assert session.query(EscalationRecord).count() == 1


def test_all_models_have_shared_columns():
    models = [
        Company,
        Location,
        Route,
        Product,
        Supplier,
        Inventory,
        InventoryPolicy,
        SalesHistory,
        Event,
        Signal,
        AgentDecision,
        CEODecision,
        EscalationRecord,
    ]

    for model in models:
        column_names = set(model.__table__.columns.keys())
        assert {"id", "created_at", "updated_at", "source"} <= column_names


def test_foreign_key_constraints_work(session):
    invalid = Product(name="Invalid", category="dairy", unit="case", company_id=999)
    session.add(invalid)

    with pytest.raises(IntegrityError):
        session.commit()
