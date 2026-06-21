from src.config.loader import load_company_config


def test_load_company_config_returns_valid_yaml():
    config = load_company_config(1)
    assert config["company"]["name"] == "Freshfield Foods"
    assert config["weights"]["stockout"] == 0.45
