# PostaHop — Project Charter

Owner: orchestrator · Last updated: 2026-10-11

## Vision
Plan, simulate and analyze packet logistics across a network of **nodes**
(hubs, depots, lockers) and **vehicles**, including **in-flight hops**: packets
transferred vehicle-to-vehicle at a rendezvous instead of only node-to-vehicle.

## Capabilities (initial scope)
1. Network model: nodes, vehicles, packets, routes, legs, transfers.
2. Routing optimization: assign packets to vehicles and sequences, with time
   windows, capacities and optional vehicle-to-vehicle transfers.
3. Geographic route analysis: travel time, distance, traffic-aware ETA, delay,
   route complexity, using Google Maps Platform (Routes API) or an alternative.
4. Simulation: replay/generate scenarios and compare strategies (with vs. without transfers).
5. Analytics: KPIs per scenario (on-time %, cost, distance, vehicles, transfers).

## Out of scope (until decided)
- Real-time driver apps, live GPS tracking, billing/payments.

## Fixed platforms
GitHub (VCS + Actions), Vercel, Supabase. See ADR-0001.

## Glossary
See `docs/GLOSSARY.md`.
