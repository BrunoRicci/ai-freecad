# ADR-0003 Task tracking: Markdown Kanban in the hub

- Status: Accepted (revisable by owner)
- Date: 2026-10-11
- Deciders: orchestrator

## Context
Requirement: a Kanban for tasks/features, GitHub used only for VCS and Actions,
no extra platforms, and all agents must read/write tracking state as files.

## Options
1. **Markdown Kanban file in the hub** (`board/KANBAN.md`). Versioned with the code,
   readable/editable by agents and humans, optional visual board via the Obsidian
   Kanban plugin. Cons: no notifications, merge conflicts if many parallel edits.
2. GitHub Projects/Issues — excluded by "GitHub only for VCS + Actions".
3. Kanban table in Supabase + small Vercel UI — single stack, but custom work and
   agents would need API access instead of files.
4. External tool (Linear, Jira, Trello) — adds a platform.

## Decision
Option 1 now. Revisit Option 3 if the team grows or a UI is needed.

## Consequences
- Card format and column rules are defined at the bottom of `board/KANBAN.md`.
- Only the orchestrator moves cards to Done.
