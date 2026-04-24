# TrustCore AI

TrustCore AI is an AI-powered digital trust scoring dashboard with:

- A FastAPI backend for scoring, analytics, alerts, PDF export, and live WebSocket updates
- A professional animated frontend dashboard
- A browser extension for collecting behavioral signals

## Run Locally

```bash
./venv/bin/python backend/main.py
```

Open:

- `http://localhost:8000`

## Project Structure

- `frontend/` - Dashboard UI
- `backend/` - FastAPI backend and trust scoring logic
- `extension/` - Browser extension
- `seed_data.py` - Demo data seeding script
- `run.sh` - Quick local startup helper
