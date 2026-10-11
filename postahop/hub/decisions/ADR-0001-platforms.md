# ADR-0001 Platforms: GitHub, Vercel, Supabase

- Status: Accepted
- Date: 2026-10-11
- Deciders: owner

## Context
The owner wants one consistent stack with minimal platforms.

## Decision
- **GitHub**: version control and GitHub Actions workflows only.
- **Vercel**: hosting, serverless functions, preview deployments, env management.
- **Supabase**: Postgres database (with PostGIS for geospatial data; pgRouting is
  also available as an extension), plus Auth/Storage if needed.
- Any additional platform requires a new ADR approved by the owner.

## Consequences
- Long-running optimization jobs must fit Vercel function limits or run elsewhere
  within this stack (e.g. GitHub Actions for offline simulations). To be resolved in ADR-0002.
- Geospatial queries live in Postgres/PostGIS.

## Sources
- Supabase pgRouting extension: https://supabase.com/docs/guides/database/extensions/pgrouting (accessed 2026-10-11)
- Supabase Postgres extensions: https://supabase.com/features/postgres-extensions (accessed 2026-10-11)
