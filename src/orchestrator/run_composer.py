from __future__ import annotations

from sqlalchemy.orm import Session

from src.agents import PluginRegistry
from src.models import Event
from src.orchestrator.ceo import CEOOrchestrator
from src.orchestrator.escalation import create_escalation


class RunComposer:
    def __init__(self, session: Session):
        self.session = session
        self.registry = PluginRegistry(session)
        self.ceo = CEOOrchestrator(session)

    def run(self, event: Event, config: dict):
        agents = self.registry.get_agents_for_event(event.event_type.value)
        scenarios = []
        for agent in agents:
            scenarios.extend(agent.evaluate({"event": event, "config": config}))
        if not scenarios:
            return create_escalation(
                self.session, "no_viable_action", event, scenarios, config
            )
        result = self.ceo.resolve(scenarios, event, config)
        self.session.commit()
        return result
