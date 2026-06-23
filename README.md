# QuantTrack

A backend-focused trading journal and analytics platform with ML/NLP-powered behavioral analysis.

## Overview

QuantTrack helps traders log trades, review performance, and track behavioral signals with simple analytics and model-backed insights.

## Screenshots

- Dashboard with key performance metrics and equity view
- Trade entry page with strategy and emotion fields
- Journal analysis page for behavioral pattern detection

## Architecture

- FastAPI backend with SQLAlchemy and Pydantic
- React frontend with Redux Toolkit and Tailwind CSS
- SQLite local storage by default, optional PostgreSQL via `DATABASE_URL`
- JWT authentication and request logging
- Lightweight scikit-learn models for trade insights
- Rule-based NLP for journal sentiment and behavior tags

## Tech stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic, Uvicorn
- Data and ML: pandas, numpy, scikit-learn, joblib
- NLP: TextBlob plus rule-based analysis
- Frontend: React, Redux Toolkit, Tailwind CSS
- Testing: pytest

## Setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Create a local .env from the example and DO NOT commit it to source control
copy ..\.env.example .env
```

Optional: update `.env` if you want PostgreSQL instead of SQLite.

```powershell
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm start
```

### Docker

```powershell
docker compose up -d
```

Open the backend docs at `http://localhost:8000/api/docs` and the frontend at `http://localhost:3000`.

## API overview

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh-token`
- `GET /api/auth/verify`
- `POST /api/auth/logout`

### Trades

- `POST /api/trades`
- `GET /api/trades`
- `GET /api/trades/{trade_id}`
- `PUT /api/trades/{trade_id}`
- `DELETE /api/trades/{trade_id}`
- `GET /api/trades/statistics/summary`

### Analytics

- `GET /api/analytics/dashboard`
- `GET /api/analytics/summary`

### ML insights

- `POST /api/ml/predictions`
- `POST /api/ml/risk-detection`
- `POST /api/ml/pattern-analysis`
- `GET /api/ml/model-performance`
- `POST /api/ml/retrain`
- `GET /api/ml/features`

### Journals and NLP

- `POST /api/journals`
- `GET /api/journals`
- `GET /api/journals/summary`
- `POST /api/journals/analyze`
- `GET /api/journals/{journal_id}/analysis`

## Features

- User authentication with JWT
- Trade journal CRUD with behavioral metadata
- Trade statistics and analytics summaries
- Lightweight ML predictions and feature importance
- Journal sentiment and behavior tagging
- Docker compose support for local development

## Future scope

- Add CSV import/export for trade history
- Add user settings and account profile details
- Improve model explainability with richer feature metadata
- Add simple data export for performance review
