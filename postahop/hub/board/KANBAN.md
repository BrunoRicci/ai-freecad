---
kanban-plugin: basic
---

## Backlog

- [ ] PH-005 Code scaffold (web app + solver package) · @engineer · blocked-by: PH-001
- [ ] PH-006 Supabase project, PostGIS, migrations workflow · @engineer · blocked-by: PH-002
- [ ] PH-007 Vercel project, preview/prod envs, GitHub Actions CI · @engineer · blocked-by: PH-005
- [ ] PH-008 Simulation harness design (synthetic demand, fleet, traffic) · @algorithms · blocked-by: PH-003
- [ ] PH-009 Docs structure + glossary v1 · @docs-writer


## Ready

- [ ] PH-002 Domain model v1 (Node, Vehicle, Packet, Route, Leg, Hop) · @architect
- [ ] PH-003 Problem formulation: PDPTW with vehicle-to-vehicle transfers + literature review · @algorithms
- [ ] PH-004 Maps provider evaluation (Google Routes API, Route Optimization API, open-source engines): capabilities, pricing, ToS/caching · @algorithms


## In Progress

- [ ] PH-001 Confirm languages/runtime (ADR-0002) · @orchestrator · waiting on owner
- [ ] PH-010 Decide repo location (subfolder vs dedicated repo) · @orchestrator · waiting on owner


## Review



## Done

- [x] PH-000 Agent system + hub setup · @orchestrator · 2026-10-11


%% kanban:settings
```
{"kanban-plugin":"basic"}
```
%%

<!--
Card rules:
- One card = one owner agent, one outcome. Format:
  `- [ ] PH-### Title · @owner · blocked-by: PH-### · links`
- Acceptance criteria for non-trivial cards go in the linked doc or in the
  delegation prompt, and are copied to the card's output doc.
- Columns: Backlog → Ready → In Progress → Review → Done. Only the orchestrator
  moves cards to Done after verifying hub hygiene.
- This file is compatible with the Obsidian "Kanban" plugin (optional visual board).
-->
