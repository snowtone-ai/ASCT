import yaml
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.agents import PluginRegistry
from src.agents.logistics_planner import LogisticsPlanner
from src.database import Base
from src.models import Event
from src.seed.generate import generate_seed


def seeded_session():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    generate_seed(session)
    return session


def load_config():
    with open("configs/company_1.yaml", encoding="utf-8") as file:
        return yaml.safe_load(file)


def test_triggers_contains_expected_event_types():
    assert LogisticsPlanner.TRIGGERS == ["route_disruption", "reorder_trigger"]


def test_agent_discovered_by_plugin_registry():
    session = seeded_session()
    agents = PluginRegistry(session).get_agents_for_event("route_disruption")
    assert any(agent.name == "LogisticsPlanner" for agent in agents)


def test_returns_valid_scenarios():
    session = seeded_session()
    event_row = session.query(Event).filter_by(event_type="reorder_trigger").first()
    scenarios = LogisticsPlanner(session).evaluate({"event": event_row, "config": load_config()})

    assert scenarios
    for scenario in scenarios:
        assert scenario["stockout_cost"] >= 0
        assert scenario["holding_cost"] >= 0
        assert scenario["transport_cost"] >= 0
        assert scenario["total_cost"] >= 0
        assert 0.0 <= scenario["confidence"] <= 1.0
