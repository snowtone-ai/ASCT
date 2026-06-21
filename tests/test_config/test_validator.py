from src.config.loader import load_company_config
from src.config.validator import validate_config


def test_valid_config_has_no_errors():
    assert validate_config(load_company_config(1)) == []


def test_weights_must_sum_to_one():
    config = load_company_config(1)
    config["weights"]["stockout"] = 0.99
    assert "weights must sum to 1.0" in validate_config(config)


def test_threshold_ranges_are_validated():
    config = load_company_config(1)
    config["constraints"]["min_confidence"] = 1.5
    errors = validate_config(config)
    assert "constraints.min_confidence must be between 0.0 and 1.0" in errors
