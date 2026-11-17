from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.models.schemas import OptimizeRequest, ComparisonResult
from backend.security.validator import validate_prompt
from backend.analyzers.prompt_analyzer import analyze_prompt
from backend.optimizers.strategy_selector import select_strategies
from backend.optimizers.prompt_generator import generate_optimized_prompt
from backend.evaluators.scorer import compare
from backend.database.session import get_db
from backend.database.models import OptimizationRun

router = APIRouter()


@router.post("/optimize", response_model=ComparisonResult)
def optimize(request: OptimizeRequest, db: Session = Depends(get_db)):
    validation = validate_prompt(request.prompt)
    if not validation.is_valid:
        raise HTTPException(status_code=400, detail=validation.reason)

    analysis = analyze_prompt(request.prompt)
    strategies = select_strategies(analysis)
    result = generate_optimized_prompt(request.prompt, analysis, strategies)

    original_score, optimized_score, improvement = compare(
        result.original_prompt, result.optimized_prompt
    )

    db.add(OptimizationRun(
        original_prompt=result.original_prompt,
        optimized_prompt=result.optimized_prompt,
        task_type=analysis.task_type,
        original_score=original_score.overall,
        optimized_score=optimized_score.overall,
        improvement=improvement,
        iterations=1,
    ))
    db.commit()

    return ComparisonResult(
        original_prompt=result.original_prompt,
        optimized_prompt=result.optimized_prompt,
        original_score=original_score,
        optimized_score=optimized_score,
        improvement=improvement,
        iterations=1,
    )


@router.get("/history")
def history(db: Session = Depends(get_db), limit: int = 20):
    runs = (
        db.query(OptimizationRun)
        .order_by(OptimizationRun.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "task_type": r.task_type,
            "original_score": r.original_score,
            "optimized_score": r.optimized_score,
            "improvement": r.improvement,
        }
        for r in runs
    ]