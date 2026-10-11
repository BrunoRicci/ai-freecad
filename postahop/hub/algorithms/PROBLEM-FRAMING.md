# Problem Framing (v0)

Owner: algorithms · Status: DRAFT seeded by orchestrator · Card: PH-003

## Problem family
- Base: **Vehicle Routing Problem with Time Windows (VRPTW)** and
  **Pickup and Delivery Problem with Time Windows (PDPTW)**: each packet has an
  origin, destination, time windows, size; vehicles have capacity and shifts.
- In-flight hops: **Pickup and Delivery Problem with Transfers (PDPT)** — a packet
  may change vehicle at a transfer point. Transfers create **synchronization**
  constraints between vehicle routes (both vehicles must be at the point in
  compatible time windows), which makes the problem harder than plain PDPTW.
- Traffic: **time-dependent** travel times (TDVRP) — travel time depends on departure time.

## Open modeling questions
- Transfer points: fixed candidate set (nodes, parking spots) vs. free rendezvous (Q-005).
- Transfer cost/time (handover duration, waiting allowed?).
- Objective: weighted sum of distance, time, lateness, vehicles, transfers — weights TBD with owner.

## Candidate solution approaches (to evaluate in PH-003)
- Exact (MIP / branch-and-cut): small instances, benchmarks for heuristics.
- Metaheuristics (e.g. Adaptive Large Neighborhood Search): realistic sizes.
- Off-the-shelf solvers: Google OR-Tools (supports pickup & delivery + time windows;
  transfers are not a built-in feature, would need custom modeling — UNVERIFIED in
  detail), PyVRP, VROOM; Google Maps Platform **Route Optimization API** as a
  managed baseline. Verify each against official docs.

## Routing data
- Google Maps Platform **Routes API** (`computeRoutes`, `computeRouteMatrix`) with
  traffic-aware routing. The Distance Matrix API is legacy; Compute Route Matrix
  replaces it (max 625 elements per server-side request per docs).
- Open-source alternatives for bulk/offline experiments: OSRM, Valhalla, GraphHopper,
  pgRouting (in Supabase). Evaluate in PH-004 (accuracy, traffic support, cost, ToS).

## Starting references (to read and verify)
- Cortés, Matamala, Contardo (2010). *The pickup and delivery problem with transfers:
  Formulation and a branch-and-cut solution method.* European Journal of Operational Research.
- Masson, Lehuédé, Péton (2013). *An adaptive large neighborhood search for the pickup
  and delivery problem with transfers.* Transportation Science.
- Drexl (2012). *Synchronization in vehicle routing — a survey of VRPs with multiple
  synchronization constraints.* Transportation Science.
- Google Routes API — Compute Route Matrix overview:
  https://developers.google.com/maps/documentation/routes/compute-route-matrix-over (accessed 2026-10-11)
