from __future__ import annotations

from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from src.models import (
    EscalationPriority,
    EscalationRecord,
    EscalationStatus,
    EscalationTrigger,
    Event,
)


def create_escalation(
    session: Session,
    trigger_type: str,
    event: Event,
    scenarios: list[dict],
    config: dict,
) -> EscalationRecord:
    priority = (
        EscalationPriority.HIGH
        if event.priority.value == "emergency"
        else EscalationPriority.MEDIUM
    )
    escalation = EscalationRecord(
        trigger_type=EscalationTrigger(trigger_type),
        event=event,
        scenarios_considered=scenarios,
        priority=priority,
        status=EscalationStatus.PENDING,
    )
    session.add(escalation)
    session.flush()
    notify_slack(escalation, config)
    return escalation


def notify_slack(escalation: EscalationRecord, config: dict) -> None:
    webhook_url = config.get("escalation", {}).get("slack_webhook_url")
    if not webhook_url:
        return
    payload = {
        "text": (
            f"ASCT escalation: {escalation.trigger_type.value} "
            f"for event #{escalation.event_id}"
        )
    }
    try:
        httpx.post(webhook_url, json=payload, timeout=3.0)
    except httpx.HTTPError:
        return


def resolve_escalation(
    session: Session,
    escalation_id: int,
    resolution: dict,
    resolved_by: str,
) -> EscalationRecord:
    escalation = session.get(EscalationRecord, escalation_id)
    if escalation is None:
        raise ValueError(f"EscalationRecord not found: {escalation_id}")
    escalation.resolution = resolution
    escalation.resolved_by = resolved_by
    escalation.resolved_at = datetime.utcnow()
    escalation.status = EscalationStatus.RESOLVED
    session.flush()
    return escalation
