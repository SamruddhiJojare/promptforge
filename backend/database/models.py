"""
Minimal storage schema for v1: one row per optimization run.
Expand into separate prompts / versions / runs tables later if needed —
this is enough to show history in the demo UI.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime, timezone

from backend.database.session import Base


class OptimizationRun(Base):
    __tablename__ = "optimization_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    original_prompt = Column(Text, nullable=False)
    optimized_prompt = Column(Text, nullable=False)
    task_type = Column(String, nullable=True)

    original_score = Column(Float, nullable=True)
    optimized_score = Column(Float, nullable=True)
    improvement = Column(Float, nullable=True)
    iterations = Column(Integer, default=1)