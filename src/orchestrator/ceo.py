from __future__ import annotations

from sqlalchemy.orm import Session

from src.models import CEODecision, EscalationRecord, Event
from src.orchestrator.escalation import create_escalation


class CEOOrchestrator:
    def __init__(self, session: Session):
        self.session = session

    def resolve(
        self, scenarios: list[dict], event: Event, config: dict
    ) -> CEODecision | EscalationRecord:
        if should_escalate_low_confidence(scenarios, event, config):
            return create_escalation(
                self.session, "low_confidence", event, scenarios, config
            )
        viable = [scenario for scenario in scenarios if check_constraints(scenario, config)]
        if not viable:
            return create_escalation(
                self.session, "no_viable_action", event, scenarios, config
            )
        ranked = sorted(viable, key=lambda item: score_scenario(item, config))
        if is_ambiguous(ranked, config):
            return create_escalation(
                self.session, "ambiguous_recommendation", event, ranked[:2], config
            )
        return create_decision(self.session, ranked[0], scenarios, event, config)


def score_scenario(scenario: dict, config: dict) -> float:
    weights = config["weights"]
    return round(
        weights["stockout"] * scenario["stockout_cost"]
        + weights["holding"] * scenario["holding_cost"]
        + weights["transport"] * scenario["transport_cost"],
        4,
    )


def check_constraints(scenario: dict, config: dict) -> bool:
    constraints = config["constraints"]
    if scenario["confidence"] < constraints["min_confidence"]:
        return False
    if scenario["total_cost"] > constraints["max_budget_jpy"]:
        return False
    return scenario["transport_cost"] <= constraints["max_transport_cost_jpy"]


def should_escalate_low_confidence(
    scenarios: list[dict], event: Event, config: dict
) -> bool:
    if event.priority.value != "emergency" or not scenarios:
        return False
    best_confidence = max(scenario["confidence"] for scenario in scenarios)
    return best_confidence < config["constraints"]["min_confidence"]


def is_ambiguous(ranked: list[dict], config: dict) -> bool:
    if len(ranked) < 2:
        return False
    threshold = config["escalation"]["ambiguity_threshold"]
    best = score_scenario(ranked[0], config)
    second = score_scenario(ranked[1], config)
    return abs(second - best) <= max(best, 1.0) * threshold


def create_decision(
    session: Session,
    selected: dict,
    all_scenarios: list[dict],
    event: Event,
    config: dict,
) -> CEODecision:
    decision = CEODecision(
        event=event,
        all_scenarios=all_scenarios,
        selected_action={"type": selected["name"], "source": "ceo"},
        score=score_scenario(selected, config),
        rationale="Lowest weighted scenario that satisfies constraints.",
        causal_chain={
            "event_id": event.id,
            "event_type": event.event_type.value,
            "selected_scenario": selected["name"],
        },
    )
    session.add(decision)
    session.flush()
    return decision
