import yaml
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import CEODecision, Event
from src.orchestrator.run_composer import RunComposer
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
        config = yaml.safe_load(file)
    config["escalation"]["ambiguity_threshold"] = 0.0
    return config


def test_correct_agents_selected_for_event_type():
    session = seeded_session()
    event_row = session.query(Event).filter_by(event_type="demand_spike").first()
    agents = RunComposer(session).registry.get_agents_for_event(event_row.event_type.value)
    assert {agent.name for agent in agents} == {"DemandForecaster", "InventoryOptimizer"}


def test_emergency_events_processed_immediately():
    session = seeded_session()
    event_row = session.query(Event).filter_by(event_type="demand_spike").first()
    result = RunComposer(session).run(event_row, load_config())
    assert result.id is not None


def test_end_to_end_event_to_decision():
    session = seeded_session()
    event_row = session.query(Event).filter_by(event_type="supply_disruption").first()
    result = RunComposer(session).run(event_row, load_config())
    assert isinstance(result, CEODecision)
    assert result.causal_chain["event_id"] == event_row.id
