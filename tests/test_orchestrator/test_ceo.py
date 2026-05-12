from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import CEODecision, EscalationRecord, Event
from src.orchestrator.ceo import CEOOrchestrator, check_constraints, score_scenario
from src.seed.generate import generate_seed


def session_and_event():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    generate_seed(session)
    event_row = session.query(Event).filter_by(event_type="demand_spike").first()
    return session, event_row


def config():
    return {
        "weights": {"stockout": 0.5, "holding": 0.2, "transport": 0.3},
        "constraints": {
            "min_confidence": 0.6,
            "max_budget_jpy": 100000,
            "max_transport_cost_jpy": 50000,
        },
        "escalation": {"ambiguity_threshold": 0.01, "slack_webhook_url": ""},
    }


def scenario(name, stockout, holding, transport, confidence=0.9):
    total = stockout + holding + transport
    return {
        "name": name,
        "stockout_cost": stockout,
        "holding_cost": holding,
        "transport_cost": transport,
        "total_cost": total,
        "confidence": confidence,
    }


def test_scoring_formula_matches_expected_output():
    assert score_scenario(scenario("a", 100, 50, 20), config()) == 66.0


def test_constraint_violation_disqualifies_scenario():
    bad = scenario("bad", 10, 10, 90000)
    assert not check_constraints(bad, config())


def test_best_scenario_selected_correctly():
    session, event_row = session_and_event()
    result = CEOOrchestrator(session).resolve(
        [scenario("expensive", 100, 0, 0), scenario("cheap", 10, 0, 0)],
        event_row,
        config(),
    )
    assert isinstance(result, CEODecision)
    assert result.selected_action["type"] == "cheap"


def test_all_disqualified_creates_escalation():
    session, event_row = session_and_event()
    result = CEOOrchestrator(session).resolve(
        [scenario("bad", 200000, 0, 0, confidence=0.9)],
        event_row,
        config(),
    )
    assert isinstance(result, EscalationRecord)
    assert result.trigger_type.value == "no_viable_action"


def test_ambiguous_scores_create_escalation():
    session, event_row = session_and_event()
    result = CEOOrchestrator(session).resolve(
        [scenario("a", 100, 0, 0), scenario("b", 101, 0, 0)],
        event_row,
        config(),
    )
    assert isinstance(result, EscalationRecord)
    assert result.trigger_type.value == "ambiguous_recommendation"
