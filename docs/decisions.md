# decisions.md

## D-001: Agent Architecture Pattern
- Date: 2026-05-12
- Target: architecture
- Decision: Synchronous Plugin Registry with Event-Triggered Runs (Hybrid)
- Adoption reason: Highest success rate (92%). Balances simplicity (sync execution, deterministic debugging) with event-driven responsiveness. Plugin auto-discovery enables zero-change agent addition.
- Reference examples:
  - Mesa (Python agent-based modeling) -- adopted: agent registry pattern, step-based execution
  - CrewAI multi-agent pattern -- adopted: role-based agent design with explicit objectives
  - LangGraph orchestration -- avoided: async graph complexity excessive for MVP scope
- Rejected alternatives:
  - Skeleton A (sync + polling): Real-time responsiveness too low (success rate 88%)
  - Skeleton B (async event-driven): asyncio complexity disproportionate for MVP (success rate 72%)
- Future review condition: If agent count exceeds 8 or latency exceeds 2s, reconsider async execution.

## D-002: Frontend Selection
- Date: 2026-05-12
- Target: UI
- Decision: Streamlit
- Adoption reason: Python-only stack, zero-cost, fastest iteration for dashboard-style UI. FastAPI REST API remains frontend-agnostic for future migration.
- Rejected alternatives:
  - React + Vite: Higher UI flexibility but adds JS toolchain complexity and development overhead.
- Future review condition: If complex interactive UI requirements emerge (drag-drop, real-time charts with sub-second updates), reconsider React.

## D-003: Natural Language Config Parser
- Date: 2026-05-12
- Target: architecture
- Decision: Rule-based Japanese keyword extraction (no LLM)
- Adoption reason: Zero-cost constraint. Japanese domain keywords ("欠品", "輸送コスト", "最優先") map to config keys via dictionary. Templates cover common patterns.
- Rejected alternatives:
  - LLM-powered parsing: Higher accuracy but violates zero-cost constraint.
- Future review condition: If user feedback indicates rule-based parser is too limiting, add LLM option as paid tier.

## D-004: Seed Data Industries
- Date: 2026-05-12
- Target: data
- Decision: Food company (perishability) + Electronics company (lead time)
- Adoption reason: Contrasting characteristics test confidence degradation (perishability penalty) and different inventory policy patterns. Demonstrates system flexibility.
- Future review condition: None (seed data is fixed).

## D-005: Confidence Calculation Design
- Date: 2026-05-12
- Target: architecture
- Decision: Config-driven formula with multiplicative penalties
- Adoption reason: base_confidence × staleness_factor × source_factor × perishability_factor × historical_accuracy. All parameters in company YAML config. No hardcoding.
- Future review condition: If real-world data shows multiplicative model is too aggressive, consider additive scoring.

## D-006: Dual Time Horizon (Strategic + Emergency)
- Date: 2026-05-12
- Target: architecture
- Decision: Two planning layers run in parallel over the same agent codebase
- Adoption reason: Supply chain planning inherently operates on multiple time scales. Kinaxis RapidResponse's "concurrent planning" demonstrates that strategic and tactical planning must happen simultaneously, not sequentially. Blue Yonder's demand sensing shows real-time signal processing is essential for modern supply chains.
- Design:
  - **Strategic Layer** (scheduled, daily/weekly): DemandForecaster + InventoryOptimizer. Triggered by API endpoint or external scheduler. Low urgency — queued for review/batch.
  - **Emergency Layer** (event-driven, real-time): All agents + CEO fast loop. Triggered when Signal confidence ≥ threshold. High urgency — immediate execution or human escalation.
  - Event model: add `priority: "scheduled" | "emergency"` field
  - RunComposer: emergency events bypass queue and execute immediately
  - Escalation: if confidence < min_threshold AND priority = "emergency" → human notification (log + flag, no auto-action)
- Reference examples:
  - Kinaxis RapidResponse -- adopted: concurrent planning model (strategic + tactical simultaneously)
  - Blue Yonder demand sensing -- adopted: real-time signal processing with AI agents as "Digital Colleagues"
  - SAP IBP S&OP -- avoided: batch-only planning cycle too slow for emergency response
- Rejected alternatives:
  - Single queue with no priority: emergency events wait behind scheduled batch jobs (unsafe)
  - Separate codebases per layer: violates DRY, doubles maintenance cost
- Implementation: Phase 1 (Event model) + Phase 3 (agent trigger logic). CodeX implements.
- Future review condition: If event volume exceeds 100/day, consider separate queues or async processing.

## D-007: Ontology Taxonomy (Palantir-inspired)
- Date: 2026-05-12
- Target: architecture
- Decision: 3 primitive types (Asset, Location, Event) + 2 derived types (Signal, Action)
- Adoption reason: Palantir Foundry's ontology-first approach — "define what objects mean before touching data." Having formal object taxonomy prevents the data model from becoming an ad-hoc collection of tables. Every table maps to a known ontology type, every relationship is semantically meaningful.
- Design:
  - Primitives map to SQL: Asset → products/inventory, Location → companies/locations, Event → events table
  - Signal types: SupplyGap, DemandSpike, RouteDisruption, InventoryAlert, SeasonalShift
  - Action: the output of CEO Orchestrator, stored with full causal chain
  - Every Signal carries confidence (0.0–1.0), every table carries source ("sensor"|"manual"|"api")
- Reference examples:
  - Palantir Foundry Ontology -- adopted: Objects with typed properties, Links between objects, Actions as first-class concept
  - Palantir AIP (2024-2026) -- noted: Ontology as backbone for enterprise AI agents (validates our agent-per-object-type approach)
  - Domain-Driven Design (Evans) -- adopted: Ubiquitous Language principle (our CONTEXT.md)
- Rejected alternatives:
  - Flat table design with no taxonomy: works initially but makes agent-to-data mapping ambiguous at scale
  - Full graph ontology (RDF/OWL): excessive complexity for MVP; SQLAlchemy relationships are sufficient
- Future review condition: If object types exceed 15, consider a formal ontology definition language.

## D-008: Four Specialist Agents (not Three)
- Date: 2026-05-12
- Target: architecture
- Decision: 4 Tier-1 agents: DemandForecaster, SupplyRiskAssessor, InventoryOptimizer, LogisticsPlanner
- Adoption reason: Supply risk and logistics risk are fundamentally different domains. A factory fire at a supplier (supply risk) requires different analysis than a typhoon blocking a delivery route (logistics). Merging them violates Principle 4 (Intentional Conflict) by creating an agent with conflicting sub-objectives.
- Design:
  - DemandForecaster: min stockout_cost. Triggers: demand_spike, seasonal_change
  - SupplyRiskAssessor: min supply_disruption_cost. Triggers: supply_disruption, weather_event
  - InventoryOptimizer: min (stockout_cost + holding_cost). Triggers: inventory_alert, demand_spike
  - LogisticsPlanner: min (transport_cost + delivery_risk). Triggers: route_disruption, reorder_trigger
  - CEO Orchestrator (Tier 2): weighted scoring across all scenarios
- Evaluated skeletons:
  - Skeleton A (3 agents — merge SupplyRisk + Logistics): Simpler but supply disruption and route optimization require different data, different SQL queries, different escalation paths. Success rate: 78%.
  - Skeleton B (4 agents — current): Clean separation of concerns. Each agent has single objective. Success rate: 90%.
  - Skeleton C (5+ agents — add PricingAgent, QualityAgent): Over-engineering for MVP. Agents can be added later via plugin registry with zero code change. Success rate: 75%.
- Selected: Skeleton B (4 agents).
- Future review condition: Add new agents only when a new objective function is needed that existing agents cannot represent. Plugin registry makes addition zero-cost.

## D-009: Human Escalation Design
- Date: 2026-05-12
- Target: architecture
- Decision: DB-backed escalation with API polling endpoint (no external notification service)
- Adoption reason: Zero-cost constraint eliminates push notification services (Twilio, SendGrid). DB + REST API provides full escalation lifecycle while allowing external systems to poll. Streamlit dashboard displays pending escalations natively.
- Design:
  - **3 triggers**: low_confidence (signal below threshold + emergency), no_viable_action (all scenarios disqualified), ambiguous_recommendation (top scores within threshold)
  - **State machine**: pending → acknowledged → resolved/overridden/auto_expired
  - **Data model**: EscalationRecord with trigger_type, event_id, scenarios_considered, status, resolution, resolved_by
  - **API**: `GET /api/escalations/pending` for external system integration
  - **Fail-safe**: auto_expired escalations take no action; system never acts autonomously when uncertain
- Evaluated skeletons:
  - Skeleton A (log-only): No API, relies on dashboard viewing. Success rate: 80%.
  - Skeleton B (DB + API polling): Zero-cost, extensible, external integration via polling. Success rate: 92%.
  - Skeleton C (DB + webhook push): Requires external service configuration. Success rate: 75%.
- Selected: Skeleton B (DB + API polling).
- Reference examples:
  - PagerDuty incident model -- adopted: escalation state machine (triggered → acknowledged → resolved)
  - Palantir AIP human-in-the-loop -- adopted: AI proposes, human approves for high-stakes decisions
- Rejected alternatives:
  - Webhook push notifications: violates zero-cost constraint, adds external service dependency
  - Email notifications: requires SMTP configuration, not self-contained
- Future review condition: If response time SLA requires push notification, add optional webhook URL in company config.

## D-010: Slack Notification for Escalations
- Date: 2026-05-12
- Target: notification
- Decision: Optional Slack Incoming Webhook, configured per company
- Adoption reason: Slack Incoming Webhooks are free (zero-cost maintained). Optional config field means system works without it. Push notification solves the "human must be watching dashboard" problem without adding mandatory external dependencies.
- Design:
  - Company config field: `escalation.slack_webhook_url` (empty string = disabled)
  - On escalation creation: if URL configured, POST JSON payload with trigger_type, event summary, top scenarios, dashboard link
  - On POST failure: log warning, continue silently (DB + dashboard still work)
  - Message format: simple Slack Block Kit with severity color coding
- Rejected alternatives:
  - Slack Bot API: OAuth complexity, bot management overhead for MVP
  - Multi-service abstraction (Slack + Teams + email): premature abstraction for single notification channel
- Future review condition: If Teams/email notifications needed, extract notification interface and add adapters.

## D-011: Phase 1 Relational Schema Examples
- Date: 2026-05-12
- Target: DB
- Decision: Implement SQLAlchemy ORM tables for the Phase 1 ontology with integer primary keys, explicit foreign keys, JSON scenario/action payloads, and shared provenance columns.
- Grounding examples:
  - Freshfield Foods demand spike: Company → Tokyo Distribution Center → dairy Product → Inventory/InventoryPolicy → demand_spike Event → DemandSpike Signal → AgentDecision/CEODecision.
  - NexTech route disruption: Company → Yokohama Main Warehouse and Nagoya Assembly Plant Locations → Route → route_disruption Event → RouteDisruption Signal.
  - Human escalation: emergency Event → multiple scenario JSON payloads → EscalationRecord with ambiguous_recommendation, pending status, optional resolution.
- Adoption reason: Preserves ontology traceability (Event → Signal → Scenario → Action) while keeping Phase 1 limited to schema and migration only.
- Future review condition: Add uniqueness constraints after seed data and API write paths reveal the natural keys.

## Future Changes
- Async agent execution if scale demands it (D-001 review condition)
- React frontend if complex interactivity needed (D-002 review condition)
- LLM-powered NL parser as paid feature (D-003 review condition)
- Separate event queues if volume > 100/day (D-006 review condition)
- Formal ontology language if types > 15 (D-007 review condition)
