# Open Questions (for the owner)

Owner: orchestrator · Anyone may append. Answered questions move to the bottom with the answer.

| ID | Question | Why it matters | Asked by | Status |
|---|---|---|---|---|
| Q-001 | Keep PostaHop as a subfolder of `ai-freecad`, or move it to a dedicated repo? | Agents/CI/Vercel are simpler with a dedicated repo; repo name is unrelated. | orchestrator | Open |
| Q-002 | OK with TypeScript (Next.js) for app/API + Python for solver/simulations? | Blocks code scaffold (ADR-0002). | orchestrator | Open |
| Q-003 | Target scale: how many nodes, vehicles, packets per day? Batch planning or real-time re-routing? | Drives algorithm choice and infra limits. | orchestrator | Open |
| Q-004 | Geographic region(s) and monthly budget for maps APIs? | Provider choice, cost model. | orchestrator | Open |
| Q-005 | In-flight hop: do vehicles meet stationary at a rendezvous point, or is any transfer allowed at any point en route? | Changes the mathematical model significantly. ASSUMPTION for now: stationary meeting at a rendezvous point. | orchestrator | Open |
| Q-006 | Any real data (historic orders, fleet, nodes) available for simulations? | Realism of results vs synthetic data. | orchestrator | Open |

## Answered
(none yet)
