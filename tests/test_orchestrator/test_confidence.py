from src.orchestrator.confidence import calculate_confidence


def config():
    return {
        "confidence": {
            "staleness_half_life_hours": 12,
            "source_multipliers": {"sensor": 1.0, "api": 0.85, "manual": 0.65},
        }
    }


def test_fresh_data_has_high_confidence():
    score = calculate_confidence(0.95, 0, "sensor", 1.0, 0.95, config())
    assert score > 0.9


def test_stale_data_has_lower_confidence():
    fresh = calculate_confidence(0.95, 0, "sensor", 1.0, 0.95, config())
    stale = calculate_confidence(0.95, 24, "sensor", 1.0, 0.95, config())
    assert stale < fresh


def test_manual_source_penalty_applied():
    api = calculate_confidence(0.95, 0, "api", 1.0, 0.95, config())
    manual = calculate_confidence(0.95, 0, "manual", 1.0, 0.95, config())
    assert manual < api


def test_perishable_product_penalty_applied():
    durable = calculate_confidence(0.95, 0, "sensor", 1.0, 0.95, config())
    perishable = calculate_confidence(0.95, 0, "sensor", 0.8, 0.95, config())
    assert perishable < durable
