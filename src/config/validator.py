from __future__ import annotations

REQUIRED_KEYS = {
    "company",
    "weights",
    "constraints",
    "confidence",
    "escalation",
    "scheduling",
    "inventory_policies",
    "locations",
    "suppliers",
}


def validate_config(config: dict) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_KEYS - set(config)
    if missing:
        errors.append(f"missing required keys: {', '.join(sorted(missing))}")
        return errors
    errors.extend(validate_weights(config["weights"]))
    errors.extend(validate_constraints(config["constraints"]))
    errors.extend(validate_confidence(config["confidence"]))
    return errors


def validate_weights(weights: dict) -> list[str]:
    errors = []
    required = {"stockout", "holding", "transport"}
    if required - set(weights):
        errors.append("weights must include stockout, holding, transport")
    total = sum(float(weights.get(key, 0)) for key in required)
    if abs(total - 1.0) > 0.0001:
        errors.append("weights must sum to 1.0")
    return errors


def validate_constraints(constraints: dict) -> list[str]:
    errors = []
    min_confidence = constraints.get("min_confidence")
    if min_confidence is None or not 0.0 <= min_confidence <= 1.0:
        errors.append("constraints.min_confidence must be between 0.0 and 1.0")
    for key in ("max_budget_jpy", "max_transport_cost_jpy"):
        if constraints.get(key, 0) <= 0:
            errors.append(f"constraints.{key} must be positive")
    return errors


def validate_confidence(confidence: dict) -> list[str]:
    errors = []
    for key in ("min_confidence_threshold", "high_confidence_threshold"):
        value = confidence.get(key)
        if value is None or not 0.0 <= value <= 1.0:
            errors.append(f"confidence.{key} must be between 0.0 and 1.0")
    if confidence.get("staleness_half_life_hours", 0) <= 0:
        errors.append("confidence.staleness_half_life_hours must be positive")
    return errors
