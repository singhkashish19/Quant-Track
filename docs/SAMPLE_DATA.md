# Sample Data Generator

This script generates sample trades and journal entries for testing and development.

## Usage

```bash
cd backend
python -m scripts.generate_sample_data
```

## Generated Data

- 1 test user (test@example.com)
- 50 sample trades with various outcomes
- 30 journal entries with NLP analysis
- 10 ML predictions

## Data

**Test User**
- Email: test@example.com
- Password: TestPassword123!
- ID: 1

**Sample Trades**
- Mix of winning and losing trades
- Various strategies (Breakout, Scalping, Support/Resistance)
- Different emotional states
- Multiple symbols and timeframes

**Sample Journals**
- Behavioral patterns
- Emotional notes
- Strategy reflections

---

## Script Code

```python
# backend/scripts/generate_sample_data.py

import sys
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

sys.path.append('..')

from app.database import SessionLocal, init_db
from app.database.models import (
    User, Trade, Journal, NLPAnalysis,
    TradeDirection, TradeSession, EmotionalState
)
from app.auth.security import hash_password
from app.utils.helpers import calculate_pnl

def generate_sample_data():
    """Generate sample data for development and testing."""
    
    db = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Create test user
        user = User(
            email="test@example.com",
            name="Test Trader",
            hashed_password=hash_password("TestPassword123!"),
            is_active=True,
            subscription_tier="pro"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created test user: {user.email}")
        
        # Generate 50 sample trades
        strategies = ["Breakout", "Scalping", "Support/Resistance", "Trend Following", "Mean Reversion"]
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "BTC/USD", "ETH/USD"]
        
        trades = []
        for i in range(50):
            direction = random.choice([TradeDirection.LONG, TradeDirection.SHORT])
            entry_price = random.uniform(100, 200)
            
            # 65% winning rate
            if random.random() < 0.65:
                if direction == TradeDirection.LONG:
                    exit_price = entry_price * random.uniform(1.01, 1.05)
                else:
                    exit_price = entry_price * random.uniform(0.95, 0.99)
            else:
                if direction == TradeDirection.LONG:
                    exit_price = entry_price * random.uniform(0.95, 0.99)
                else:
                    exit_price = entry_price * random.uniform(1.01, 1.05)
            
            lot_size = random.choice([10, 20, 50, 100])
            pnl, pnl_percentage = calculate_pnl(entry_price, exit_price, lot_size, direction.value)
            
            entry_time = datetime.utcnow() - timedelta(days=random.randint(1, 60))
            exit_time = entry_time + timedelta(hours=random.uniform(0.5, 8))
            
            trade = Trade(
                user_id=user.id,
                symbol=random.choice(symbols),
                direction=direction,
                entry_price=entry_price,
                exit_price=exit_price,
                stop_loss=entry_price - 5,
                take_profit=entry_price + 10,
                lot_size=lot_size,
                pnl=pnl,
                pnl_percentage=pnl_percentage,
                strategy=random.choice(strategies),
                timeframe=random.choice(["5M", "15M", "1H", "4H", "1D"]),
                session=TradeSession.NYSE,
                emotional_state=random.choice(list(EmotionalState)),
                entry_timestamp=entry_time,
                exit_timestamp=exit_time,
                is_open=False,
                notes=f"Sample trade #{i+1}"
            )
            
            db.add(trade)
            trades.append(trade)
        
        db.commit()
        print(f"✅ Created {len(trades)} sample trades")
        
        # Generate journals for some trades
        journal_samples = [
            "Entered too early, should have waited for confirmation.",
            "Great execution on this breakout setup. Market conditions were perfect.",
            "Got scared and exited too soon. I had a stop loss but panicked.",
            "This was a revenge trade after losing the previous one. Bad decision.",
            "Following the plan perfectly. Emotional control was excellent today.",
            "Impulsive entry. Didn't have a clear setup. Got lucky with the exit.",
            "High conviction setup. FOMO kicked in, but managed to exit on profits.",
        ]
        
        for trade in trades[:30]:
            journal = Journal(
                trade_id=trade.id,
                user_id=user.id,
                notes=random.choice(journal_samples),
                emotional_state=trade.emotional_state
            )
            db.add(journal)
        
        db.commit()
        print("✅ Created sample journals")
        
        print("\n✨ Sample data generation complete!")
        print(f"Test credentials:")
        print(f"  Email: test@example.com")
        print(f"  Password: TestPassword123!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_sample_data()
```

---

## Creating Sample Data

```bash
# Create the scripts directory
mkdir -p backend/scripts
touch backend/scripts/__init__.py
```

Save the script above to `backend/scripts/generate_sample_data.py`

Then run:
```bash
cd backend
python scripts/generate_sample_data.py
```

---

## Reset Sample Data

```bash
# Drop all data and recreate
python -c "from app.database import drop_db, init_db; drop_db(); init_db()"

# Then generate new sample data
python scripts/generate_sample_data.py
```

---

**Sample Data Generator Last Updated**: May 2024
