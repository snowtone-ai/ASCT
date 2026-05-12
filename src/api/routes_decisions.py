from fastapi import APIRouter, HTTPException

from src.api.deps import DbSession
from src.api.serializers import decision_to_dict
from src.models import CEODecision

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


@router.get("")
def list_decisions(db: DbSession) -> list[dict]:
    rows = db.query(CEODecision).order_by(CEODecision.id.desc()).all()
    return [decision_to_dict(row) for row in rows]


@router.get("/{decision_id}")
def get_decision(decision_id: int, db: DbSession) -> dict:
    decision = db.get(CEODecision, decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="decision not found")
    return decision_to_dict(decision)
