from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import EscalationStatus, Event
from src.orchestrator import escalation as module
from src.orchestrator.escalation import create_escalation, resolve_escalation
from src.seed.generate import generate_seed


def session_and_event():
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    generate_seed(session)
    event_row = session.query(Event).first()
    return session, event_row


def config(webhook=""):
    return {"escalation": {"slack_webhook_url": webhook}}


def test_escalation_record_created_with_correct_fields():
    session, event_row = session_and_event()
    escalation = create_escalation(
        session, "no_viable_action", event_row, [{"name": "x"}], config()
    )
    assert escalation.status == EscalationStatus.PENDING
    assert escalation.scenarios_considered == [{"name": "x"}]


def test_slack_webhook_called_when_configured(monkeypatch):
    calls = []
    monkeypatch.setattr(module.httpx, "post", lambda *args, **kwargs: calls.append(args))
    session, event_row = session_and_event()
    create_escalation(session, "no_viable_action", event_row, [], config("https://example.test"))
    assert calls


def test_slack_webhook_failure_is_silent(monkeypatch):
    def fail(*_args, **_kwargs):
        raise module.httpx.HTTPError("network")

    monkeypatch.setattr(module.httpx, "post", fail)
    session, event_row = session_and_event()
    create_escalation(session, "no_viable_action", event_row, [], config("https://example.test"))


def test_escalation_resolution_updates_status():
    session, event_row = session_and_event()
    escalation = create_escalation(session, "no_viable_action", event_row, [], config())
    resolved = resolve_escalation(session, escalation.id, {"action": "approve"}, "ops")
    assert resolved.status == EscalationStatus.RESOLVED
    assert resolved.resolved_by == "ops"
