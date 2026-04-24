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

## Deploy Live On Render

This repo includes a `Dockerfile`, `.dockerignore`, and `render.yaml` so you can deploy it as one live FastAPI service.

1. Push the latest code to GitHub.
2. In Render, click `New` -> `Blueprint`.
3. Connect this repository and deploy the detected `render.yaml`.
4. Open your `https://<your-service>.onrender.com` URL after the build finishes.

Important notes:

- The app now exposes `GET /healthz` for health checks.
- `render.yaml` enables `TRUSTCORE_DEMO_SEED=true`, so a fresh live deploy starts with demo records instead of an empty dashboard.
- Render free web services use ephemeral storage, so SQLite data can reset on restart or redeploy.
- If you want persistent SQLite storage on a paid Render web service, attach a disk at `/app/data`.
- After deploy, open the browser extension popup and save your live backend URL so the extension sends metrics to the hosted app instead of localhost.
