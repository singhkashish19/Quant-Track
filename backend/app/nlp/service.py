"""Rule-based NLP starter pipeline for behavioral trading journals."""

import re
from collections import Counter
from typing import Dict, List, Tuple

from sqlalchemy.orm import Session
try:
    from textblob import TextBlob
except ModuleNotFoundError:  # Allows the API to boot before optional NLP deps are installed.
    TextBlob = None

from app.database.models import Journal, NLPAnalysis, Trade
from app.nlp.schemas import JournalCreate


class NLPService:
    """Creates journals and stores behavioral NLP analysis."""

    STOPWORDS = {
        "a",
        "an",
        "and",
        "because",
        "but",
        "for",
        "i",
        "in",
        "it",
        "my",
        "of",
        "on",
        "the",
        "to",
        "was",
    }

    BEHAVIOR_RULES = {
        "fomo": ("missed", "chased", "aggressive", "moved fast", "without confirmation", "late entry"),
        "revenge_trading": ("revenge", "after loss", "re-entered", "win it back", "immediately after"),
        "impulsive": ("too early", "impulsive", "no plan", "ignored", "broke rules", "forced"),
        "fear": ("fear", "scared", "hesitated", "panic", "closed early"),
        "greed": ("greed", "overconfident", "held too long", "wanted more", "doubled"),
        "discipline": ("followed", "rules", "setup", "waited", "planned", "confirmed"),
    }

    @staticmethod
    def create_journal(user_id: int, data: JournalCreate, db: Session) -> Tuple[Journal, NLPAnalysis]:
        if data.trade_id:
            trade = db.query(Trade).filter(Trade.id == data.trade_id, Trade.user_id == user_id).first()
            if not trade:
                raise ValueError("Trade not found")

        journal = Journal(
            user_id=user_id,
            trade_id=data.trade_id,
            notes=data.notes,
            emotional_state=data.emotional_state,
        )
        db.add(journal)
        db.flush()

        payload = NLPService.analyze_text(data.notes)
        analysis = NLPAnalysis(
            user_id=user_id,
            journal_id=journal.id,
            sentiment_score=payload["sentiment_score"],
            detected_emotions=payload["detected_emotions"],
            fomo_score=payload["fomo_score"],
            revenge_trade_score=payload["revenge_trade_score"],
            impulsive_score=payload["impulsive_score"],
            fear_greed_pattern=payload["fear_greed_pattern"],
            extracted_keywords=payload["extracted_keywords"],
            behavior_tags=payload["behavior_tags"],
        )
        db.add(analysis)
        db.commit()
        db.refresh(journal)
        db.refresh(analysis)
        return journal, analysis

    @staticmethod
    def analyze_text(text: str) -> dict:
        normalized = text.lower()
        scores = {
            label: NLPService._score_keywords(normalized, keywords)
            for label, keywords in NLPService.BEHAVIOR_RULES.items()
        }
        sentiment_score = NLPService._sentiment_score(text)
        behavior_tags = [label for label, score in scores.items() if score >= 0.34]
        if not behavior_tags and sentiment_score > 0.2:
            behavior_tags.append("positive_execution")
        if not behavior_tags and sentiment_score < -0.2:
            behavior_tags.append("negative_emotional_state")

        fear_greed_pattern = None
        if scores["fear"] > scores["greed"] and scores["fear"] > 0:
            fear_greed_pattern = "fear"
        elif scores["greed"] > 0:
            fear_greed_pattern = "greed"
        elif scores["discipline"] > 0:
            fear_greed_pattern = "disciplined"

        return {
            "sentiment_score": sentiment_score,
            "detected_emotions": scores,
            "fomo_score": scores["fomo"],
            "revenge_trade_score": scores["revenge_trading"],
            "impulsive_score": scores["impulsive"],
            "fear_greed_pattern": fear_greed_pattern,
            "extracted_keywords": NLPService._keywords(normalized),
            "behavior_tags": behavior_tags,
        }

    @staticmethod
    def _score_keywords(text: str, keywords: Tuple[str, ...]) -> float:
        matches = sum(1 for keyword in keywords if keyword in text)
        return round(min(matches / 3, 1.0), 2)

    @staticmethod
    def _keywords(text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z]{3,}", text)
        filtered = [token for token in tokens if token not in NLPService.STOPWORDS]
        return [word for word, _ in Counter(filtered).most_common(8)]

    @staticmethod
    def _sentiment_score(text: str) -> float:
        if TextBlob is not None:
            return round(TextBlob(text).sentiment.polarity, 3)

        positive = {"perfectly", "followed", "confidence", "planned", "confirmed", "good"}
        negative = {"loss", "ignored", "forced", "scared", "panic", "revenge", "early"}
        tokens = set(re.findall(r"[a-zA-Z]{3,}", text.lower()))
        raw_score = len(tokens & positive) - len(tokens & negative)
        return round(max(min(raw_score / 4, 1.0), -1.0), 3)
