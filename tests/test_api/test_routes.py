from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.deps import get_db
from src.database import Base
from src.main import app
from src.models import Event
from src.seed.generate import generate_seed


def make_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    generate_seed(session)

    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    return TestClient(app), session


def test_health_endpoint():
    client, _session = make_client()
    assert client.get("/health").json() == {"status": "ok"}


def test_dashboard_status_endpoint():
    client, _session = make_client()
    response = client.get("/api/dashboard/status")
    assert response.status_code == 200
    assert "inventory" in response.json()


def test_event_ingest_triggers_run():
    client, _session = make_client()
    response = client.post(
        "/api/events",
        json={
            "company_id": 1,
            "event_type": "supply_disruption",
            "priority": "emergency",
            "data": {"target": "dairy"},
        },
    )
    assert response.status_code == 200
    assert response.json()["result"]["type"] in {"decision", "escalation"}


def test_decision_endpoints():
    client, session = make_client()
    event_row = session.query(Event).filter_by(event_type="supply_disruption").first()
    client.post(
        "/api/events",
        json={
            "company_id": event_row.company_id,
            "event_type": event_row.event_type.value,
            "priority": event_row.priority.value,
            "data": event_row.data,
        },
    )
    rows = client.get("/api/decisions").json()
    assert rows
    assert client.get(f"/api/decisions/{rows[0]['id']}").status_code == 200


def test_config_parse_endpoint():
    client, _session = make_client()
    response = client.post("/api/config/parse-nl", json={"text": "欠品を最優先"})
    assert response.json()["weights"]["stockout"] == 0.5
