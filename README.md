---
title: Orascom Audit Management System
emoji: 📊
colorFrom: blue
colorTo: red
sdk: streamlit
sdk_version: 1.37.0
app_file: app.py
pinned: false
license: mit
---

# Orascom Audit Management System

A role-based audit tracking platform built with Streamlit, FastAPI, and SQLite.

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

## Deploy (Hugging Face Spaces)

### Hugging Face Spaces Deployment
This repo is configured for Hugging Face Spaces deployment:

1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Choose **Streamlit** SDK
4. Connect your GitHub repository
5. Set Space name and visibility
6. Add these secrets in Space settings:
   - `AUDIT_ADMIN_USERNAME`: Your admin username
   - `AUDIT_ADMIN_PASSWORD`: Your admin password
7. Deploy and access your Space URL

### Technical Details
- FastAPI runs on `127.0.0.1:8000` in a background thread
- Streamlit frontend runs on the main thread
- SQLite database persists in Space storage
- Single-process architecture for Spaces compatibility

### Alternative: Render Blueprint
This repo also includes `render.yaml` for Render deployment:
- `orascom-audit-api` (FastAPI backend)
- `orascom-audit-frontend` (Streamlit frontend)
