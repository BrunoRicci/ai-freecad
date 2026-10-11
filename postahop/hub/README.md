# Hub Protocol

The hub is the project's single source of truth. Every agent reads it before
working and updates it after working. If it is not in the hub, it is not known.

## 1. Before any task
1. `STATUS.md` — current state.
2. Your GitHub issue and its dependencies (conventions: `board/README.md`).
3. `handoffs/` — open handoffs addressed to you.
4. Files linked from your issue, plus your owned area.
5. `decisions/` — ADRs relevant to the task. Do not contradict an accepted ADR;
   propose a superseding one instead.

## 2. After any task (definition of done for hub hygiene)
- [ ] GitHub issue updated: status label, comment with summary + links to outputs; closed when done.
- [ ] One entry appended to `JOURNAL.md`.
- [ ] Owned docs updated with results.
- [ ] Handoff created if another agent must act; handoffs addressed to you closed.
- [ ] New decision → ADR in `decisions/`. New unknown → `questions/OPEN-QUESTIONS.md`.

## 3. Ownership (one writer per area; others propose via handoff)

| Path | Owner | Others may |
|---|---|---|
| `PROJECT.md`, `STATUS.md` | orchestrator | read |
| GitHub issues / Project | orchestrator (creates, prioritizes) | update their own issues |
| `board/` | orchestrator | read |
| `JOURNAL.md` | all | append only |
| `decisions/` | architect | draft ADRs as `Proposed` |
| `architecture/` | architect | read |
| `algorithms/` | algorithms | read |
| `finance/` | algorithms | read |
| `engineering/` | engineer | read |
| `docs/` | docs-writer | read |
| `research/` | all | add notes (own files) |
| `questions/OPEN-QUESTIONS.md` | orchestrator | append |
| `handoffs/` | all | create; only the addressee closes |

## 4. IDs and conventions
- Tasks: GitHub issue `#N` (legacy seed IDs `PH-###` kept in issue titles) · ADRs: `ADR-####` · Questions: `Q-###` · Handoffs: `H-YYYYMMDD-##`
- Dates: ISO 8601 (`2026-10-11`). Units: SI, times in seconds unless stated, timestamps UTC.
- File names: kebab-case. Formats: Markdown, YAML, CSV, JSON, Mermaid for diagrams.

## 5. Truthfulness
- External facts need a source: URL + access date. Prefer official docs and peer-reviewed papers.
- Mark unverified statements `ASSUMPTION` or `UNVERIFIED`.
- Numbers from experiments must state dataset, parameters, and how to reproduce.

## 6. Safety
- Never write secrets, API keys, or personal data to the hub. Reference env var names only.
