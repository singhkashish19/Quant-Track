"""ML training and inference service for QuantTrack."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models import MLPrediction, Trade
from app.ml.feature_engineering import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERIC_FEATURES,
    FeatureEngineeringService,
)
from app.ml.schemas import (
    FeatureImportanceItem,
    FeatureImportanceResponse,
    ModelMetric,
    ModelPerformanceResponse,
    PredictionRequest,
    PredictionResponse,
    RetrainResponse,
)


class MLService:
    """Trains, persists, and serves lightweight scikit-learn models."""

    MODEL_VERSION = "phase2-sklearn-v1"
    STORAGE_DIR = Path(__file__).resolve().parent / "model_storage"
    MODEL_FILE = STORAGE_DIR / "quanttrack_ml_bundle.joblib"

    @staticmethod
    def retrain(user_id: int, db: Session) -> RetrainResponse:
        bundle = MLService._train_bundle(user_id, db)
        return RetrainResponse(message="Models retrained successfully", performance=MLService._performance_from_bundle(bundle))

    @staticmethod
    def model_performance(user_id: int, db: Session) -> ModelPerformanceResponse:
        bundle = MLService._load_or_train(user_id, db)
        return MLService._performance_from_bundle(bundle)

    @staticmethod
    def feature_importance(user_id: int, db: Session) -> FeatureImportanceResponse:
        bundle = MLService._load_or_train(user_id, db)
        model = bundle["risk_model"].named_steps["model"]
        try:
            names = bundle["risk_model"].named_steps["preprocess"].get_feature_names_out()
        except Exception:
            names = FEATURE_COLUMNS
        importances = getattr(model, "feature_importances_", [])
        ranked = sorted(zip(names, importances), key=lambda item: item[1], reverse=True)[:12]
        return FeatureImportanceResponse(
            model_version=bundle["model_version"],
            top_features=[FeatureImportanceItem(feature=str(name), importance=round(float(score), 4)) for name, score in ranked],
        )

    @staticmethod
    def predict(user_id: int, request: PredictionRequest, db: Session) -> PredictionResponse:
        bundle = MLService._load_or_train(user_id, db)
        trade = MLService._resolve_trade(user_id, request, db)
        history = FeatureEngineeringService.rows_for_user(user_id, db)
        consecutive_losses = MLService._current_consecutive_losses(user_id, db)
        row = FeatureEngineeringService.row_from_trade(trade, history=history, consecutive_losses=consecutive_losses)

        pd = MLService._pd()
        frame = pd.DataFrame([row])[FEATURE_COLUMNS]
        profit_model = bundle["profit_model"]
        risk_model = bundle["risk_model"]
        cluster_model = bundle["cluster_model"]

        profit_probability = float(profit_model.predict_proba(frame)[0][1])
        risk_score = float(risk_model.predict_proba(frame)[0][1])
        cluster = int(cluster_model.predict(frame)[0])
        confidence = round(max(profit_probability, 1 - profit_probability) * (1 - abs(risk_score - 0.5) / 2), 3)
        recommendations = MLService._recommendations(row, profit_probability, risk_score, cluster)
        trade_id = getattr(trade, "id", None) if not isinstance(trade, dict) else trade.get("id")

        if trade_id:
            MLService._persist_prediction(
                user_id=user_id,
                trade_id=trade_id,
                profitability=profit_probability,
                risk_score=risk_score,
                cluster=cluster,
                row=row,
                db=db,
            )

        return PredictionResponse(
            trade_id=trade_id,
            profitability_probability=round(profit_probability, 3),
            risk_score=round(risk_score, 3),
            pattern_cluster=cluster,
            confidence_score=confidence,
            recommendations=recommendations,
            feature_snapshot={key: row[key] for key in FEATURE_COLUMNS if key in row},
            model_version=bundle["model_version"],
        )

    @staticmethod
    def _train_bundle(user_id: int, db: Session) -> dict:
        pd = MLService._pd()
        np = MLService._np()
        joblib = MLService._joblib()
        models = MLService._sklearn()

        rows = FeatureEngineeringService.rows_for_user(user_id, db)
        data_source = "user_trades"
        if len(rows) < 30 or MLService._single_class(rows, "profitable_trade") or MLService._single_class(rows, "high_risk_trader"):
            rows = MLService._load_demo_rows()
            data_source = "demo_hybrid_dataset"

        df = pd.DataFrame(rows)
        for column in FEATURE_COLUMNS:
            if column not in df:
                df[column] = 0 if column in NUMERIC_FEATURES else "unknown"
        df = df.dropna(subset=["profitable_trade", "high_risk_trader"])
        X = df[FEATURE_COLUMNS]
        y_profit = df["profitable_trade"].astype(int)
        y_risk = df["high_risk_trader"].astype(int)

        def make_preprocessor():
            return models["ColumnTransformer"](
                transformers=[
                    ("num", models["StandardScaler"](), NUMERIC_FEATURES),
                    ("cat", models["OneHotEncoder"](handle_unknown="ignore"), CATEGORICAL_FEATURES),
                ]
            )

        profit_model = models["Pipeline"](
            steps=[
                ("preprocess", make_preprocessor()),
                ("model", models["LogisticRegression"](max_iter=1000, class_weight="balanced")),
            ]
        )
        risk_model = models["Pipeline"](
            steps=[
                ("preprocess", make_preprocessor()),
                ("model", models["RandomForestClassifier"](n_estimators=180, random_state=42, class_weight="balanced")),
            ]
        )
        cluster_count = int(min(4, max(2, np.sqrt(len(df)).round())))
        cluster_model = models["Pipeline"](
            steps=[
                ("preprocess", make_preprocessor()),
                ("model", models["KMeans"](n_clusters=cluster_count, random_state=42, n_init=10)),
            ]
        )

        indices = np.arange(len(X))
        stratify_profit = y_profit if y_profit.value_counts().min() >= 2 else None
        train_idx, test_idx = models["train_test_split"](
            indices, test_size=0.25, random_state=42, stratify=stratify_profit
        )
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_profit_train = y_profit.iloc[train_idx]
        y_profit_test = y_profit.iloc[test_idx]
        y_risk_train = y_risk.iloc[train_idx]
        y_risk_test = y_risk.iloc[test_idx]

        profit_model.fit(X_train, y_profit_train)
        risk_model.fit(X_train, y_risk_train)
        cluster_model.fit(X)

        profit_pred = profit_model.predict(X_test)
        risk_pred = risk_model.predict(X_test)
        clusters = cluster_model.predict(X)
        performance = {
            "profitability_model": MLService._metric_dict(y_profit_test, profit_pred),
            "risk_model": MLService._metric_dict(y_risk_test, risk_pred),
            "cluster_distribution": {str(int(label)): int(count) for label, count in pd.Series(clusters).value_counts().sort_index().items()},
        }

        bundle = {
            "model_version": MLService.MODEL_VERSION,
            "trained_at": datetime.now(timezone.utc),
            "training_rows": int(len(df)),
            "data_source": data_source,
            "profit_model": profit_model,
            "risk_model": risk_model,
            "cluster_model": cluster_model,
            "performance": performance,
        }
        MLService.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(bundle, MLService.MODEL_FILE)
        return bundle

    @staticmethod
    def _load_or_train(user_id: int, db: Session) -> dict:
        joblib = MLService._joblib()
        if MLService.MODEL_FILE.exists():
            try:
                return joblib.load(MLService.MODEL_FILE)
            except Exception:
                pass
        return MLService._train_bundle(user_id, db)

    @staticmethod
    def _load_demo_rows() -> list[dict]:
        pd = MLService._pd()
        root = Path(__file__).resolve().parents[3]
        trades = pd.read_csv(root / "datasets" / "trades.csv")
        features = pd.read_csv(root / "datasets" / "engineered_features.csv")
        merged = features.merge(trades, on="trade_id", how="left")
        renamed = merged.rename(columns={"rr_ratio_y": "rr_ratio"})
        if "rr_ratio_x" in renamed:
            renamed["average_rr_last_10"] = renamed["rr_ratio_x"].fillna(renamed["average_rr_last_10"])
        renamed["stop_loss_distance"] = (renamed["entry_price"] - renamed["stop_loss"]).abs() / renamed["entry_price"]
        renamed["take_profit_distance"] = (renamed["take_profit"] - renamed["entry_price"]).abs() / renamed["entry_price"]
        renamed["hour_of_day"] = pd.to_datetime(renamed["timestamp"]).dt.hour
        renamed["day_of_week"] = pd.to_datetime(renamed["timestamp"]).dt.dayofweek
        renamed["revenge_trade_flag"] = renamed["revenge_trade_flag"].astype(bool)
        renamed["overtrading_flag"] = renamed["overtrading_flag"].astype(bool)
        for column in FEATURE_COLUMNS + ["profitable_trade", "high_risk_trader"]:
            if column not in renamed:
                renamed[column] = 0 if column in NUMERIC_FEATURES + ["profitable_trade", "high_risk_trader"] else "unknown"
        return renamed[FEATURE_COLUMNS + ["profitable_trade", "high_risk_trader", "revenge_trade_flag", "overtrading_flag"]].to_dict("records")

    @staticmethod
    def _resolve_trade(user_id: int, request: PredictionRequest, db: Session) -> Trade | dict:
        if request.trade_id:
            trade = db.query(Trade).filter(Trade.id == request.trade_id, Trade.user_id == user_id).first()
            if not trade:
                raise ValueError("Trade not found")
            return trade
        if request.trade:
            return request.trade.model_dump()
        trade = (
            db.query(Trade)
            .filter(Trade.user_id == user_id)
            .order_by(Trade.entry_timestamp.desc())
            .first()
        )
        if trade:
            return trade
        demo = MLService._load_demo_rows()[0]
        demo["entry_timestamp"] = datetime.now(timezone.utc)
        return demo

    @staticmethod
    def _current_consecutive_losses(user_id: int, db: Session) -> int:
        trades = (
            db.query(Trade)
            .filter(Trade.user_id == user_id, Trade.pnl.isnot(None))
            .order_by(Trade.entry_timestamp.desc())
            .limit(20)
            .all()
        )
        count = 0
        for trade in trades:
            if trade.pnl is not None and trade.pnl < 0:
                count += 1
            else:
                break
        return count

    @staticmethod
    def _persist_prediction(
        user_id: int,
        trade_id: int,
        profitability: float,
        risk_score: float,
        cluster: int,
        row: dict,
        db: Session,
    ) -> None:
        for prediction_type, value, confidence in [
            ("profitability", profitability, max(profitability, 1 - profitability)),
            ("risk", risk_score, max(risk_score, 1 - risk_score)),
            ("cluster", float(cluster), 1.0),
        ]:
            db.add(
                MLPrediction(
                    user_id=user_id,
                    trade_id=trade_id,
                    model_name=MLService.MODEL_VERSION,
                    prediction_type=prediction_type,
                    prediction_value=float(value),
                    confidence_score=round(float(confidence), 3),
                    features_used={key: row.get(key) for key in FEATURE_COLUMNS},
                )
            )
        db.commit()

    @staticmethod
    def _recommendations(row: dict, profitability: float, risk_score: float, cluster: int) -> list[str]:
        messages = []
        if risk_score >= 0.65:
            messages.append("High behavioral risk detected. Reduce size or wait for a rule-confirmed setup.")
        if profitability < 0.45:
            messages.append("Profitability probability is below your baseline. Recheck strategy, session, and RR quality.")
        if row.get("consecutive_losses", 0) >= 2:
            messages.append("Recent losing streak detected. Take a cooldown before the next entry.")
        if row.get("revenge_trade_frequency", 0) > 0.2 or row.get("emotional_state") == "REVENGE":
            messages.append("Revenge-trading pattern is elevated. Avoid immediate re-entry after losses.")
        if row.get("overtrading_score", 0) > 0.25:
            messages.append("Overtrading score is high. Limit trades to your best setups.")
        if not messages:
            messages.append(f"Pattern cluster {cluster} looks acceptable. Keep execution aligned with your trading plan.")
        return messages

    @staticmethod
    def _single_class(rows: list[dict], target: str) -> bool:
        values = {row.get(target) for row in rows if row.get(target) is not None}
        return len(values) < 2

    @staticmethod
    def _metric_dict(y_true, y_pred) -> dict:
        metrics = MLService._sklearn()
        return {
            "accuracy": round(float(metrics["accuracy_score"](y_true, y_pred)), 3),
            "precision": round(float(metrics["precision_score"](y_true, y_pred, zero_division=0)), 3),
            "recall": round(float(metrics["recall_score"](y_true, y_pred, zero_division=0)), 3),
            "f1_score": round(float(metrics["f1_score"](y_true, y_pred, zero_division=0)), 3),
        }

    @staticmethod
    def _performance_from_bundle(bundle: dict) -> ModelPerformanceResponse:
        performance = bundle["performance"]
        return ModelPerformanceResponse(
            model_version=bundle["model_version"],
            trained_at=bundle["trained_at"],
            training_rows=bundle["training_rows"],
            data_source=bundle["data_source"],
            profitability_model=ModelMetric(**performance["profitability_model"]),
            risk_model=ModelMetric(**performance["risk_model"]),
            cluster_distribution=performance["cluster_distribution"],
        )

    @staticmethod
    def _pd():
        import pandas as pd

        return pd

    @staticmethod
    def _np():
        import numpy as np

        return np

    @staticmethod
    def _joblib():
        import joblib

        return joblib

    @staticmethod
    def _sklearn() -> dict:
        from sklearn.cluster import KMeans
        from sklearn.compose import ColumnTransformer
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        return {
            "KMeans": KMeans,
            "ColumnTransformer": ColumnTransformer,
            "RandomForestClassifier": RandomForestClassifier,
            "LogisticRegression": LogisticRegression,
            "accuracy_score": accuracy_score,
            "f1_score": f1_score,
            "precision_score": precision_score,
            "recall_score": recall_score,
            "train_test_split": train_test_split,
            "Pipeline": Pipeline,
            "OneHotEncoder": OneHotEncoder,
            "StandardScaler": StandardScaler,
        }
