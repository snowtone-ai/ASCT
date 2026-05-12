from fastapi import APIRouter, HTTPException

from src.api.deps import DbSession
from src.models import Company

router = APIRouter(prefix="/api/companies", tags=["companies"])


@router.get("")
def list_companies(db: DbSession) -> list[dict]:
    return [{"id": row.id, "name": row.name, "industry": row.industry} for row in db.query(Company)]


@router.post("")
def create_company(payload: dict, db: DbSession) -> dict:
    company = Company(
        name=payload["name"],
        industry=payload.get("industry", "unknown"),
        currency=payload.get("currency", "JPY"),
    )
    db.add(company)
    db.commit()
    return {"id": company.id, "name": company.name}


@router.get("/{company_id}")
def get_company(company_id: int, db: DbSession) -> dict:
    company = db.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail="company not found")
    return {"id": company.id, "name": company.name, "industry": company.industry}
