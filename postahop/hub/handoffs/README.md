# Handoffs

Agent-to-agent requests. One file per handoff: `H-YYYYMMDD-##-from-to-topic.md`.
The orchestrator routes open handoffs to the addressee. Only the addressee closes
a handoff (set `Status: Closed` + resolution). Closed handoffs stay for history.

## Template

```markdown
# H-YYYYMMDD-## Short title
- From: <agent> · To: <agent> · Card: PH-###
- Status: Open | Closed
- Priority: low | normal | high

## Request
What is needed and why.

## Context
Links to hub files, ADRs, code.

## Expected output
Which files should be created/updated.

## Resolution
(filled by addressee when closing)
```
