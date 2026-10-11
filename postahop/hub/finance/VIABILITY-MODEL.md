# Financial Viability Model (v0)

Owner: algorithms · Status: DRAFT seeded by orchestrator · Issue: PH-012

## Question
At MVP scale (5,000 packets/day, ~100 vehicles, 20 nodes), what is the cost per
packet, and do in-flight hops reduce it versus a node-only network?

## Cost drivers (inputs — values needed from owner, Q-007)
| Driver | Unit | Source |
|---|---|---|
| Vehicle fixed cost | per vehicle-day | owner |
| Driver cost | per hour | owner |
| Energy/fuel + maintenance | per km | owner |
| Node operating cost | per node-day | owner |
| Node handling | per packet | owner |
| Transfer handling (vehicle-vehicle) | per transfer | owner / ASSUMPTION |
| Maps/routing API | per request/element | PH-004 (official pricing) |
| Cloud (Vercel, Supabase) | per month | official pricing |
| Revenue | per packet | owner |

## Outputs
- Cost per packet (total and by driver), break-even price, sensitivity
  (tornado) on the top drivers, node-only vs hops comparison.
- All outputs reproducible from simulation runs (seed + parameters).
