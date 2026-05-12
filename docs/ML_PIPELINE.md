# ML Pipeline Implementation Guide

## Overview

The ML pipeline consists of three models working together to provide trading intelligence:

1. **Profitability Predictor** - Predicts if a trade will be profitable
2. **Risk Detector** - Detects risky trading patterns
3. **Pattern Clusterer** - Groups similar trades for strategy analysis

---

## Architecture

```
Raw Trade Data
    ↓
Feature Engineering
    ├─→ [Technical Features]
    ├─→ [Risk Features]
    ├─→ [Behavioral Features]
    ├─→ [Statistical Features]
    ↓
Feature Normalization
    ↓
Model Pipeline
    ├─→ Profitability Predictor (Logistic Regression)
    ├─→ Risk Detector (Random Forest)
    └─→ Pattern Clusterer (K-Means)
    ↓
Predictions & Insights
```

---

## Feature Engineering

### Technical Features
```python
def engineer_technical_features(trade):
    return {
        'entry_exit_ratio': (trade.exit_price - trade.entry_price) / trade.entry_price,
        'lot_size_ratio': trade.lot_size / 100,  # Normalized
        'rr_ratio': calculate_rr_ratio(trade),
        'time_in_trade': calculate_time_in_hours(trade),
        'volatility_estimate': estimate_volatility(trade)
    }
```

### Risk Features
```python
def engineer_risk_features(trade):
    return {
        'stop_loss_distance': abs(trade.entry_price - trade.stop_loss) / trade.entry_price,
        'take_profit_distance': abs(trade.take_profit - trade.entry_price) / trade.entry_price,
        'position_size_pct': (trade.lot_size * trade.entry_price) / 10000,
        'risk_amount': abs(trade.entry_price - trade.stop_loss) * trade.lot_size
    }
```

### Behavioral Features
```python
def engineer_behavioral_features(trade, user_trades):
    return {
        'emotional_state_encoded': encode_emotional_state(trade.emotional_state),
        'time_since_last_trade': calculate_time_since_last_trade(trade, user_trades),
        'consecutive_losses': calculate_consecutive_losses(trade, user_trades),
        'win_rate_at_time': calculate_running_win_rate(trade, user_trades)
    }
```

---

## Model 1: Profitability Predictor

### Algorithm
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class ProfitabilityPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = LogisticRegression(random_state=42)
    
    def train(self, X_train, y_train):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled, y_train)
    
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]
```

### Input Features
- Entry/exit price ratio
- Risk-reward ratio
- Lot size
- Time in trade
- Emotional state
- Win rate at time of trade

### Output
- Probability of trade being profitable (0-1)
- Confidence score

### Training Data
- Requires 50+ trades with known outcomes
- Binary classification (won/lost)

---

## Model 2: Risk Detector

### Algorithm
```python
from sklearn.ensemble import RandomForestClassifier

class RiskDetector:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X):
        # Returns risk score (0-1, higher = riskier)
        risk_scores = self.model.predict_proba(X)[:, 1]
        return risk_scores
```

### Input Features
- Stop loss distance
- Take profit distance
- Position size
- Risk amount
- Consecutive losses
- Volatility estimate

### Output
- Risk score (0-1)
- Risk level (Low/Medium/High)

### Risk Thresholds
- Low: 0.0 - 0.33
- Medium: 0.33 - 0.67
- High: 0.67 - 1.0

---

## Model 3: Pattern Clusterer

### Algorithm
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class PatternClusterer:
    def __init__(self, n_clusters=5):
        self.scaler = StandardScaler()
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.cluster_names = {}
    
    def train(self, X_train):
        X_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_scaled)
    
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
```

### Input Features
- All technical features
- All risk features
- All behavioral features

### Output
- Cluster ID (0-4)
- Pattern name
- Cluster characteristics

### Cluster Interpretation
- Cluster 0: "High Risk, High Reward" trades
- Cluster 1: "Conservative" trades
- Cluster 2: "Scalping" trades
- Cluster 3: "Swing" trades
- Cluster 4: "Outlier" trades

---

## Implementation Steps

### Step 1: Data Collection
```python
def prepare_training_data(user_id, db):
    trades = db.query(Trade).filter(
        Trade.user_id == user_id,
        Trade.is_open == False
    ).all()
    
    features = []
    labels = []
    
    for trade in trades:
        X = engineer_all_features(trade, trades)
        y = 1 if trade.pnl > 0 else 0
        features.append(X)
        labels.append(y)
    
    return np.array(features), np.array(labels)
```

### Step 2: Model Training
```python
def train_ml_pipeline(user_id, db):
    X, y = prepare_training_data(user_id, db)
    
    # Only train if we have enough data
    if len(X) < 30:
        return None
    
    # Train profitability predictor
    profit_model = ProfitabilityPredictor()
    profit_model.train(X, y)
    
    # Train risk detector
    risk_labels = [1 if trade.pnl < -1000 else 0 for trade in trades]
    risk_model = RiskDetector()
    risk_model.train(X, np.array(risk_labels))
    
    # Train pattern clusterer
    pattern_model = PatternClusterer(n_clusters=5)
    pattern_model.train(X)
    
    return profit_model, risk_model, pattern_model
```

### Step 3: Model Persistence
```python
import joblib

def save_models(user_id, models):
    profit_model, risk_model, pattern_model = models
    
    joblib.dump(
        profit_model,
        f'ml/model_storage/profitability_{user_id}.joblib'
    )
    joblib.dump(
        risk_model,
        f'ml/model_storage/risk_{user_id}.joblib'
    )
    joblib.dump(
        pattern_model,
        f'ml/model_storage/pattern_{user_id}.joblib'
    )

def load_models(user_id):
    profit_model = joblib.load(
        f'ml/model_storage/profitability_{user_id}.joblib'
    )
    risk_model = joblib.load(
        f'ml/model_storage/risk_{user_id}.joblib'
    )
    pattern_model = joblib.load(
        f'ml/model_storage/pattern_{user_id}.joblib'
    )
    
    return profit_model, risk_model, pattern_model
```

### Step 4: Making Predictions
```python
def predict_on_new_trade(trade, user_id, db):
    models = load_models(user_id)
    
    if models is None:
        return None
    
    profit_model, risk_model, pattern_model = models
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    X = engineer_all_features(trade, trades)
    
    predictions = {
        'profitability_score': profit_model.predict(X)[0],
        'risk_score': risk_model.predict(X)[0],
        'pattern_cluster': pattern_model.predict(X)[0]
    }
    
    return predictions
```

---

## Retraining Schedule

### Weekly Retraining
```python
from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def retrain_ml_models():
    users = db.query(User).filter(User.is_active == True).all()
    
    for user in users:
        # Check if user has 10+ new trades since last training
        last_train = get_last_training_date(user.id)
        new_trades = db.query(Trade).filter(
            Trade.user_id == user.id,
            Trade.created_at > last_train,
            Trade.is_open == False
        ).count()
        
        if new_trades >= 10:
            models = train_ml_pipeline(user.id, db)
            save_models(user.id, models)
            log_training_event(user.id)
```

---

## Model Performance Evaluation

### Metrics
```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    return {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'auc_roc': roc_auc_score(y_test, y_pred_proba)
    }
```

### Validation
- Use cross-validation with k=5 folds
- Maintain out-of-sample test set (20% of data)
- Track metrics over time

---

## API Endpoints

### Get Prediction for New Trade
```
POST /api/ml/predictions
Authorization: Bearer <token>

Request:
{
  "symbol": "AAPL",
  "direction": "LONG",
  "entry_price": 150.25,
  "lot_size": 100,
  "stop_loss": 149.00,
  "take_profit": 155.00
}

Response:
{
  "profitability_score": 0.72,
  "profitability_label": "HIGH",
  "risk_score": 0.45,
  "risk_label": "MEDIUM",
  "pattern_cluster": 1,
  "pattern_name": "Conservative",
  "confidence": 0.85,
  "recommendation": "GO - Good setup with moderate risk"
}
```

### Get Model Performance
```
GET /api/ml/performance
Authorization: Bearer <token>

Response:
{
  "model_accuracy": 0.78,
  "trades_analyzed": 150,
  "last_retrained": "2024-05-15T10:30:00",
  "model_age_days": 7,
  "metrics": {
    "profitability": {
      "accuracy": 0.78,
      "precision": 0.81,
      "recall": 0.75
    },
    "risk": {
      "accuracy": 0.82,
      "precision": 0.79,
      "recall": 0.84
    }
  }
}
```

---

**ML Pipeline Guide Last Updated**: May 2024
