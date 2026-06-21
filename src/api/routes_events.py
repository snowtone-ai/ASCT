from fastapi import APIRouter

from src.api.deps import DbSession
from src.api.serializers import decision_to_dict, escalation_to_dict, event_to_dict
from src.config.loader import load_company_config
from src.models import Event, EventPriority, EventType
from src.orchestrator.run_composer import RunComposer

router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("")
def create_event(payload: dict, db: DbSession) -> dict:
    event = Event(
        event_type=EventType(payload["event_type"]),
        description=payload.get("description", payload["event_type"]),
        priority=EventPriority(payload.get("priority", "scheduled")),
        data=payload.get("data", {}),
        company_id=payload["company_id"],
    )
    db.add(event)
    db.flush()
    config = load_company_config(event.company_id)
    result = RunComposer(db).run(event, config)
    return {"event": event_to_dict(event), "result": serialize_result(result)}


def serialize_result(result) -> dict:
    if result.__class__.__name__ == "CEODecision":
        return {"type": "decision", "data": decision_to_dict(result)}
    return {"type": "escalation", "data": escalation_to_dict(result)}
