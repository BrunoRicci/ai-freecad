# PostaHop — Project Charter

Owner: orchestrator · Last updated: 2026-10-11

## Vision
Plan, simulate and analyze packet logistics across **nodes** (hubs, depots) and
**vehicles**, including **in-flight hops**: vehicle-to-vehicle transfers at a
rendezvous point, in addition to vehicle-to-node transfers.

## MVP goal
Validate feasibility and viability before building any product:
1. **Algorithms** — routing with node and vehicle-to-vehicle transfers.
2. **API** — submit scenario, get plan/ETAs, report delay → reroute.
3. **Financial viability** — cost per packet, break-even, hops vs node-only.
4. **Robustness** — delays, disruptions, reroutes.

MVP scale: 5,000 packets/day, ~100 vehicles, 20 nodes.

## Out of scope (MVP)
- End-user app or product UI (only a simple simulation results viewer).
- Live GPS tracking, driver apps, billing/payments.

## Stack
Python 3.12, FastAPI on Vercel, Supabase (Postgres + PostGIS), GitHub
(VCS, Actions, Issues, Projects). See ADR-0001, ADR-0002, ADR-0004.

## Glossary
See `docs/GLOSSARY.md`.
