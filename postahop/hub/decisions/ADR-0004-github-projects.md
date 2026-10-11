# ADR-0004 Task tracking: GitHub Issues + GitHub Projects

- Status: Accepted
- Date: 2026-10-11
- Deciders: owner
- Supersedes: ADR-0003

## Context
The owner allowed GitHub Projects. A dedicated repo `PostaHop` replaces the
subfolder in `ai-freecad`.

## Decision
- Issues are work items; a user-level GitHub Project "PostaHop" is the board.
- Agents update issues (labels, comments, close) via REST/MCP.
- A GitHub Action (`project-sync.yml`) mirrors issue state to the Project Status
  field, because Claude cloud sessions cannot call the GraphQL API that Projects
  require (verified 2026-10-11: GraphQL and user-level project endpoints return 403
  from the session).

## Consequences
- Needs a classic PAT secret `PROJECT_TOKEN` and repo variable `PROJECT_NUMBER`.
- Conventions in `hub/board/README.md`.
