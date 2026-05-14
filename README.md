# QuantTrack

A practical trading journal and analytics platform built with a FastAPI backend and React frontend.

This repository contains the core application structure for recording trades, managing journal entries, generating analytics summaries, and running workflow-aware ML/NLP inference.

---

## What This Project Includes

- FastAPI backend with JWT authentication, SQLAlchemy ORM, and Pydantic validation
- Trade tracking CRUD API with statistics summary
- Journal entry workflow with NLP-driven behavioral analysis
- Analytics endpoints for dashboard metrics and summary views
- ML inference endpoints for trade prediction, risk detection, and feature explanation
- React frontend scaffold for dashboard, trades, journal, auth, and analytics pages
- Local development support using SQLite and optional PostgreSQL via `DATABASE_URL`
- Docker Compose configuration for backend + frontend + PostgreSQL

---

## Project Status

This project is a working prototype with the following implemented capabilities:

- User registration and login with JWT access and refresh tokens
- Trade CRUD operations and user-scoped data isolation
- Trading statistics and dashboard analytics calculation
- Journal creation and NLP analysis on journal notes
- ML prediction service with route-level inference and model metadata
- API documentation available via `/api/docs`

Not currently implemented or outside the core scope:

- broker integrations or live market feeds
- full production-grade Redis/Celery background processing
- a complete enterprise-grade deployment pipeline

---

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn
- SQLite (default local storage)
- PostgreSQL (optional via `DATABASE_URL`)
- python-jose, bcrypt, passlib
- pandas, numpy, scikit-learn, joblib
- TextBlob, spaCy, NLTK

### Frontend

- React
- Redux Toolkit
- Tailwind CSS
- Axios

### Dev / Testing

- Docker / Docker Compose
- Alembic
- Pytest

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn
- Docker and Docker Compose (optional)

### Backend Setup

```powershell
cd 'E:\FAANG\PROJECTS\QUANT TRACK\backend'
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` if you need custom configuration.

> By default, the backend uses `sqlite:///./quanttrack.db` when `DATABASE_URL` is not set.

Run the backend locally:

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the API docs at: `http://localhost:8000/api/docs`

### Frontend Setup

```powershell
cd 'E:\FAANG\PROJECTS\QUANT TRACK\frontend'
npm install
npm start
```

The frontend is expected on `http://localhost:3000` by default.

### Docker Compose

The repository includes a `docker-compose.yml` that starts:

- `postgres` database
- `backend` API service
- `frontend` React service

Start with:

```powershell
docker compose up -d
```

If you use Docker Compose, make sure `DATABASE_URL` is configured to point at the `postgres` service.

---

## API Endpoints

### Health and Root

- `GET /api/health` — health check
- `GET /` — root status and documentation links

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh-token`
- `GET /api/auth/verify`
- `POST /api/auth/logout`

### Trades

- `POST /api/trades` — create a trade
- `GET /api/trades` — list user trades
- `GET /api/trades/{trade_id}` — get trade details
- `PUT /api/trades/{trade_id}` — update a trade
- `DELETE /api/trades/{trade_id}` — delete a trade
- `GET /api/trades/statistics/summary` — summary statistics

### Analytics

- `GET /api/analytics/dashboard` — dashboard payload
- `GET /api/analytics/summary` — summary metrics

### ML Insights

- `POST /api/ml/predictions` — trade prediction
- `POST /api/ml/risk-detection` — risk detection
- `POST /api/ml/pattern-analysis` — pattern analysis
- `GET /api/ml/model-performance` — model performance metrics
- `POST /api/ml/retrain` — retrain models
- `GET /api/ml/features` — feature importance

### Journals and NLP

- `POST /api/journals` — create journal entry and analyze it
- `GET /api/journals` — list journal entries
- `GET /api/journals/summary` — journal analysis summary
- `POST /api/journals/analyze` — analyze text without storing it
- `GET /api/journals/{journal_id}/analysis` — retrieve stored analysis

---

## Database Schema Overview

### Core tables

- `users`
- `trades`
- `journals`
- `nlp_analyses`
- `ml_predictions`
- `analytics_summaries`

### Notes

- Users are isolated by `user_id` on all protected resources.
- Trades support direction, session, emotional state, result labels, and optional notes.
- Journal entries can be linked to a trade and store NLP analysis output.
- ML predictions are persisted with confidence and feature metadata.
- Analytics summaries can store pre-calculated metric JSON payloads.

---

## Testing

Run backend tests from the project root:

```powershell
cd 'E:\FAANG\PROJECTS\QUANT TRACK\backend'
.\.venv\Scripts\Activate.ps1
pytest tests/
```

---

## Notes for Review

- The backend is configured to run with SQLite by default and uses `DATABASE_URL` for PostgreSQL if available.
- The project includes ML/NLP inference routes, but the current implementation is best described as prototype-level logic rather than a production-grade trading AI system.
- `docker-compose.yml` is designed to wire together backend, frontend, and PostgreSQL, but local dependency management should be validated before using containers.

---

## License

MIT
