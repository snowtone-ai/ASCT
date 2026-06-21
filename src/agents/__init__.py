from __future__ import annotations

import importlib
import pkgutil

from sqlalchemy.orm import Session

from src.agents.base import BaseAgent


class PluginRegistry:
    def __init__(self, session: Session):
        self.session = session
        self._agent_classes: list[type[BaseAgent]] = []

    def discover(self) -> list[type[BaseAgent]]:
        if self._agent_classes:
            return self._agent_classes
        package_name = __name__
        for module_info in pkgutil.iter_modules(__path__):
            if module_info.name == "base" or module_info.name.startswith("_"):
                continue
            module = importlib.import_module(f"{package_name}.{module_info.name}")
            self._agent_classes.extend(find_agent_classes(module))
        return self._agent_classes

    def get_agents_for_event(self, event_type: str) -> list[BaseAgent]:
        return [
            agent_class(self.session)
            for agent_class in self.discover()
            if event_type in agent_class.TRIGGERS
        ]


def find_agent_classes(module: object) -> list[type[BaseAgent]]:
    classes = []
    for item in vars(module).values():
        if isinstance(item, type) and issubclass(item, BaseAgent) and item is not BaseAgent:
            classes.append(item)
    return classes
