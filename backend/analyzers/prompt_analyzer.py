"""
Stage 1: Analyze the raw user prompt.

Uses a single LLM call constrained to return JSON matching PromptAnalysis.
"""

import json
from groq import Groq

from configs.settings import settings
from backend.models.schemas import PromptAnalysis

client = Groq(api_key=settings.groq_api_key)

ANALYZER_SYSTEM_PROMPT = """You are a prompt analysis engine. Given a user's \
prompt, identify its task type, domain, target audience, how ambiguous it \
is, and what's missing that would make it more effective.

Respond with ONLY a JSON object, no other text, matching this schema:
{
  "task_type": string,           // e.g. "classification", "summarization", "qa", "coding", "data_analysis", "creative_writing"
  "domain": string or null,
  "target_audience": string or null,
  "ambiguity_score": float,      // 0.0 (very clear) to 1.0 (very ambiguous)
  "missing_elements": [string],  // e.g. ["output_format", "target_audience", "constraints"]
  "notes": string or null
}"""


def analyze_prompt(prompt: str) -> PromptAnalysis:
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    text = response.choices[0].message.content
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    data = json.loads(text)
    return PromptAnalysis(**data)