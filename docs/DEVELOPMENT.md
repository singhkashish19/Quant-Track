# Development Guide

## Project Overview

QuantTrack is a full-stack SaaS analytics platform for traders. This guide covers local development setup and best practices.

---

## Local Development Environment

### Prerequisites

```bash
# Check Python version
python --version  # Should be 3.11+

# Check Node version
node --version  # Should be 18+

# Check Docker
docker --version
docker-compose --version
```

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up .env file
cp ../.env.example ../.env
# Edit .env with your settings

# Initialize database
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## Code Organization

### Backend Structure

```
app/
├── auth/               # Authentication & JWT
├── trades/             # Trade CRUD
├── analytics/          # Metrics & calculations
├── ml/                 # ML models
├── nlp/                # NLP analysis
├── database/           # ORM models
└── main.py             # FastAPI app
```

### Frontend Structure

```
src/
├── components/         # Reusable components
├── pages/              # Page components
├── services/           # API calls
├── store/              # Redux state
├── utils/              # Helper functions
└── styles/             # CSS
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Implement Feature

#### Backend

```python
# 1. Create schema in app/module/schemas.py
from pydantic import BaseModel

class MySchema(BaseModel):
    field: str

# 2. Create service in app/module/service.py
class MyService:
    @staticmethod
    def my_method(data: MySchema, db: Session):
        # Implementation
        pass

# 3. Create route in app/module/router.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-endpoint")
def my_endpoint(data: MySchema):
    return MyService.my_method(data, db)

# 4. Add router to main.py
app.include_router(my_router)
```

#### Frontend

```javascript
// 1. Create component in src/components/MyComponent.js
function MyComponent() {
  return <div>Component</div>;
}

// 2. Add API call in src/services/api.js
export const myAPI = {
  create: (data) => apiClient.post('/my-endpoint', data),
};

// 3. Create page in src/pages/MyPage.js
function MyPage() {
  return <MyComponent />;
}

// 4. Add route in src/App.js
<Route path="/my-page" element={<MyPage />} />
```

### 3. Test Locally

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: Add my feature"
git push origin feature/my-feature
```

### 5. Create Pull Request

Open PR on GitHub with description of changes.

---

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_trades.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_trades.py::test_create_trade
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- test/LoginPage.test.js
```

### Test Structure

```
backend/tests/
├── test_auth.py
├── test_trades.py
├── test_analytics.py
├── conftest.py       # Fixtures
└── fixtures/
    ├── sample_trades.json
    └── sample_users.json
```

---

## Database Management

### View Current Schema

```bash
# Connect to database
psql postgresql://user:pass@localhost:5432/quanttrack_db

# List tables
\dt

# Describe table
\d trades

# View specific data
SELECT * FROM trades LIMIT 5;
```

### Create Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new_field to trades"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head
```

### Reset Database

```bash
cd backend

# Drop all tables
alembic downgrade base

# Recreate from scratch
alembic upgrade head
```

---

## Debugging

### Backend Debugging

```python
# Add breakpoint in code
def my_function():
    x = 10
    breakpoint()  # Debugger will stop here
    return x

# Then run:
# python -m pdb app/main.py
```

### Frontend Debugging

```javascript
// Use browser DevTools
function MyComponent() {
  console.log('Rendering');  // Browser console
  debugger;                   // Debugger will pause here
  return <div>Component</div>;
}

// Use Redux DevTools
// Install extension in your browser
```

### View Logs

```bash
# Backend logs
docker-compose logs backend -f

# Frontend logs
docker-compose logs frontend -f

# All logs
docker-compose logs -f
```

---

## Performance Tips

### Backend

1. Use async functions for I/O operations
2. Implement caching with Redis
3. Use database indexes for fast queries
4. Batch operations when possible
5. Profile with `cProfile`

```python
import cProfile

def my_function():
    # Code to profile
    pass

cProfile.run('my_function()')
```

### Frontend

1. Use React.memo for expensive components
2. Lazy load pages with React.lazy
3. Minimize bundle size
4. Use Redux selectors to prevent re-renders
5. Use useCallback for expensive functions

---

## Code Style

### Python (Black)

```bash
# Format code
black backend/

# Check style
black --check backend/
```

### JavaScript (Prettier)

```bash
# Format code
npx prettier --write frontend/src

# Check style
npx prettier --check frontend/src
```

### ESLint

```bash
# Fix linting issues
npm run lint:fix

# Check linting
npm run lint
```

---

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/quanttrack_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
DEBUG=True
ENVIRONMENT=development
APP_NAME=QuantTrack
```

### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_DEBUG=true
```

---

## Common Issues

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Issue: Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps

# Verify credentials in .env
# Restart database service
docker-compose restart postgres
```

### Issue: Frontend API Errors

```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check CORS configuration
# Check Authorization header in requests
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Development Guide Last Updated**: May 2024
