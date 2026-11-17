"""
Stage 4: Evaluate original vs optimized prompts.

Deterministic checks where possible, plus ONE LLM-judge call per prompt
for the subjective bits.
"""

import json
from groq import Groq

from configs.settings import settings
from backend.models.schemas import EvaluationScore

client = Groq(api_key=settings.groq_api_key)

JUDGE_SYSTEM_PROMPT = """You are an evaluator scoring how effective a \
prompt is likely to be for its intended task. Score on a 0-10 scale for \
each dimension. Respond with ONLY a JSON object, no other text:
{
  "relevance": float,          // does it clearly target the task?
  "clarity": float,            // is it unambiguous and well-specified?
  "format_adherence": float,   // does it specify a clear expected output?
  "notes": string or null
}"""


def _run_deterministic_checks(prompt: str) -> dict:
    """Cheap, no-LLM checks that catch obvious issues before/instead of judging."""
    has_output_format = any(kw in prompt.lower() for kw in ["json", "format:", "return", "schema", "structure"])
    length_ok = 10 <= len(prompt) <= 4000
    return {"has_output_format": has_output_format, "length_ok": length_ok}


def score_prompt(prompt: str) -> EvaluationScore:
    checks = _run_deterministic_checks(prompt)

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": f'Prompt to evaluate:\n"""{prompt}"""'},
        ],
    )

    text = response.choices[0].message.content.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data = json.loads(text)

    format_score = data["format_adherence"]
    if checks["has_output_format"] and format_score < 5:
        format_score = 5.0

    overall = round((data["relevance"] + data["clarity"] + format_score) / 3, 2)

    return EvaluationScore(
        relevance=data["relevance"],
        clarity=data["clarity"],
        format_adherence=format_score,
        overall=overall,
        notes=data.get("notes"),
    )


def compare(original_prompt: str, optimized_prompt: str) -> tuple[EvaluationScore, EvaluationScore, float]:
    original_score = score_prompt(original_prompt)
    optimized_score = score_prompt(optimized_prompt)
    improvement = round(optimized_score.overall - original_score.overall, 2)
    return original_score, optimized_score, improvement