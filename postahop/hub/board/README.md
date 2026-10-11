# Task tracking: GitHub Issues + Projects

Owner: orchestrator · See ADR-0004.

- **Issues** are the cards. **The GitHub Project** ("PostaHop") is the board.
- The hub stays the source of truth for content (designs, results, decisions);
  issues hold the work item, status and discussion, and link to hub files.

## Board columns (Project "Status" field)
`Backlog` → `Ready` → `In Progress` → `In Review` → `Done`

## Labels
| Label | Meaning |
|---|---|
| `agent:architect` · `agent:algorithms` · `agent:engineer` · `agent:docs-writer` · `agent:orchestrator` | Owner agent (exactly one) |
| `status:ready` · `status:in-progress` · `status:review` | Board column (at most one) |
| `blocked` | Waiting on dependency or owner decision |
| `type:feature` · `type:research` · `type:infra` · `type:docs` · `type:decision` | Kind of work |
| `prio:high` · `prio:normal` · `prio:low` | Priority |

## How status reaches the board
- Agents set `status:*` labels and close issues (works via REST/MCP from agent sessions).
- `.github/workflows/project-sync.yml` adds every issue to the Project and maps
  labels → Status (`closed` → `Done`, no status label → `Backlog`).
- Requires repo variable `PROJECT_NUMBER` and secret `PROJECT_TOKEN`
  (classic PAT with `project` and `repo` scopes). Reason: Claude cloud sessions
  cannot call the GitHub GraphQL API that Projects use.

## Issue body template
```
## Goal
## Acceptance criteria
- [ ] ...
## Inputs (hub files, ADRs)
## Expected outputs (files to create/update)
## Depends on
#N
```

Initial backlog: `backlog-seed.md` (created as issues once the repo exists).
