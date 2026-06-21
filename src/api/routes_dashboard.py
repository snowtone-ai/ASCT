from fastapi import APIRouter

from src.api.deps import DbSession
from src.api.serializers import decision_to_dict, escalation_to_dict, inventory_to_dict
from src.models import CEODecision, EscalationRecord, EscalationStatus, Event, Inventory

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/status")
def status(db: DbSession) -> dict:
    return {
        "inventory": [inventory_to_dict(row) for row in db.query(Inventory).limit(20)],
        "active_events": db.query(Event).count(),
        "recent_decisions": [
            decision_to_dict(row)
            for row in db.query(CEODecision).order_by(CEODecision.id.desc()).limit(10)
        ],
        "pending_escalations": [
            escalation_to_dict(row)
            for row in db.query(EscalationRecord).filter_by(status=EscalationStatus.PENDING)
        ],
    }
