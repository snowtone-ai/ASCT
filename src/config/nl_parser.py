from __future__ import annotations

import re

WEIGHT_KEYWORDS = {
    "欠品": "stockout",
    "輸送コスト": "transport",
    "保管コスト": "holding",
}


def parse_japanese_config(text: str) -> dict:
    updates: dict = {}
    weight = parse_weight_update(text)
    if weight:
        updates.setdefault("weights", {}).update(weight)
    policy = parse_inventory_policy(text)
    if policy:
        updates.setdefault("inventory_policies", {}).update(policy)
    return updates


def parse_weight_update(text: str) -> dict[str, float]:
    for keyword, key in WEIGHT_KEYWORDS.items():
        if keyword in text and "最優先" in text:
            return rebalance_weights(key)
    return {}


def rebalance_weights(priority_key: str) -> dict[str, float]:
    weights = {"stockout": 0.25, "holding": 0.25, "transport": 0.25}
    weights[priority_key] = 0.5
    return weights


def parse_inventory_policy(text: str) -> dict:
    product = parse_product_name(text)
    values = {}
    minimum = re.search(r"最低\s*(\d+)\s*個", text)
    maximum = re.search(r"最大\s*(\d+)\s*個", text)
    if minimum:
        values["reorder_point"] = int(minimum.group(1))
    if maximum:
        values["max_stock"] = int(maximum.group(1))
    return {product: values} if product and values else {}


def parse_product_name(text: str) -> str | None:
    match = re.search(r"([A-Za-z_]+)", text)
    if match:
        return match.group(1)
    return None
