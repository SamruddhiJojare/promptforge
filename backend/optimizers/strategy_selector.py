"""
Stage 2: Decide which optimization strategies to apply.

Deliberately rule-based (a dict lookup), not ML-based. Task-to-strategy
mapping is well understood and doesn't need to be learned.
"""

from backend.models.schemas import PromptAnalysis, OptimizationStrategies

_STRATEGY_TABLE: dict[str, OptimizationStrategies] = {
    "qa": OptimizationStrategies(use_role_prompting=True),
    "classification": OptimizationStrategies(use_role_prompting=True, use_few_shot=True, use_structured_output=True),
    "extraction": OptimizationStrategies(use_structured_output=True, use_constraints=True),
    "summarization": OptimizationStrategies(use_role_prompting=True, use_constraints=True),
    "coding": OptimizationStrategies(use_constraints=True, use_structured_output=True),
    "reasoning": OptimizationStrategies(use_chain_of_thought=True, use_role_prompting=True),
    "data_analysis": OptimizationStrategies(use_role_prompting=True, use_structured_output=True, use_constraints=True),
    "creative_writing": OptimizationStrategies(use_role_prompting=True, use_constraints=True),
}

_DEFAULT_STRATEGY = OptimizationStrategies(use_role_prompting=True, use_constraints=True)


def select_strategies(analysis: PromptAnalysis) -> OptimizationStrategies:
    strategy = _STRATEGY_TABLE.get(analysis.task_type.lower(), _DEFAULT_STRATEGY)

    if analysis.ambiguity_score > 0.6:
        strategy = strategy.model_copy(update={"use_structured_output": True})

    return strategy