# QuantTrack — AI-Powered Trading Journal & Behavioral Analytics Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)

**A production-grade SaaS analytics platform for traders to record trades, analyze performance, identify behavioral mistakes, and receive AI/ML-driven insights.**

---

## 🎯 Project Overview

QuantTrack is a comprehensive trading analytics platform designed for:

- **Retail Traders** seeking performance improvement and behavioral insights
- **Institutional Traders** managing multiple strategies across different sessions
- **Trading Coaches** analyzing student performance and patterns
- **Fintech Platforms** integrating advanced trading analytics

### Key Features

✅ **Trade Management** — Record trades with complete metadata (entry, exit, strategy, emotional state)  
✅ **Advanced Analytics** — Calculate professional metrics (Sharpe ratio, drawdown, profit factor)  
✅ **ML-Powered Insights** — Predictive models for trade outcomes and risk detection  
✅ **NLP Behavioral Analysis** — Detect trading psychology patterns from journal entries  
✅ **Real-time Dashboard** — Visual performance analytics and equity curves  
✅ **Production-Ready API** — RESTful API with comprehensive documentation  
✅ **Secure Authentication** — JWT-based stateless authentication with refresh tokens  
✅ **Containerized Deployment** — Docker & Docker Compose for easy deployment  

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React.js Frontend (SPA)                      │
│  - Authentication UI                                             │
│  - Trade Management Dashboard                                    │
│  - Analytics & Visualizations                                    │
│  - Journal & Behavioral Insights                                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API (HTTPS)
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Async Python)                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Authentication | Trades | Analytics | ML | NLP Engines   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────┬───────────────────────────────────────────────────┘
               │
     ┌─────────┼──────────┬────────────┐
     │         │          │            │
     ▼         ▼          ▼            ▼
  PostgreSQL  Redis   Celery Workers   ML Models
  (Database)  (Cache)  (Background Jobs) (Serialized)
```

### Modular Architecture

```
backend/
├── app/
│   ├── auth/              # Authentication & Authorization
│   ├── trades/            # Trade Management (CRUD)
│   ├── analytics/         # Analytics Engine & Metrics
│   ├── ml/                # ML Pipeline & Models
│   ├── nlp/               # NLP & Behavioral Analysis
│   ├── database/          # SQLAlchemy ORM Models
│   ├── middleware/        # Custom Middleware
│   ├── utils/             # Helper Functions
│   └── main.py            # FastAPI Application
├── tests/                 # Unit & Integration Tests
├── requirements.txt       # Python Dependencies
└── Dockerfile             # Container Configuration
```

---

## 💻 Tech Stack

### Frontend
- **React.js 18** — Modern, component-based UI framework
- **Redux Toolkit** — State management
- **Tailwind CSS** — Utility-first CSS framework
- **Recharts** — Production-grade charting library
- **Axios** — Promise-based HTTP client
- **React Router** — Client-side routing

### Backend
- **FastAPI** — Modern async web framework with auto-documentation
- **SQLAlchemy** — Powerful ORM for database operations
- **Pydantic** — Data validation using Python type hints
- **PostgreSQL** — ACID-compliant relational database
- **Redis** — In-memory cache and session storage
- **Celery** — Distributed task queue for async processing
- **JWT (python-jose)** — Token-based authentication

### AI/ML
- **Scikit-learn** — Machine learning algorithms
- **Pandas** — Data manipulation and analysis
- **NumPy** — Numerical computing
- **Joblib** — Model serialization

### NLP
- **spaCy** — Industrial-strength NLP
- **TextBlob** — Simple sentiment analysis
- **NLTK** — Natural Language Processing toolkit

### DevOps
- **Docker** — Container orchestration
- **Docker Compose** — Multi-container orchestration
- **Alembic** — Database migrations
- **Pytest** — Testing framework

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd QUANT\ TRACK

# Create environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
alembic upgrade head

# Run backend
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`  
API Documentation: `http://localhost:8000/api/docs`

### 3. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: `http://localhost:3000`

### 4. Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d

# Wait for services to initialize (30-60 seconds)

# Run migrations
docker-compose exec backend alembic upgrade head

# Check logs
docker-compose logs -f
```

**Services**:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

---

## 📚 API Documentation

### Authentication Endpoints

```
POST /api/auth/register
  - Register new user
  - Request: {email, name, password}
  - Response: {user, tokens{access_token, refresh_token}}

POST /api/auth/login
  - Login user
  - Request: {email, password}
  - Response: {user, tokens{access_token, refresh_token}}

POST /api/auth/refresh-token
  - Refresh access token
  - Request: {refresh_token}
  - Response: {access_token, refresh_token, token_type}

GET /api/auth/verify
  - Verify token and get current user
  - Headers: {Authorization: Bearer <token>}
  - Response: {user}
```

### Trade Management Endpoints

```
POST /api/trades
  - Create new trade
  - Request: TradeCreate schema
  - Response: TradeResponse

GET /api/trades
  - List user trades (paginated)
  - Query: {skip, limit, symbol, strategy, session}
  - Response: TradeListResponse

GET /api/trades/{id}
  - Get trade details
  - Response: TradeResponse

PUT /api/trades/{id}
  - Update trade
  - Request: TradeUpdate schema
  - Response: TradeResponse

DELETE /api/trades/{id}
  - Delete trade
  - Response: 204 No Content

GET /api/trades/statistics/summary
  - Get trade statistics
  - Response: TradeStatisticsResponse
```

### Analytics Endpoints

```
GET /api/analytics/summary
  - Get overall metrics summary
  - Response: AnalyticsSummaryResponse

GET /api/analytics/metrics
  - Get detailed metrics by period
  - Query: {period, start_date, end_date}
  - Response: DetailedMetricsResponse

GET /api/analytics/equity-curve
  - Get equity curve data for charting
  - Response: List of {date, equity}

GET /api/analytics/drawdown
  - Get drawdown analysis
  - Response: DrawdownAnalysisResponse
```

### ML Endpoints

```
POST /api/ml/predictions
  - Get trade profitability prediction
  - Request: {trade_id}
  - Response: {prediction, confidence_score}

POST /api/ml/risk-detection
  - Detect high-risk trading behavior
  - Request: {user_id, analysis_period}
  - Response: {risk_score, risk_factors}

POST /api/ml/pattern-analysis
  - Cluster and analyze trade patterns
  - Response: {patterns, clusters}
```

### Journal Endpoints

```
POST /api/journals
  - Create journal entry
  - Request: {trade_id, notes, emotional_state}
  - Response: JournalResponse

GET /api/journals
  - List journal entries
  - Query: {skip, limit, trade_id}
  - Response: JournalListResponse

GET /api/journals/{id}/analysis
  - Get NLP analysis results
  - Response: NLPAnalysisResponse
```

---

## 🗄️ Database Schema

### Core Tables

**USERS**
```sql
- id (PK)
- email (UNIQUE)
- name
- hashed_password
- is_active
- subscription_tier
- created_at, updated_at
```

**TRADES**
```sql
- id (PK)
- user_id (FK)
- symbol
- direction (LONG/SHORT)
- entry_price, exit_price
- stop_loss, take_profit
- lot_size
- pnl, pnl_percentage
- risk_reward_ratio
- strategy, timeframe
- session (NYSE/NSE/CRYPTO/FOREX)
- emotional_state
- entry_timestamp, exit_timestamp
- is_open
- created_at, updated_at
```

**JOURNALS**
```sql
- id (PK)
- trade_id (FK)
- user_id (FK)
- notes (TEXT)
- emotional_state
- created_at, updated_at
```

**NLP_ANALYSES**
```sql
- id (PK)
- journal_id (FK)
- user_id (FK)
- sentiment_score
- fomo_score, revenge_trade_score, impulsive_score
- fear_greed_pattern
- extracted_keywords (JSON)
- behavior_tags (JSON)
- created_at
```

**ML_PREDICTIONS**
```sql
- id (PK)
- trade_id (FK)
- user_id (FK)
- model_name
- prediction_type
- prediction_value
- confidence_score
- features_used (JSON)
- created_at
```

**ANALYTICS_SUMMARIES**
```sql
- id (PK)
- user_id (FK)
- period (DAILY/WEEKLY/MONTHLY)
- period_date
- metrics_json (JSON)
- generated_at
```

---

## 🤖 Machine Learning Pipeline

### Implemented Models

1. **Profitability Predictor** (Logistic Regression)
   - Predicts if a trade setup is likely to be profitable
   - Input: Trade features (entry/exit ratio, RR ratio, etc.)
   - Output: Probability (0-1)

2. **Risk Detector** (Random Forest)
   - Detects high-risk trading behavior
   - Input: Trade history, emotional states
   - Output: Risk score, contributing factors

3. **Pattern Clusterer** (K-Means)
   - Groups profitable setups by similarity
   - Input: Trade features
   - Output: Cluster assignments, characteristics

### Feature Engineering

```python
Features extracted from trades:
- Risk-Reward Ratio
- Entry/Exit Time Ratio
- Lot Size relative to account
- Time in trade
- Market conditions (volatility)
- Historical win rate
- Strategy performance
- Emotional state correlation
```

### Model Training Pipeline

```python
1. Data Collection → Trades with outcomes
2. Feature Engineering → Extract 20+ features
3. Preprocessing → Scaling, encoding, missing value handling
4. Train/Test Split → 80/20 time-based split
5. Model Training → Fit models on training data
6. Evaluation → Accuracy, precision, recall, AUC
7. Serialization → Save models with joblib
8. Deployment → Load models for inference
```

---

## 🧠 NLP & Behavioral Analysis

### Behavioral Pattern Detection

Analyzes trading journal entries to detect:

1. **FOMO (Fear of Missing Out)**
   - Keywords: "missed", "jumped in", "aggressive"
   - Sentiment: Positive after entry, negative after exit

2. **Revenge Trading**
   - Keywords: "revenge", "get back", "lost"
   - High lot sizes after consecutive losses

3. **Impulsive Trading**
   - Keywords: "suddenly", "impulse", "gut feeling"
   - Low preparation, high emotion

4. **Fear/Greed Patterns**
   - Sentiment analysis: Negative (fear) vs. Positive (greed)
   - Emotional intensity from word analysis

### NLP Implementation

```python
1. Text Preprocessing
   - Lowercase, remove special chars
   - Tokenization, stop word removal
   
2. Sentiment Analysis (TextBlob)
   - Polarity: -1 (negative) to +1 (positive)
   - Subjectivity: 0 (objective) to 1 (subjective)

3. Emotion Classification
   - spaCy NER for emotion extraction
   - Custom behavior keyword matching
   
4. Behavioral Tagging
   - Rule-based pattern detection
   - Multi-class classification
```

---

## 📊 Key Metrics Calculated

### Basic Metrics
- **Win Rate** = (Winning Trades / Total Closed Trades) × 100
- **Profit Factor** = (Sum of Wins / Sum of Losses)
- **Average RR Ratio** = Mean of all risk-reward ratios
- **Total P&L** = Sum of all trade P&Ls

### Advanced Metrics
- **Max Drawdown** = Maximum cumulative loss from peak
- **Sharpe Ratio** = (Mean Return - Risk-free Rate) / Std Dev
- **Expectancy** = (Win% × Avg Win) - (Loss% × Avg Loss)
- **Recovery Factor** = Total P&L / Max Drawdown

### Analytics Summaries
- Daily/Weekly/Monthly aggregations
- Strategy-wise performance breakdown
- Session-wise performance analysis
- Emotional state correlation with outcomes

---

## 🔐 Security Features

### Authentication & Authorization
- ✅ JWT tokens with 15-minute access, 7-day refresh expiry
- ✅ Bcrypt password hashing (12+ rounds)
- ✅ Stateless authentication
- ✅ Rate limiting on login/register (5 attempts/5 min)
- ✅ CORS configuration

### Data Protection
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (Pydantic validation)
- ✅ CSRF protection (SameSite cookies)
- ✅ HTTPS enforcement (in production)
- ✅ Environment variables for secrets

### API Security
- ✅ Input validation on all endpoints
- ✅ Request body size limits
- ✅ User isolation (can only access own data)
- ✅ Audit logging for sensitive operations

---

## 📈 Deployment

### Development Environment

```bash
docker-compose up -d
```

### Production Deployment

#### Option 1: AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. Install Docker, Docker Compose
# 3. Clone repository
# 4. Configure .env for production
# 5. Set up RDS PostgreSQL
# 6. Set up ElastiCache Redis
# 7. Deploy with Docker Compose

docker-compose up -d
```

#### Option 2: Heroku

```bash
# 1. Create Heroku app
heroku create quanttrack-app

# 2. Add PostgreSQL addon
heroku addons:create heroku-postgresql

# 3. Deploy
git push heroku main
```

#### Option 3: Kubernetes

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for Kubernetes setup.

---

## 🧪 Testing

### Run Tests

```bash
# Backend tests
cd backend
pytest tests/

# With coverage
pytest --cov=app tests/

# Frontend tests
cd frontend
npm test
```

### Test Structure

```
backend/tests/
├── test_auth.py          # Authentication tests
├── test_trades.py        # Trade CRUD tests
├── test_analytics.py     # Analytics calculations
├── test_ml.py            # ML model tests
├── test_nlp.py           # NLP analysis tests
└── conftest.py           # Test fixtures
```

---

## 📝 Project Structure

```
QUANT TRACK/
│
├── ARCHITECTURE.md                      # System architecture document
├── README.md                            # This file
├── docker-compose.yml                   # Docker Compose configuration
├── .env.example                         # Environment variables template
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI app entry point
│   │   ├── config.py                    # Configuration management
│   │   │
│   │   ├── auth/                        # Authentication module
│   │   │   ├── security.py              # JWT, password hashing
│   │   │   ├── service.py               # Auth business logic
│   │   │   ├── schemas.py               # Pydantic models
│   │   │   ├── dependencies.py          # FastAPI dependencies
│   │   │   ├── router.py                # API endpoints
│   │   │   └── __init__.py
│   │   │
│   │   ├── trades/                      # Trade management module
│   │   │   ├── service.py               # Trade business logic
│   │   │   ├── schemas.py               # Pydantic models
│   │   │   ├── router.py                # API endpoints
│   │   │   └── __init__.py
│   │   │
│   │   ├── analytics/                   # Analytics engine
│   │   │   ├── metrics/                 # Metric calculation
│   │   │   ├── calculators/             # Advanced calculators
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── ml/                          # ML pipeline
│   │   │   ├── models/                  # Model implementations
│   │   │   ├── feature_engineering.py
│   │   │   ├── preprocessing.py
│   │   │   ├── model_storage/           # Serialized models
│   │   │   └── __init__.py
│   │   │
│   │   ├── nlp/                         # NLP & behavioral analysis
│   │   │   ├── analyzers/               # Sentiment, emotion, etc.
│   │   │   ├── service.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── database/                    # Database layer
│   │   │   ├── models.py                # SQLAlchemy models
│   │   │   ├── session.py               # DB session management
│   │   │   └── __init__.py
│   │   │
│   │   ├── middleware/                  # Custom middleware
│   │   ├── utils/                       # Helper functions
│   │   │   ├── helpers.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   │
│   ├── tests/                           # Backend tests
│   │   ├── test_auth.py
│   │   ├── test_trades.py
│   │   └── conftest.py
│   │
│   ├── requirements.txt                 # Python dependencies
│   ├── Dockerfile                       # Backend container
│   └── .dockerignore
│
├── frontend/
│   ├── src/
│   │   ├── App.js                       # Main App component
│   │   ├── index.js                     # React entry point
│   │   │
│   │   ├── components/                  # Reusable components
│   │   │   ├── Navbar.js
│   │   │   ├── Sidebar.js
│   │   │   ├── TradeForm.js
│   │   │   ├── Chart.js
│   │   │   └── ...
│   │   │
│   │   ├── pages/                       # Page components
│   │   │   ├── Dashboard.js
│   │   │   ├── TradesPage.js
│   │   │   ├── AnalyticsPage.js
│   │   │   ├── LoginPage.js
│   │   │   └── ...
│   │   │
│   │   ├── services/                    # API & utilities
│   │   │   ├── api.js                   # Axios API client
│   │   │   └── ...
│   │   │
│   │   ├── store/                       # Redux state
│   │   │   ├── index.js
│   │   │   └── slices/
│   │   │       ├── authSlice.js
│   │   │       ├── tradesSlice.js
│   │   │       └── analyticsSlice.js
│   │   │
│   │   ├── hooks/                       # Custom hooks
│   │   ├── utils/                       # Utilities
│   │   └── styles/
│   │       └── globals.css
│   │
│   ├── public/
│   │   └── index.html
│   │
│   ├── package.json                     # Dependencies
│   ├── Dockerfile                       # Frontend container
│   └── tailwind.config.js               # Tailwind config
│
├── datasets/                            # Sample data
│   ├── sample_trades.csv
│   └── test_journals.json
│
├── notebooks/                           # Jupyter notebooks
│   ├── ml_exploration.ipynb
│   ├── nlp_analysis.ipynb
│   └── data_analysis.ipynb
│
├── docs/                                # Documentation
│   ├── API.md                           # API reference
│   ├── DEPLOYMENT.md                    # Deployment guide
│   ├── DATABASE.md                      # Database schema
│   ├── ML_PIPELINE.md                   # ML documentation
│   └── NLP_ANALYSIS.md                  # NLP documentation
│
└── alembic/                             # Database migrations
    ├── env.py
    ├── alembic.ini
    └── versions/
```

---

## 🎓 Learning Resources

### Key Implementation Patterns

1. **Service Layer Pattern**
   - Separates business logic from API routes
   - Makes testing easier
   - Improves code reusability

2. **Repository Pattern**
   - Abstracts database queries
   - Makes database implementation switchable
   - Improves testing

3. **Dependency Injection**
   - FastAPI dependencies for database sessions
   - Cleaner code, easier testing

4. **Async/Await**
   - FastAPI async support for I/O operations
   - Better scalability

---

## 👥 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🚀 Future Enhancements

### Phase 2 Features

- [ ] Advanced charting with TradingView integration
- [ ] Real-time trade alerts and notifications
- [ ] Multi-user team collaboration
- [ ] Advanced portfolio analysis
- [ ] Market data integration (Yahoo Finance, Alpha Vantage)
- [ ] Automated trade recording from brokers
- [ ] Mobile app (React Native)
- [ ] Backtesting engine
- [ ] Advanced ML models (Deep Learning, LSTM)

### Phase 3 Features

- [ ] Social trading (share strategies)
- [ ] AI trading coach
- [ ] Broker integration APIs
- [ ] Advanced options analytics
- [ ] Risk management tools
- [ ] Market sentiment analysis
- [ ] Community features
- [ ] Premium features & subscriptions

---

## 📞 Support

For support, email support@quanttrack.com or open an issue on GitHub.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) and [React](https://react.dev/)
- Analytics powered by [scikit-learn](https://scikit-learn.org/)
- NLP by [spaCy](https://spacy.io/)
- Hosted with [Docker](https://www.docker.com/)

---

**Made with ❤️ by the QuantTrack Team**

---

**Last Updated**: May 2024  
**Version**: 1.0.0
