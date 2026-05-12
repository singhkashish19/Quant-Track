"""Journal and NLP API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.database.models import Journal, NLPAnalysis, User
from app.nlp.schemas import (
    JournalCreate,
    JournalResponse,
    JournalSummaryResponse,
    JournalWithAnalysisResponse,
    NLPAnalysisResponse,
)
from app.nlp.service import NLPService

router = APIRouter(prefix="/api/journals", tags=["Journals & NLP"])


@router.post("", response_model=JournalWithAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def create_journal(
    journal_data: JournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> JournalWithAnalysisResponse:
    """Create a journal entry and run behavioral NLP analysis immediately."""
    try:
        journal, analysis = NLPService.create_journal(current_user.id, journal_data, db)
        return JournalWithAnalysisResponse(
            journal=JournalResponse.from_attributes(journal),
            analysis=NLPAnalysisResponse.from_attributes(analysis),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("", response_model=list[JournalResponse])
async def list_journals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[JournalResponse]:
    """List the current user's journal entries."""
    journals = (
        db.query(Journal)
        .filter(Journal.user_id == current_user.id)
        .order_by(Journal.created_at.desc())
        .all()
    )
    return [JournalResponse.from_attributes(journal) for journal in journals]


@router.get("/summary", response_model=JournalSummaryResponse)
async def journal_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> JournalSummaryResponse:
    """Summarize behavioral journal signals for the current user."""
    analyses = (
        db.query(NLPAnalysis)
        .filter(NLPAnalysis.user_id == current_user.id)
        .order_by(NLPAnalysis.created_at.desc())
        .all()
    )
    if not analyses:
        return JournalSummaryResponse(
            total_journals=0,
            average_sentiment=0.0,
            fomo_events=0,
            revenge_events=0,
            impulsive_events=0,
            dominant_behavior=None,
            risk_warnings=[],
        )

    fomo_events = sum(1 for item in analyses if item.fomo_score >= 0.34)
    revenge_events = sum(1 for item in analyses if item.revenge_trade_score >= 0.34)
    impulsive_events = sum(1 for item in analyses if item.impulsive_score >= 0.34)
    behavior_counts = {
        "FOMO": fomo_events,
        "revenge_trading": revenge_events,
        "impulsive_trading": impulsive_events,
    }
    dominant_behavior = max(behavior_counts, key=behavior_counts.get)
    warnings = []
    if fomo_events >= 3:
        warnings.append("Repeated FOMO entries detected. Add a confirmation checklist before entries.")
    if revenge_events >= 2:
        warnings.append("Revenge-trading notes are recurring. Use a cooldown rule after losses.")
    if impulsive_events >= 3:
        warnings.append("Impulsive execution is recurring. Reduce trade frequency until rule adherence improves.")

    return JournalSummaryResponse(
        total_journals=len(analyses),
        average_sentiment=round(sum(item.sentiment_score for item in analyses) / len(analyses), 3),
        fomo_events=fomo_events,
        revenge_events=revenge_events,
        impulsive_events=impulsive_events,
        dominant_behavior=dominant_behavior if behavior_counts[dominant_behavior] else None,
        risk_warnings=warnings,
    )


@router.post("/analyze", response_model=NLPAnalysisResponse)
async def analyze_text(journal_data: JournalCreate) -> NLPAnalysisResponse:
    """Analyze journal text without saving it."""
    payload = NLPService.analyze_text(journal_data.notes)
    return NLPAnalysisResponse(journal_id=0, **payload)


@router.get("/{journal_id}/analysis", response_model=NLPAnalysisResponse)
async def get_journal_analysis(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> NLPAnalysisResponse:
    """Return stored NLP analysis for a journal entry."""
    analysis = (
        db.query(NLPAnalysis)
        .filter(NLPAnalysis.journal_id == journal_id, NLPAnalysis.user_id == current_user.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal analysis not found")
    return NLPAnalysisResponse.from_attributes(analysis)
