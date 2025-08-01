# NuiFlo WorkForce – Backend API

FastAPI service that extends CrewAI and connects to Supabase Postgres.

## Quick start
```bash
# install deps (inside repo root)
uv sync -p workforce_api

# set env vars
export SUPABASE_DB_URL="postgresql+asyncpg://postgres:<PW>@db.<project>.supabase.co:6543/postgres"

# run dev server
uv run uvicorn workforce_api.main:app --reload
``` 