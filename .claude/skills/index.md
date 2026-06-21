# pm-zero v10 Skill Index -- ASCT

## Skill Loading
Read only the section needed. Each skill is self-contained.

## S1 /resume
Read state / decisions / issues. Identify restart point. Report current status.

## S2 /escape
On 3x failure: web-search a known fix and record the source URL in docs/issues.md (Self-Evolution).
If still unresolved, summarize in HANDOFF-JA.md and surface to the human.

## S3 /audit
Verify pm-zero knowledge / repo rules / official docs are current. Report staleness.

## S4 /reference
Find 3 real-world examples. Record in docs/decisions.md with adopted/avoided elements.

## S5 /ev
Self-Evolution: classify post-completion lessons into: Project-specific (stays in docs/issues.md) /
Always-applicable rule (one line in CLAUDE.md) / Reference-level lesson (docs/lessons.md) /
OS design issue (v10.x candidate, note in docs/decisions.md).

## S6 /env-guide
Decompose API key / OAuth / deploy setup into human-executable steps only.

## S7 /console-debug
Classify browser console / pageerror / network errors. Propose fix per category.

## S8 /verify
Select verification mode (quick / standard / final) and execute.

## S9 /context-update
Review CONTEXT.md. Add new domain terms appearing 3+ times. Prune obsolete terms.

## S10 /setup
Run scripts/setup.mjs. Verify directory structure. Report readiness.

## S11 /seed
Generate or regenerate seed data for ASCT.
1. Run `python -m src.seed.generate`
2. Verify row counts per table
3. Report: companies, locations, products, days of history

## S12 /agent-new
Scaffold a new ASCT agent.
1. Create src/agents/{name}.py from BaseAgent template
2. Define TRIGGERS, objective function, evaluate() method
3. Create tests/test_agents/test_{name}.py
4. Update CONTEXT.md with new agent definition
5. Verify: ruff check, pytest

## S13 /schema
Review or update SQL schema.
1. Read src/models/*.py
2. Compare with docs/vision.md checklist
3. Generate Alembic migration if needed: `alembic revision --autogenerate -m "description"`
4. Run: `alembic upgrade head`
5. Verify tables exist
