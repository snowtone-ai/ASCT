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

## D-006: Event Priority — Scheduled vs Emergency
- Date: 2026-05-12
- Target: architecture
- Decision: **Deferred to Phase 1 (CodeX)** — design gap identified at scaffold stage
- Problem: Current architecture treats all events equally via EventIngestor. No distinction between:
  - **定期更新 (Scheduled)**: reorder_trigger, daily inventory check → can wait, batch OK
  - **緊急時 (Emergency)**: supply_disruption, weather_event → must preempt, immediate processing
- Required design for Phase 1:
  - Add `priority: "scheduled" | "emergency"` field to Event model
  - RunComposer: emergency events skip queue and run immediately
  - Scheduled events: triggered by Alembic-compatible cron-style job or API endpoint called by external scheduler
  - Emergency escalation path: if confidence < min_threshold AND priority = "emergency" → human notification (log + flag, no auto-action)
- Rejected: Single queue with no priority (current implicit design) — risk of emergency events waiting behind scheduled batch jobs
- Future review condition: If event volume exceeds 100/day, consider separate queues or async processing.

## Future Changes
- Async agent execution if scale demands it (D-001 review condition)
- React frontend if complex interactivity needed (D-002 review condition)
- LLM-powered NL parser as paid feature (D-003 review condition)
