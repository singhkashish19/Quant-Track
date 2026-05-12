# DATABASE SCHEMA & MIGRATIONS

## Overview

QuantTrack uses PostgreSQL with SQLAlchemy ORM. Database migrations are managed with Alembic.

---

## Database Tables

### USERS Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    subscription_tier VARCHAR(50) DEFAULT 'free',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_email (email),
    INDEX idx_user_is_active (is_active)
);
```

### TRADES Table
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    direction VARCHAR(10) NOT NULL, -- LONG or SHORT
    entry_price FLOAT NOT NULL,
    exit_price FLOAT,
    stop_loss FLOAT,
    take_profit FLOAT,
    lot_size FLOAT NOT NULL,
    pnl FLOAT,
    pnl_percentage FLOAT,
    risk_reward_ratio FLOAT,
    strategy VARCHAR(100),
    timeframe VARCHAR(10),
    session VARCHAR(20) NOT NULL, -- NYSE, NSE, CRYPTO, FOREX
    emotional_state VARCHAR(20), -- CALM, CONFIDENT, ANXIOUS, FEARFUL, GREEDY, FRUSTRATED
    entry_timestamp TIMESTAMP NOT NULL,
    exit_timestamp TIMESTAMP,
    notes TEXT,
    is_open BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_trade_user_date (user_id, entry_timestamp),
    INDEX idx_trade_symbol_date (symbol, entry_timestamp),
    INDEX idx_trade_strategy (strategy),
    INDEX idx_trade_is_open (is_open)
);
```

### JOURNALS Table
```sql
CREATE TABLE journals (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES trades(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notes TEXT NOT NULL,
    emotional_state VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_journal_user_date (user_id, created_at),
    INDEX idx_journal_trade_id (trade_id)
);
```

### NLP_ANALYSES Table
```sql
CREATE TABLE nlp_analyses (
    id SERIAL PRIMARY KEY,
    journal_id INTEGER NOT NULL REFERENCES journals(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sentiment_score FLOAT NOT NULL, -- -1 to 1
    detected_emotions JSON,
    fomo_score FLOAT DEFAULT 0.0,
    revenge_trade_score FLOAT DEFAULT 0.0,
    impulsive_score FLOAT DEFAULT 0.0,
    fear_greed_pattern VARCHAR(50),
    extracted_keywords JSON,
    behavior_tags JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (journal_id) REFERENCES journals(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_nlp_user_date (user_id, created_at),
    INDEX idx_nlp_journal_id (journal_id)
);
```

### ML_PREDICTIONS Table
```sql
CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER NOT NULL REFERENCES trades(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_name VARCHAR(100) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL, -- profitability, risk, pattern
    prediction_value FLOAT NOT NULL,
    confidence_score FLOAT NOT NULL,
    features_used JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_prediction_user_trade (user_id, trade_id),
    INDEX idx_prediction_model (model_name)
);
```

### ANALYTICS_SUMMARIES Table
```sql
CREATE TABLE analytics_summaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    period VARCHAR(20) NOT NULL, -- DAILY, WEEKLY, MONTHLY
    period_date TIMESTAMP NOT NULL,
    metrics_json JSON NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_analytics_user_period (user_id, period, period_date)
);
```

---

## Entity Relationships

```
USERS (1) ──────────── (N) TRADES
  │                       │
  │                       ├─── (1) JOURNALS
  │                       │      │
  │                       │      └─── (1) NLP_ANALYSES
  │                       │
  │                       └─── (N) ML_PREDICTIONS
  │
  ├─── (N) JOURNALS
  ├─── (N) ML_PREDICTIONS
  └─── (N) ANALYTICS_SUMMARIES
```

---

## Migrations

### Running Migrations

```bash
# Initialize Alembic (first time only)
cd backend
alembic init migrations

# Create a new migration
alembic revision --autogenerate -m "Add trades table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Migration File Structure

```python
# migrations/versions/001_initial_schema.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('users')
```

---

## Indexing Strategy

### Performance-Critical Indexes

| Table | Columns | Purpose |
|-------|---------|---------|
| trades | (user_id, entry_timestamp) | Fast user trade queries by date |
| trades | (symbol, entry_timestamp) | Symbol performance analysis |
| trades | (strategy) | Strategy filtering |
| journals | (user_id, created_at) | User journal timeline |
| nlp_analyses | (user_id, created_at) | Analysis history |
| analytics_summaries | (user_id, period, period_date) | Time-series queries |

### Composite Indexes

```sql
-- Fast queries for user trades in date range
CREATE INDEX idx_trades_user_period 
ON trades(user_id, entry_timestamp DESC);

-- Strategy performance analysis
CREATE INDEX idx_trades_strategy_user 
ON trades(user_id, strategy, entry_timestamp);

-- Win/loss analysis
CREATE INDEX idx_trades_user_pnl 
ON trades(user_id, pnl DESC);
```

---

## JSON Columns

### NLP_ANALYSES.detected_emotions
```json
{
  "fear": 0.8,
  "greed": 0.3,
  "overconfidence": 0.5,
  "regret": 0.2
}
```

### NLP_ANALYSES.extracted_keywords
```json
{
  "keywords": ["FOMO", "support", "resistance"],
  "frequency": [3, 2, 1],
  "importance_score": [0.9, 0.7, 0.6]
}
```

### ML_PREDICTIONS.features_used
```json
{
  "rr_ratio": 2.5,
  "entry_exit_ratio": 0.015,
  "lot_size_ratio": 0.02,
  "emotional_state": "CONFIDENT",
  "time_in_trade_hours": 1.5
}
```

### ANALYTICS_SUMMARIES.metrics_json
```json
{
  "total_trades": 42,
  "win_rate": 0.619,
  "profit_factor": 2.3,
  "max_drawdown": -1250.0,
  "sharpe_ratio": 1.45,
  "expectancy": 95.50,
  "largest_win": 1250.0,
  "largest_loss": -850.0
}
```

---

## Data Retention Policy

| Table | Retention | Notes |
|-------|-----------|-------|
| TRADES | Permanent | Core trading data |
| JOURNALS | Permanent | Journal entries |
| ML_PREDICTIONS | 1 year | Archive old predictions |
| NLP_ANALYSES | 1 year | Archive old analyses |
| ANALYTICS_SUMMARIES | 2 years | Keep summaries longer |

---

## Backup Strategy

### Daily Backups
```bash
# Automatic backup using pg_dump
pg_dump quanttrack_db > backup_$(date +%Y%m%d).sql
```

### Backup Retention
- Keep last 30 daily backups
- Keep last 12 weekly backups
- Keep last 24 monthly backups

---

## Query Optimization Tips

### Slow Query Analysis
```sql
-- Find slow queries
SELECT query, calls, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;

-- Analyze query plan
EXPLAIN ANALYZE 
SELECT * FROM trades WHERE user_id = 1 AND created_at > NOW() - INTERVAL '30 days';
```

### Common Optimization Patterns

```sql
-- Efficient pagination
SELECT * FROM trades 
WHERE user_id = 1 
ORDER BY entry_timestamp DESC 
LIMIT 50 OFFSET 0;

-- Efficient filtering
SELECT * FROM trades 
WHERE user_id = 1 
  AND strategy = 'Breakout' 
  AND entry_timestamp BETWEEN DATE '2024-01-01' AND DATE '2024-12-31';

-- Aggregation query
SELECT 
    strategy,
    COUNT(*) as trade_count,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl
FROM trades 
WHERE user_id = 1 
GROUP BY strategy
ORDER BY total_pnl DESC;
```

---

**Database Schema Last Updated**: May 2024
