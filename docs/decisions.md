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

## D-006: pm-zero v10 Migration
- Date: 2026-06-21
- Target: governance / tooling
- Decision: Migrate the repository's governance and meta files from pm-zero v9.2 to v10 (Autonomous Solo-Dev OS).
- Adoption reason: v10 removes the multi-vendor assumption (Claude Code only), makes CLAUDE.md the single primary directive, assumes context compaction at ~40-50% (file-based durability), and adds allow-by-default autonomy with a deterministic deny-set guard. Aligns ASCT with the latest knowledge base (pm-zero-knowledge-v10.md).
- Changes:
  - Removed: AGENTS.md, .codex/, OS-KERNEL.md, REPO-GUIDE.md, .mcp.json, MEMORY.md.
  - Added: tasks.md (execution ledger), docs/repo-map.md, .claude/hooks/guard.mjs.
  - Rewrote: CLAUDE.md, .claude/settings.json, docs/state.md, docs/issues.md, HANDOFF-JA.md.
  - Kept: docs/vision.md, docs/decisions.md, CONTEXT.md (valid v10 optional domain-vocabulary file), scripts/*, .env.example, .gitignore.
- Non-obvious permission boundary: .claude/settings.json uses defaultMode "dontAsk" with allow-by-default safe ops and a PreToolUse guard.mjs that blocks the dangerous set (force-push, reset --hard, destructive DB ops, unscoped rm -rf, secret reads). CLAUDE_AUTOCOMPACT_PCT_OVERRIDE is set to 50 per the v10 compaction design target.
- Future review condition: Re-review when pm-zero knowledge advances past v10, or after major Claude Code/model releases (verify setting keys against current docs).

## Future Changes
- Async agent execution if scale demands it (D-001 review condition)
- React frontend if complex interactivity needed (D-002 review condition)
- LLM-powered NL parser as paid feature (D-003 review condition)
