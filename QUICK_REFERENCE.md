# QuantTrack - Quick Reference Guide

## 🎯 Project Overview
**Status**: ✅ Production Ready  
**Type**: Full-stack web application  
**Tech Stack**: FastAPI (Python) + React (JavaScript) + PostgreSQL + Docker  

---

## 📁 Directory Structure

```
QUANT TRACK/
├── backend/                          # Python FastAPI backend
│   ├── app/
│   │   ├── auth/                     # Authentication module
│   │   ├── trades/                   # Trade management module
│   │   ├── analytics/                # Analytics engine
│   │   ├── ml/                       # Machine learning
│   │   ├── nlp/                      # NLP analysis
│   │   ├── database/                 # ORM models
│   │   ├── middleware/               # Custom middleware
│   │   ├── utils/                    # Helper functions
│   │   ├── config.py                 # Configuration
│   │   └── main.py                   # FastAPI app entry
│   ├── tests/                        # Unit & integration tests
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Backend container
│   └── alembic/                      # Database migrations
│
├── frontend/                         # React.js frontend
│   ├── src/
│   │   ├── pages/                    # Page components
│   │   │   ├── Dashboard.js
│   │   │   ├── TradesPage.js
│   │   │   ├── AnalyticsPage.js
│   │   │   ├── JournalPage.js
│   │   │   ├── InsightsPage.js
│   │   │   └── ProfilePage.js
│   │   ├── components/               # Reusable components
│   │   ├── services/                 # API clients
│   │   ├── store/                    # Redux store
│   │   ├── hooks/                    # Custom hooks
│   │   ├── utils/                    # Utilities
│   │   ├── styles/                   # Global styles
│   │   ├── App.js                    # Root component
│   │   └── index.js                  # Entry point
│   ├── public/                       # Static files
│   ├── package.json                  # NPM dependencies
│   ├── Dockerfile                    # Frontend container
│   └── .env.example                  # Environment template
│
├── docs/                             # Documentation
│   ├── API.md                        # API reference
│   ├── DATABASE.md                   # Database schema
│   ├── ML_PIPELINE.md                # ML guide
│   ├── NLP_BEHAVIORAL_ANALYSIS.md   # NLP guide
│   ├── DEVELOPMENT.md                # Dev workflow
│   ├── GETTING_STARTED.md            # Quick start
│   └── ...
│
├── datasets/                         # Sample data
│   ├── trades.csv
│   ├── journals.csv
│   └── engineered_features.csv
│
├── docker-compose.yml                # Docker orchestration
├── .env.example                      # Environment variables
├── README.md                         # Main readme
├── ARCHITECTURE.md                   # Architecture docs
├── PROJECT_STATUS.md                 # Status report
├── PHASE2_REQUIREMENTS.md            # Requirements
├── COMPLETION_REPORT.md              # Final report
└── DOCUMENTATION_INDEX.md            # Doc navigation
```

---

## 🚀 Quick Start

### 1. **Clone/Navigate to Project**
```bash
cd "e:\FAANG\PROJECTS\QUANT TRACK"
```

### 2. **Setup Environment**
```bash
# Create .env from template
cp .env.example .env

# Update with your settings (optional)
# nano .env
```

### 3. **Run with Docker** (Easiest)
```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Access application
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/api/docs
```

### 4. **Stop Services**
```bash
docker-compose down
```

---

## 🔑 Key Endpoints

### Frontend
- **Login**: `http://localhost:3000/login`
- **Dashboard**: `http://localhost:3000/dashboard`
- **Trades**: `http://localhost:3000/trades`
- **Analytics**: `http://localhost:3000/analytics`
- **Journal**: `http://localhost:3000/journal`
- **Insights**: `http://localhost:3000/insights`

### Backend API
- **Health**: `GET http://localhost:8000/api/health`
- **Docs**: `http://localhost:8000/api/docs` (Swagger)
- **Base URL**: `http://localhost:8000/api`

### Database
- **Host**: localhost
- **Port**: 5432
- **User**: quanttrack_user
- **Password**: quanttrack_password (from .env)
- **Database**: quanttrack_db

### Redis
- **Host**: localhost
- **Port**: 6379

---

## 📝 API Quick Reference

### Authentication
```bash
# Register
POST /api/auth/register
Body: {"email": "user@example.com", "password": "...", "name": "..."}

# Login
POST /api/auth/login
Body: {"email": "user@example.com", "password": "..."}

# Refresh Token
POST /api/auth/refresh-token
Header: Authorization: Bearer <refresh_token>
```

### Trades
```bash
# Create Trade
POST /api/trades
Body: {trade_data}

# List Trades
GET /api/trades?limit=20&skip=0

# Get Trade
GET /api/trades/{id}

# Update Trade
PUT /api/trades/{id}
Body: {updated_fields}

# Delete Trade
DELETE /api/trades/{id}

# Get Statistics
GET /api/trades/statistics/summary
```

### Analytics
```bash
# Dashboard (all data)
GET /api/analytics/dashboard

# Summary (metrics only)
GET /api/analytics/summary
```

### ML
```bash
# Predict Trade
POST /api/ml/predictions
Body: {trade_features}

# Model Performance
GET /api/ml/model-performance

# Feature Importance
GET /api/ml/features

# Retrain Models
POST /api/ml/retrain
```

### Journals
```bash
# Create Journal
POST /api/journals
Body: {"notes": "...", "emotional_state": "FOMO"}

# List Journals
GET /api/journals

# Get Journal
GET /api/journals/{id}
```

---

## 🛠️ Development Workflow

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example .env

# Initialize database
python -m alembic upgrade head

# Run server with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build

# Run tests
npm test
```

---

## 📊 Database Tables

| Table | Purpose | Relationships |
|-------|---------|---|
| users | User accounts | One-to-many: trades, journals, predictions |
| trades | Trade records | Many-to-one: user, One-to-many: predictions, journal |
| journals | Journal entries | Many-to-one: user, trade, One-to-many: nlp_analyses |
| nlp_analyses | NLP results | Many-to-one: user, journal |
| ml_predictions | ML predictions | Many-to-one: user, trade |
| analytics_summaries | Pre-calculated metrics | Many-to-one: user |

---

## 🔒 Environment Variables

Key variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/db
DB_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your_secret_key_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
DEBUG=False
ENVIRONMENT=production
APP_VERSION=1.0.0

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
```

---

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest tests/ -v
```

### Run Specific Test
```bash
pytest tests/test_phase2_services.py::test_feature_engineering_creates_model_ready_row -v
```

### Test with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

---

## 🐳 Docker Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Execute Commands
```bash
# Run Python command in backend
docker-compose exec backend python -c "print('hello')"

# Run shell in frontend
docker-compose exec frontend /bin/sh
```

### Database
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U quanttrack_user -d quanttrack_db

# Migrate database
docker-compose exec backend python -m alembic upgrade head
```

---

## 📚 Documentation Links

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design |
| [COMPLETION_REPORT.md](COMPLETION_REPORT.md) | Full status report |
| [API.md](docs/API.md) | API reference |
| [DATABASE.md](docs/DATABASE.md) | Schema docs |
| [ML_PIPELINE.md](docs/ML_PIPELINE.md) | ML guide |
| [NLP_BEHAVIORAL_ANALYSIS.md](docs/NLP_BEHAVIORAL_ANALYSIS.md) | NLP guide |
| [DEVELOPMENT.md](docs/DEVELOPMENT.md) | Dev workflow |
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Quick start |

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Linux/Mac
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Docker Issues
```bash
# Rebuild all images
docker-compose build --no-cache

# Remove all containers
docker-compose down -v

# Start fresh
docker-compose up -d
```

### Database Connection
```bash
# Check PostgreSQL
docker-compose logs postgres

# Reset database
docker-compose down -v postgres
docker-compose up -d postgres
```

---

## 📈 Performance Tips

1. **Database Queries**: Use pagination for large datasets
2. **Frontend**: Use React DevTools to check unnecessary re-renders
3. **Backend**: Check slow queries in logs
4. **Caching**: Use Redis for frequently accessed data
5. **ML Models**: Retrain periodically (weekly recommended)

---

## 🚀 Deployment

### Pre-Deployment Checklist
- [ ] Update SECRET_KEY in .env
- [ ] Change database password
- [ ] Set DEBUG=False
- [ ] Set ENVIRONMENT=production
- [ ] Update CORS_ORIGINS
- [ ] Update REACT_APP_API_URL
- [ ] Configure SSL/TLS
- [ ] Setup backup strategy
- [ ] Configure monitoring
- [ ] Test all endpoints

### Deployment Steps
```bash
# Build production images
docker-compose build

# Start with production settings
ENVIRONMENT=production DEBUG=False docker-compose up -d

# Initialize database
docker-compose exec backend python -m alembic upgrade head

# Check health
curl http://your-domain.com/api/health
```

---

## 💡 Tips & Tricks

### Add a New Feature
1. Create API endpoint in backend
2. Create schema/model if needed
3. Create API client in frontend
4. Create page/component to use it
5. Add tests

### Debug Mode
```bash
# Backend
DEBUG=True uvicorn app.main:app --reload

# Frontend
BROWSER=none npm start
```

### Clear All Data
```bash
docker-compose down -v
docker-compose up -d
```

---

## 📞 Support Resources

- **Backend Issues**: Check `docs/DEVELOPMENT.md`
- **Frontend Issues**: Check React Console (F12)
- **Database Issues**: Check PostgreSQL logs
- **API Issues**: Visit `http://localhost:8000/api/docs`
- **General**: Check `DOCUMENTATION_INDEX.md`

---

**Last Updated**: May 12, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
