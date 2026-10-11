# Open Questions (for the owner)

Owner: orchestrator · Anyone may append. Answered questions move to the bottom.

| ID | Question | Why it matters | Asked by | Status |
|---|---|---|---|---|
| Q-004 | Geographic region/city for the MVP, and monthly budget for maps APIs? | Realistic road network, provider costs. | orchestrator | Open |
| Q-006 | Any real data (historic orders, fleet, nodes)? | Realism vs synthetic data. | orchestrator | Open |
| Q-007 | Cost and revenue inputs (vehicle/day, driver/hour, cost/km, node/day, handling/packet, price/packet)? Rough ranges are fine. | Financial viability model. | orchestrator | Open |
| Q-008 | Vehicle types and capacity (packets or volume per vehicle)? | V2V transfer feasibility. | algorithms | Open |
| Q-009 | Delivery promise (same-day / next-day, time windows) and how orders arrive (all known in the morning vs. during the day)? | Static vs dynamic problem. | algorithms | Open |

## Answered
| ID | Question | Answer (2026-10-11) |
|---|---|---|
| Q-001 | Subfolder or dedicated repo? | Dedicated repo `PostaHop` + GitHub Projects (ADR-0004). |
| Q-002 | Languages? | Python for simulation/analysis/pilots; API choice delegated → Python/FastAPI (ADR-0002). No app UI; simple results viewer only. |
| Q-003 | Target scale? | 5,000 packets/day, ~100 vehicles, 20 nodes (MVP). |
| Q-005 | Transfer mechanics? | Two types, both stopped at a point: vehicle→node (fixed, hundreds of packets, possible queue/delay) and vehicle→vehicle (almost any point, limited capacity). |
