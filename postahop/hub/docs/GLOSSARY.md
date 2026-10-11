# Glossary

Owner: docs-writer · One term, one meaning.

| Term | Definition |
|---|---|
| Node | Fixed location in the network (hub, depot, locker). |
| Vehicle | Mobile carrier with capacity and shift. |
| Packet | Item to move from origin to destination within time windows. |
| Route | Ordered list of stops assigned to one vehicle in a plan. |
| Leg | Travel segment between two consecutive stops. |
| Hop | Custody change of a packet while both parties are stopped (vehicle↔node or vehicle→vehicle). |
| In-flight hop | Vehicle-to-vehicle transfer at a rendezvous point, without passing through a node. |
| Rendezvous point | Location where two vehicles meet to transfer packets. |
| ETA | Estimated time of arrival at a stop. |
| Scenario | Set of inputs (network, fleet, demand, traffic) used for planning or simulation. |
| Node queue delay | Waiting time at a node before a hop is handled. |
| Rerouting | Re-optimizing plans after an event (delay, breakdown, new order). |
