# CONTEXT.md -- ASCT Domain Vocabulary

## Purpose
Shared domain language consumed by all skills and agents.
Reduces token usage by establishing common terms once.

## Project Terms
- ASCT: Agentic Supply Chain Twin. The system being built.
- Seed Data: Pre-generated realistic sample data for 2 companies, 3 locations each, 5 product types, 30 days of sales history.
- Company Config: Per-company YAML configuration defining weights, constraints, thresholds, and policies.

## Architecture Terms
- TypedSignal: A data point with type, dimension, target, delta, duration, and confidence. Example: SupplyGap(dimension="volume", delta=-0.10, target="SupplierA", confidence=0.95).
- CausalChain: The traceable path Event → Signal → Agent Scenario → CEO Decision.
- Scenario: An agent's proposed action with shape: {name, stockout_cost, holding_cost, transport_cost, total_cost, confidence}.
- BaseAgent: Abstract base class. Each agent implements evaluate(context) -> list[Scenario].
- TRIGGERS: Class attribute on agents declaring which event types activate them.
- RunComposer: Maps incoming events to relevant agents via TRIGGERS, executes synchronously.
- CEOOrchestrator: Scores all agent scenarios with weighted formula, applies constraints, selects optimal action.
- ConfidenceScore: Dynamic value = base × staleness_factor × source_factor × perishability_factor × historical_accuracy. All parameters from config.
- EventIngestor: API endpoint or scheduled check that receives external events and triggers agent runs.
- PluginRegistry: Auto-discovery mechanism in src/agents/__init__.py that loads all agent modules.

## Agent Terms
- DemandForecaster: Agent minimizing stockout risk. Triggers: demand_spike, seasonal_change.
- SupplyRiskAssessor: Agent minimizing supply disruption cost. Triggers: supply_disruption, weather_event.
- InventoryOptimizer: Agent minimizing holding cost with stockout prevention constraint. Triggers: inventory_alert, demand_spike.
- LogisticsPlanner: Agent minimizing transport cost. Triggers: route_disruption, reorder_trigger.

## Data Source Types
- sensor: Automated data from IoT/systems. Highest confidence bonus.
- api: Data from external APIs. Standard confidence.
- manual: Human-entered data. Confidence penalty applied.

## User-Facing Terms
- 欠品リスク (Stockout Risk): Risk of inventory dropping below minimum policy level.
- 保管コスト (Holding Cost): Cost of maintaining excess inventory.
- 輸送コスト (Transport Cost): Logistics and shipping costs.
- 信頼度 (Confidence): Dynamic score indicating data/decision reliability.
- 因果チェーン (Causal Chain): Japanese term for CausalChain shown in UI.

## Update Rules
- Add terms when a new domain concept appears 3+ times in conversation.
- Keep definitions under 20 words each.
- Review and prune after each major feature completion.
