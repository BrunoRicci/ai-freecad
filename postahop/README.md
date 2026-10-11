# PostaHop

Logistics analysis and packet routing platform: nodes, vehicles, packets, and
"in-flight" vehicle-to-vehicle packet transfers, with geographic route analysis
(travel time, traffic, delay, ETA).

## Stack (fixed by the owner)

| Concern | Platform |
|---|---|
| Version control, CI/CD | GitHub + GitHub Actions |
| Hosting / infrastructure | Vercel |
| Database | Supabase (Postgres + PostGIS) |
| Task tracking | Markdown Kanban in `hub/board/KANBAN.md` (see ADR-0003) |

## Layout

```
postahop/
├── CLAUDE.md            # Orchestrator (main agent) instructions
├── .claude/agents/      # Specialist agent definitions
│   ├── architect.md
│   ├── algorithms.md
│   ├── engineer.md
│   └── docs-writer.md
└── hub/                 # Single source of truth, shared by all agents
    ├── README.md        # Hub protocol: read/write rules, ownership, IDs
    ├── PROJECT.md       # Vision, scope, glossary pointer
    ├── STATUS.md        # Current state snapshot
    ├── JOURNAL.md       # Append-only activity log
    ├── board/           # Kanban
    ├── decisions/       # ADRs
    ├── handoffs/        # Agent-to-agent requests
    ├── questions/       # Open questions for the owner
    ├── architecture/    # Architect-owned
    ├── algorithms/      # Algorithms-owned
    ├── engineering/     # Engineer-owned (envs, CI/CD, runbooks)
    ├── docs/            # Docs-writer-owned (glossary, user docs)
    └── research/        # Sourced research notes
```

## Using the agents

Start Claude Code **from this folder** (`cd postahop && claude`). Claude Code
discovers project agents by walking up from the working directory, so agents in
`postahop/.claude/agents/` are not visible when started from the repo root.
