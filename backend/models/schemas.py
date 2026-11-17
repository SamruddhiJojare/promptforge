"""
Shared Pydantic models. Keep these as the single source of truth for the
shape of data moving between analyzer -> optimizer -> evaluator -> API.
"""

from pydantic import BaseModel, Field
from typing import Optional


class PromptAnalysis(BaseModel):
    """Output of the analyzer stage."""
    task_type: str = Field(..., description="e.g. classification, summarization, qa, coding")
    domain: Optional[str] = None
    target_audience: Optional[str] = None
    ambiguity_score: float = Field(..., ge=0, le=1)
    missing_elements: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class OptimizationStrategies(BaseModel):
    """Output of the strategy selector — which techniques to apply."""
    use_role_prompting: bool = False
    use_few_shot: bool = False
    use_structured_output: bool = False
    use_constraints: bool = False
    use_chain_of_thought: bool = False


class OptimizedPrompt(BaseModel):
    """Output of the prompt generator."""
    original_prompt: str
    optimized_prompt: str
    strategies_applied: OptimizationStrategies
    analysis: PromptAnalysis


class EvaluationScore(BaseModel):
    """Score for a single prompt (original or optimized)."""
    relevance: float = Field(..., ge=0, le=10)
    clarity: float = Field(..., ge=0, le=10)
    format_adherence: float = Field(..., ge=0, le=10)
    overall: float = Field(..., ge=0, le=10)
    notes: Optional[str] = None


class ComparisonResult(BaseModel):
    """Final side-by-side result shown in the UI."""
    original_prompt: str
    optimized_prompt: str
    original_score: EvaluationScore
    optimized_score: EvaluationScore
    improvement: float
    iterations: int = 1


class OptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    max_iterations: int = Field(default=1, ge=1, le=3)