from __future__ import annotations


def calculate_confidence(
    base: float,
    data_age_hours: float,
    source: str,
    perishability_factor: float,
    historical_accuracy: float,
    config: dict,
) -> float:
    confidence_config = config["confidence"]
    half_life_hours = confidence_config["staleness_half_life_hours"]
    staleness_factor = 0.5 ** (data_age_hours / half_life_hours)
    source_multiplier = confidence_config["source_multipliers"].get(source, 0.7)
    score = (
        base
        * staleness_factor
        * source_multiplier
        * perishability_factor
        * historical_accuracy
    )
    return round(min(max(score, 0.0), 1.0), 4)
