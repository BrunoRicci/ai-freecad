# ADR-0002 Languages and runtime

- Status: **Proposed** (needs owner confirmation — Q-002)
- Date: 2026-10-11
- Deciders: owner, architect
- Related: PH-001, PH-005

## Context
- Web app, APIs and dashboards deploy to Vercel; Next.js/TypeScript is Vercel's
  first-class framework.
- The mature optimization/simulation ecosystem is Python (Google OR-Tools, PyVRP,
  NumPy/pandas). Vercel supports Python functions, but solver runtime and memory
  must fit Vercel function limits (look up current limits before committing).

## Options
1. **TypeScript (Next.js) for app/API + Python for solver & simulations.**
   Solver as Vercel Python function for small instances; offline/batch simulations
   in GitHub Actions or locally. Pros: best tools per job. Cons: two languages.
2. **TypeScript only.** Pros: one language. Cons: weak optimization ecosystem;
   would push us to external solver APIs.
3. **Python only (e.g. FastAPI on Vercel).** Pros: one language. Cons: weaker
   frontend story; UI still needs JS.

## Proposed decision
Option 1, pending owner confirmation and a quick spike on Vercel limits with a
realistic instance size (PH-004/PH-008 inform this).

## Consequences
- Monorepo with `apps/web` (Next.js) and `packages/solver` (Python), shared
  JSON schema for problem/solution contracts.
