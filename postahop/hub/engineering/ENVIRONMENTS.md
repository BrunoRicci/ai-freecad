# Environments

Owner: engineer · Status: PLANNED (PH-005..PH-007)

| Env | Hosting | Database | Trigger |
|---|---|---|---|
| local | `next dev` / local Python | Supabase CLI local stack | developer |
| preview | Vercel preview deployment | Supabase (branch or shared staging — TBD) | every PR |
| production | Vercel production | Supabase production project | merge to release branch (TBD) |

## Env var names (values live in Vercel/GitHub/Supabase secret stores only)
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_MAPS_API_KEY`
