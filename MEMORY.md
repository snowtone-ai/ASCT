# MEMORY.md

## External Memory
State lives in files, independent of LLM memory.

## Files
- docs/vision.md: spec, success criteria, failure cases
- docs/state.md: current state, Write Lock, verification state
- docs/decisions.md: permanent decisions, Reference URLs, future review conditions
- docs/issues.md: failure log, Escalation, review timeout

## Rules
- Only mark work complete when state.md confirms it.
- Only assume a decision when decisions.md records it.
- Check issues.md before repeating a known-failed approach.
- After 3 consecutive failures, record in Escalation.
