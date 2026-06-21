from src.config.nl_parser import parse_japanese_config


def test_parse_priority_weight_from_japanese_text():
    result = parse_japanese_config("欠品を最優先にしてください")
    assert result["weights"]["stockout"] == 0.5


def test_parse_transport_priority_from_japanese_text():
    result = parse_japanese_config("輸送コストを最優先")
    assert result["weights"]["transport"] == 0.5


def test_parse_inventory_policy_numbers():
    result = parse_japanese_config("dairy は最低100個、最大300個にしてください")
    assert result["inventory_policies"]["dairy"]["reorder_point"] == 100
    assert result["inventory_policies"]["dairy"]["max_stock"] == 300
