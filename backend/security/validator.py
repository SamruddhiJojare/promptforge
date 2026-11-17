"""
Lightweight input validation. Intentionally NOT a full injection-detection
system for v1 — just enough to reject obviously bad input and flag the
most common override attempts. Expand later if you want a real security
module.
"""

import re

MAX_PROMPT_LENGTH = 4000

_INJECTION_PATTERNS = [
    r"ignore (all |the )?(previous|above) instructions",
    r"disregard (all |the )?(previous|above) instructions",
    r"reveal (the )?system prompt",
    r"you are now",
]


class ValidationResult:
    def __init__(self, is_valid: bool, reason: str | None = None, flagged: bool = False):
        self.is_valid = is_valid
        self.reason = reason
        self.flagged = flagged


def validate_prompt(prompt: str) -> ValidationResult:
    if not prompt or not prompt.strip():
        return ValidationResult(False, "Prompt is empty.")

    if len(prompt) > MAX_PROMPT_LENGTH:
        return ValidationResult(False, f"Prompt exceeds {MAX_PROMPT_LENGTH} characters.")

    lowered = prompt.lower()
    for pattern in _INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            # Don't hard-block — flag it. A false positive shouldn't break the demo.
            return ValidationResult(True, "Possible instruction override detected.", flagged=True)

    return ValidationResult(True)