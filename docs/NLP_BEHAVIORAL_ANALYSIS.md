# NLP & Behavioral Analysis Implementation Guide

## Overview

The NLP module analyzes trader journals and emotional patterns to provide behavioral insights and detect risky trading behaviors.

---

## Architecture

```
Journal Entry (Text)
    ↓
Text Preprocessing
    ├─→ Tokenization
    ├─→ Lemmatization
    ├─→ Cleaning
    ↓
Analysis Pipeline
    ├─→ Sentiment Analysis (TextBlob)
    ├─→ Emotion Detection (Custom Classifier)
    ├─→ Behavioral Pattern Detection
    ├─→ Risk Pattern Flagging
    ↓
Insights Generation
    ├─→ Behavioral Flags
    ├─→ Pattern Tags
    ├─→ Risk Warnings
    └─→ Recommendations
```

---

## Component 1: Sentiment Analysis

### Implementation
```python
from textblob import TextBlob

class SentimentAnalyzer:
    @staticmethod
    def analyze(text):
        """
        Returns sentiment score between -1 (negative) and 1 (positive)
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        return {
            'sentiment_score': polarity,
            'sentiment_label': SentimentAnalyzer.get_label(polarity),
            'subjectivity': blob.sentiment.subjectivity
        }
    
    @staticmethod
    def get_label(score):
        if score < -0.5:
            return 'VERY_NEGATIVE'
        elif score < -0.1:
            return 'NEGATIVE'
        elif score < 0.1:
            return 'NEUTRAL'
        elif score < 0.5:
            return 'POSITIVE'
        else:
            return 'VERY_POSITIVE'
```

### Metrics
- **Polarity**: -1 to 1 (negative to positive)
- **Subjectivity**: 0 to 1 (objective to subjective)

---

## Component 2: Emotion Detection

### Emotions Detected
```python
EMOTIONS = {
    'fear': ['worried', 'scared', 'terrified', 'panic', 'nervous'],
    'greed': ['money', 'rich', 'profit', 'make', 'huge', 'fortune'],
    'overconfidence': ['perfect', 'genius', 'best', 'easy', 'guaranteed'],
    'regret': ['should', 'wish', 'mistake', 'bad', 'wrong', 'failed'],
    'fomo': ['fomo', 'missed', 'late', 'others', 'everyone', 'jump'],
    'frustration': ['angry', 'mad', 'frustrated', 'upset', 'annoyed']
}
```

### Implementation
```python
class EmotionDetector:
    @staticmethod
    def detect(text):
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, keywords in EMOTIONS.items():
            score = sum(text_lower.count(kw) for kw in keywords)
            emotion_scores[emotion] = score
        
        # Normalize
        total = sum(emotion_scores.values())
        if total > 0:
            emotion_scores = {
                k: v/total for k, v in emotion_scores.items()
            }
        
        return emotion_scores
```

---

## Component 3: Behavioral Pattern Detection

### Risky Patterns

#### Pattern 1: FOMO (Fear of Missing Out)
```python
def detect_fomo(text, recent_trades):
    """Detect if trader is experiencing FOMO"""
    fomo_keywords = ['fomo', 'missed', 'everyone', 'jump', 'quickly']
    has_fomo_words = any(kw in text.lower() for kw in fomo_keywords)
    
    # Check if entering after recent wins
    recent_winners = sum(1 for t in recent_trades[-5:] if t.pnl > 0)
    fomo_score = 0.0
    
    if has_fomo_words:
        fomo_score += 0.5
    if recent_winners >= 3:
        fomo_score += 0.3
    
    return min(fomo_score, 1.0)
```

#### Pattern 2: Revenge Trading
```python
def detect_revenge_trading(trade, previous_trades):
    """Detect if trader is revenge trading after loss"""
    # Check if previous trade was a loss
    if previous_trades and previous_trades[-1].pnl < 0:
        # Check if current trade is larger and/or riskier
        is_larger = trade.lot_size > previous_trades[-1].lot_size
        is_riskier = (trade.entry_price - trade.stop_loss) < \
                     (previous_trades[-1].entry_price - previous_trades[-1].stop_loss)
        
        if is_larger or is_riskier:
            return 0.8
    
    return 0.0
```

#### Pattern 3: Impulsive Trading
```python
def detect_impulsive_trading(text, trade_frequency):
    """Detect impulsive, emotional trading"""
    impulsive_words = ['suddenly', 'quickly', 'impulse', 'gut', 'feeling']
    has_impulsive_words = any(kw in text.lower() for kw in impulsive_words)
    
    # Check trading frequency
    trades_per_day = trade_frequency  # Should be < 5 for non-scalpers
    
    impulsive_score = 0.0
    if has_impulsive_words:
        impulsive_score += 0.5
    if trades_per_day > 10:
        impulsive_score += 0.3
    
    return min(impulsive_score, 1.0)
```

---

## Component 4: Behavioral Flags

### High Priority Flags
```python
BEHAVIORAL_FLAGS = {
    'FOMO_DETECTED': {
        'severity': 'HIGH',
        'description': 'Fear of missing out detected',
        'recommendation': 'Take a break, follow your plan'
    },
    'REVENGE_TRADING': {
        'severity': 'CRITICAL',
        'description': 'Attempting to recover losses with aggressive trading',
        'recommendation': 'STOP trading immediately, review what went wrong'
    },
    'OVERCONFIDENCE': {
        'severity': 'HIGH',
        'description': 'Overconfidence in abilities detected',
        'recommendation': 'Stick to your rules, reduce position size'
    },
    'PANIC_SELLING': {
        'severity': 'HIGH',
        'description': 'Panic exiting positions due to fear',
        'recommendation': 'Trust your stop loss, maintain discipline'
    },
    'EXCESSIVE_TRADING': {
        'severity': 'MEDIUM',
        'description': 'Trading too frequently',
        'recommendation': 'Quality over quantity, trade your setups only'
    }
}
```

---

## Component 5: Journal Analysis Pipeline

### Complete Analysis
```python
from typing import Dict, List

class JournalAnalyzer:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotion_detector = EmotionDetector()
    
    def analyze_journal(self, journal_text: str, trade, db) -> Dict:
        # Get user's recent trades
        recent_trades = db.query(Trade).filter(
            Trade.user_id == trade.user_id,
            Trade.created_at > datetime.utcnow() - timedelta(days=7)
        ).order_by(Trade.created_at.desc()).limit(10).all()
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze(journal_text)
        
        # Emotion detection
        emotions = self.emotion_detector.detect(journal_text)
        
        # Behavioral patterns
        behavioral_flags = self._detect_behaviors(
            journal_text, trade, recent_trades
        )
        
        return {
            'sentiment': sentiment,
            'emotions': emotions,
            'behavioral_flags': behavioral_flags,
            'overall_risk_score': self._calculate_risk_score(
                sentiment, emotions, behavioral_flags
            ),
            'recommendations': self._generate_recommendations(
                sentiment, emotions, behavioral_flags
            )
        }
    
    def _detect_behaviors(self, text: str, trade, recent_trades: List) -> List:
        flags = []
        
        fomo_score = detect_fomo(text, recent_trades)
        if fomo_score > 0.6:
            flags.append({
                'flag': 'FOMO_DETECTED',
                'score': fomo_score
            })
        
        revenge_score = detect_revenge_trading(trade, recent_trades)
        if revenge_score > 0.6:
            flags.append({
                'flag': 'REVENGE_TRADING',
                'score': revenge_score
            })
        
        impulsive_score = detect_impulsive_trading(
            text, len(recent_trades) / 7  # trades per day
        )
        if impulsive_score > 0.6:
            flags.append({
                'flag': 'IMPULSIVE_TRADING',
                'score': impulsive_score
            })
        
        return flags
    
    def _calculate_risk_score(self, sentiment, emotions, flags) -> float:
        score = 0.0
        
        # Negative sentiment increases risk
        score += abs(sentiment['sentiment_score']) * 0.3
        
        # Negative emotions increase risk
        score += (emotions.get('fear', 0) + emotions.get('greed', 0)) * 0.3
        
        # Behavioral flags increase risk
        score += len(flags) * 0.2
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, sentiment, emotions, flags) -> List[str]:
        recommendations = []
        
        if sentiment['sentiment_score'] < -0.5:
            recommendations.append('You\'re in a negative mindset - consider taking a break')
        
        if emotions.get('greed', 0) > 0.3:
            recommendations.append('Greed detected - stick to your profit targets')
        
        if emotions.get('fear', 0) > 0.3:
            recommendations.append('Fear detected - trust your stop losses')
        
        for flag in flags:
            if flag['flag'] in BEHAVIORAL_FLAGS:
                recommendations.append(
                    BEHAVIORAL_FLAGS[flag['flag']]['recommendation']
                )
        
        return recommendations
```

---

## API Endpoints

### Analyze Journal Entry
```
POST /api/journals/{journal_id}/analyze
Authorization: Bearer <token>

Response:
{
  "sentiment": {
    "sentiment_score": 0.35,
    "sentiment_label": "POSITIVE",
    "subjectivity": 0.62
  },
  "emotions": {
    "fear": 0.15,
    "greed": 0.25,
    "overconfidence": 0.10,
    "regret": 0.05,
    "fomo": 0.30,
    "frustration": 0.15
  },
  "behavioral_flags": [
    {
      "flag": "FOMO_DETECTED",
      "score": 0.75,
      "severity": "HIGH"
    }
  ],
  "overall_risk_score": 0.68,
  "recommendations": [
    "Greed detected - stick to your profit targets",
    "FOMO detected - take a break"
  ]
}
```

### Get Behavioral Summary
```
GET /api/journals/analysis/summary?period=week
Authorization: Bearer <token>

Response:
{
  "period": "WEEKLY",
  "analyzed_journals": 12,
  "average_sentiment": 0.25,
  "emotion_distribution": {
    "fear": 0.18,
    "greed": 0.28,
    "overconfidence": 0.12,
    "frustration": 0.22,
    "fomo": 0.35,
    "regret": 0.15
  },
  "top_behavioral_flags": [
    {
      "flag": "FOMO_DETECTED",
      "occurrences": 8,
      "average_score": 0.72
    },
    {
      "flag": "GREED",
      "occurrences": 7,
      "average_score": 0.68
    }
  ],
  "behavioral_improvement": -0.15,
  "insights": [
    "FOMO is your biggest risk - work on patience",
    "Greed has increased - stick to your profit targets",
    "Overall emotional control has decreased"
  ]
}
```

---

## Machine Learning Enhancement

### Training Custom Emotion Classifier
```python
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer

class CustomEmotionClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.model = MultinomialNB()
    
    def train(self, journal_texts, emotion_labels):
        X = self.vectorizer.fit_transform(journal_texts)
        self.model.fit(X, emotion_labels)
    
    def predict(self, text):
        X = self.vectorizer.transform([text])
        probabilities = self.model.predict_proba(X)[0]
        return dict(zip(self.model.classes_, probabilities))
```

---

## Best Practices

1. **Update Analysis Regularly**: Analyze journals within 24 hours of entry
2. **Track Trends**: Monitor emotion patterns over weeks/months
3. **Avoid Bias**: Use objective metrics alongside sentiment analysis
4. **Combine Signals**: Use NLP + trading data for complete picture
5. **Provide Actionable Advice**: Give specific recommendations, not just scores

---

**NLP & Behavioral Analysis Guide Last Updated**: May 2024
