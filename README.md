# Personal Expense Tracker API

FastAPI Personal Expense Tracker for PHITRON AI/ML Mid Term.

## Tech stack

- FastAPI
- PostgreSQL (Supabase)
- SQLAlchemy ORM
- Pydantic
- JWT authentication
- Pytest

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your Supabase DATABASE_URL to .env
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000/
Docs: http://127.0.0.1:8000/docs
