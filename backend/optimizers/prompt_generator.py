"""
Stage 3: Generate the optimized prompt.

Single LLM call, given the original prompt + analysis + which strategies
to apply.
"""

from groq import Groq

from configs.settings import settings
from backend.models.schemas import PromptAnalysis, OptimizationStrategies, OptimizedPrompt

client = Groq(api_key=settings.groq_api_key)


def _build_instructions(strategies: OptimizationStrategies) -> str:
    parts = []
    if strategies.use_role_prompting:
        parts.append("- Assign the model an appropriate expert role.")
    if strategies.use_few_shot:
        parts.append("- Include 1-2 short illustrative examples.")
    if strategies.use_structured_output:
        parts.append("- Specify an explicit output format/schema.")
    if strategies.use_constraints:
        parts.append("- Add relevant constraints (length, scope, what to avoid).")
    if strategies.use_chain_of_thought:
        parts.append("- Ask the model to reason step by step before answering.")
    return "\n".join(parts) if parts else "- Improve clarity and specificity generally."


REWRITE_SYSTEM_PROMPT = """You are a prompt engineering assistant. Rewrite \
the user's original prompt into a clearer, more effective version by \
applying ONLY the techniques listed below. Do not change the underlying \
task or intent. Return ONLY the rewritten prompt text, no preamble, no \
explanation, no markdown fences."""


def generate_optimized_prompt(
    original_prompt: str,
    analysis: PromptAnalysis,
    strategies: OptimizationStrategies,
) -> OptimizedPrompt:
    instructions = _build_instructions(strategies)

    user_message = f"""Original prompt:
\"\"\"{original_prompt}\"\"\"

Detected task type: {analysis.task_type}
Missing elements: {", ".join(analysis.missing_elements) or "none noted"}

Apply these techniques:
{instructions}"""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    optimized_text = response.choices[0].message.content.strip()

    return OptimizedPrompt(
        original_prompt=original_prompt,
        optimized_prompt=optimized_text,
        strategies_applied=strategies,
        analysis=analysis,
    )