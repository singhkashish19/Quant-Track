# QuantTrack - How to Run

A concise guide to start the QuantTrack backend and frontend locally or with Docker.

## Backend - Local

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example .env
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000/api/docs`

## Frontend - Local

```powershell
cd frontend
npm install
npm start
```

Open: `http://localhost:3000`

## Docker

```powershell
docker compose up -d
```

The stack includes:
- `backend` FastAPI service
- `frontend` React development server
- `postgres` database service

## Test

```powershell
cd backend
pytest tests/ -v
```

## Notes

- The backend runs on SQLite by default when `DATABASE_URL` is not set.
- Use `.env.example` as the starting point for local or Docker environment variables.
- Docker is optional; the project is designed to work locally with minimal setup.
