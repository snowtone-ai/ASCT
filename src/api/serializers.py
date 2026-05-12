from src.models import CEODecision, EscalationRecord, Event, Inventory


def event_to_dict(event: Event) -> dict:
    return {
        "id": event.id,
        "event_type": event.event_type.value,
        "priority": event.priority.value,
        "description": event.description,
        "company_id": event.company_id,
        "data": event.data,
    }


def decision_to_dict(decision: CEODecision) -> dict:
    return {
        "id": decision.id,
        "event_id": decision.event_id,
        "selected_action": decision.selected_action,
        "score": decision.score,
        "rationale": decision.rationale,
        "causal_chain": decision.causal_chain,
    }


def escalation_to_dict(escalation: EscalationRecord) -> dict:
    return {
        "id": escalation.id,
        "event_id": escalation.event_id,
        "trigger_type": escalation.trigger_type.value,
        "priority": escalation.priority.value,
        "status": escalation.status.value,
        "resolution": escalation.resolution,
    }


def inventory_to_dict(inventory: Inventory) -> dict:
    return {
        "product": inventory.product.category,
        "location": inventory.location.name,
        "quantity": inventory.quantity,
    }
