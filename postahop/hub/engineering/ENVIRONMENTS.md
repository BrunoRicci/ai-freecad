# Environments

Owner: engineer · Status: PLANNED (PH-005..PH-007)

| Env | API | Database | Trigger |
|---|---|---|---|
| local | `uvicorn` / `fastapi dev` | Supabase CLI local stack | developer |
| preview | Vercel preview deployment | Supabase staging project (or branching — TBD) | every PR |
| production | Vercel production | Supabase production project | merge to `main` |

Simulations: local or GitHub Actions (`workflow_dispatch`), results as artifacts/reports.

## Env var / secret names (values only in Vercel/GitHub/Supabase secret stores)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_MAPS_API_KEY`
- GitHub: secret `PROJECT_TOKEN`, variable `PROJECT_NUMBER` (Project sync)
