from fastapi import APIRouter, HTTPException

from src.api.deps import DbSession
from src.api.serializers import escalation_to_dict
from src.models import EscalationRecord, EscalationStatus
from src.orchestrator.escalation import resolve_escalation

router = APIRouter(prefix="/api/escalations", tags=["escalations"])


@router.get("/pending")
def list_pending(db: DbSession) -> list[dict]:
    rows = db.query(EscalationRecord).filter_by(status=EscalationStatus.PENDING).all()
    return [escalation_to_dict(row) for row in rows]


@router.put("/{escalation_id}/resolve")
def resolve(escalation_id: int, payload: dict, db: DbSession) -> dict:
    try:
        row = resolve_escalation(
            db,
            escalation_id,
            payload.get("resolution", {}),
            payload.get("resolved_by", "human"),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    return escalation_to_dict(row)
