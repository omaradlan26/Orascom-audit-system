# Orascom Audit Management System

Local-first MVP of a role-based audit tracking platform built with `Streamlit`, `FastAPI`, and `SQLite`.

## Features
- Guest read-only access
- Admin login with password hashing
- Audit CRUD operations
- Filterable audit list
- Dashboard metrics for total, open, closed, and overdue audits
- SQLite persistence with seeded demo data

## Project Structure
- `backend/app/main.py`: FastAPI entrypoint
- `backend/app/routes/`: auth and audit API routes
- `backend/app/db.py`: SQLite initialization and connection helpers
- `frontend/app.py`: Streamlit dashboard
- `frontend/components/`: dashboard and audit form/table rendering

## Requirements
- Python 3.11+

## Installation
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
Optional environment variables:

```bash
AUDIT_API_URL=http://127.0.0.1:8000
AUDIT_DB_PATH=backend/data/audit_system.db
AUDIT_ADMIN_USERNAME=admin
AUDIT_ADMIN_PASSWORD=admin123
```

You can copy values from `.env.example` into your shell or environment manager.

## Run The Backend
```bash
uvicorn backend.app.main:app --reload
```

The API will start on `http://127.0.0.1:8000` with:
- `GET /health`
- `POST /auth/guest`
- `POST /auth/login`
- `GET /audits`
- `GET /audits/summary`
- `POST /audits`
- `PUT /audits/{id}`
- `DELETE /audits/{id}`

## Automated Smoke Test (Optional)
With the backend running:

```bash
python scripts/smoke_test.py
```

## Run The Frontend
In a second terminal:

```bash
streamlit run frontend/app.py
```

The UI will start on `http://localhost:8501`.

## Default Access
- Admin username: `admin`
- Admin password: `admin123`
- Guest mode: available from the login screen without a password

Change the admin credentials with environment variables before production use.

## Local Validation Checklist
1. Start the FastAPI backend.
2. Start the Streamlit frontend.
3. Enter guest mode and verify the dashboard is view-only.
4. Log in as admin and create, edit, and delete an audit.
5. Restart the backend and verify audit data persists in SQLite.

## Future Upgrades
- Move the DB layer from SQLite to PostgreSQL
- Replace in-memory session storage with a stronger auth/session mechanism
- Add export, notifications, history tracking, and deployment configs for hosted environments

## Deploy (Render Blueprint)
This repo includes `render.yaml` for deploying both services:
- `orascom-audit-api` (FastAPI backend)
- `orascom-audit-frontend` (Streamlit frontend)

### Steps
1. Open [Render Dashboard](https://dashboard.render.com/).
2. Click **New** -> **Blueprint**.
3. Connect this GitHub repository.
4. Render will detect `render.yaml` and create both services.
5. Set secret env vars when prompted:
   - `AUDIT_ADMIN_USERNAME`
   - `AUDIT_ADMIN_PASSWORD`
6. Deploy and open the `orascom-audit-frontend` URL.

The frontend automatically receives `AUDIT_API_URL` from the backend service URL via blueprint config.
