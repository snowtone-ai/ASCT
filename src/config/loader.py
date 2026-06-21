from __future__ import annotations

from pathlib import Path

import yaml

from src.config.validator import validate_config

CONFIG_DIR = Path("configs")


def load_company_config(company_id: int) -> dict:
    path = CONFIG_DIR / f"company_{company_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Company config not found: {company_id}")
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = validate_config(config)
    if errors:
        raise ValueError("; ".join(errors))
    return config
