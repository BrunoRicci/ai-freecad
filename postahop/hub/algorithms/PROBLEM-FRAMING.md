# Problem Framing (v1)

Owner: algorithms · Status: DRAFT seeded by orchestrator · Issue: PH-003

## MVP scale (owner, 2026-10-11)
- **5,000 packets/day**, **~100 vehicles**, **20 nodes**.
- Goal: feasibility and viability analysis, not production.

## Transfer types (owner, 2026-10-11)
In all cases the physical transfer happens **while both parties are stopped at a point**.

| | Vehicle → Node | Vehicle → Vehicle (in-flight hop) |
|---|---|---|
| Location | Fixed (20 nodes) | Almost any stopping point (rendezvous) |
| Capacity | Hundreds of packets | Limited (vehicle capacity) |
| Delay | Handling time + possible queue | Handling time + waiting for the other vehicle (synchronization) |
| Modeling | Capacitated facility with service/queue time | Synchronization constraint between two routes |

## Problem family
- **PDPTW** (pickup and delivery with time windows) as the base.
- **PDPT** (pickup and delivery with transfers): packets may change vehicle at
  transfer points. Node transfers = fixed transfer points with capacity and queue;
  vehicle transfers = rendezvous points chosen from a candidate set.
- **Time-dependent travel times** (traffic) and **dynamic events** (delays,
  breakdowns, new orders) → re-optimization.

## Scale implications (to verify in PH-003/PH-004)
- Exact methods for PDPT are only practical for small instances; at 5,000
  packets/day we need **decomposition + heuristics**. ASSUMPTION based on the
  literature below; to be confirmed by the review.
- Travel-time matrix: up to ~10,000 pickup/delivery points + 20 nodes ⇒ ~10⁸
  origin-destination pairs for a full matrix. Google Compute Route Matrix allows
  625 elements per request and bills per element, so full matrices from Google
  are impractical. Plan: zone aggregation (e.g. H3 cells) + open-source engine
  (OSRM/Valhalla/pgRouting) for bulk matrices; Google Routes API for traffic
  calibration samples and spot ETAs. Exact costs quantified in PH-004.

## Proposed solution approach (hypothesis to test)
1. **Zoning:** assign the service area to the 20 nodes (Voronoi/clustering).
2. **Baseline (node-only):** first/last mile per zone as PDPTW/VRPTW
   (~250 packets and ~5 vehicles per zone on average); node-to-node linehaul.
   Solvers to benchmark: OR-Tools, PyVRP.
3. **In-flight hops:** improvement layer (e.g. ALNS move) that replaces node
   visits with vehicle-vehicle rendezvous when detour + wait + handling is lower
   than going through a node and capacity allows.
4. **Rerouting:** rolling-horizon re-optimization triggered by delay events.
5. **Compare** baseline vs hops on KPIs: on-time %, km, vehicle-hours, transfers,
   node queue time, cost per packet.

## Open modeling questions
- Vehicle capacity (packets/volume) and fleet mix → Q-008.
- Packet time windows (same-day? next-day?) and order arrival (batch vs streaming) → Q-009.
- Node queue model (fixed delay vs. queueing model) — start with an empirical
  distribution parameter; refine with data.
- Rendezvous candidates: legal stopping points; start with a grid of candidate points.

## Starting references (to read and verify)
- Cortés, Matamala, Contardo (2010). *The pickup and delivery problem with transfers:
  Formulation and a branch-and-cut solution method.* European Journal of Operational Research.
- Masson, Lehuédé, Péton (2013). *An adaptive large neighborhood search for the pickup
  and delivery problem with transfers.* Transportation Science.
- Drexl (2012). *Synchronization in vehicle routing — a survey of VRPs with multiple
  synchronization constraints.* Transportation Science.
- Google Routes API — Compute Route Matrix overview:
  https://developers.google.com/maps/documentation/routes/compute-route-matrix-over (accessed 2026-10-11)
