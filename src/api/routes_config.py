from fastapi import APIRouter, HTTPException

from src.config.loader import load_company_config
from src.config.nl_parser import parse_japanese_config
from src.config.validator import validate_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/{company_id}")
def get_config(company_id: int) -> dict:
    return load_company_config(company_id)


@router.put("/{company_id}")
def validate_company_config(company_id: int, payload: dict) -> dict:
    errors = validate_config(payload)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    return {"company_id": company_id, "status": "valid"}


@router.post("/parse-nl")
def parse_nl(payload: dict) -> dict:
    return parse_japanese_config(payload.get("text", ""))
