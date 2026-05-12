# QuantTrack Dataset Strategy

QuantTrack uses a hybrid dataset architecture:

- `trades.csv`: completed trade history with market, execution, risk, and behavioral labels.
- `journals.csv`: self-labeled journal text for sentiment, emotion, and behavioral NLP.
- `engineered_features.csv`: rolling features generated from trade history for ML models.

Generate local demo data:

```bash
python datasets/generate_synthetic_data.py
```

The generator is deterministic by default and produces realistic placement-demo data for XAUUSD, BTCUSD, EURUSD, NAS100, and US30.
