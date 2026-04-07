"""
Deterministic task graders for Round 1 Phase 2.

Hackathon requirement: each task score must lie strictly in (0, 1) — not 0.0 nor 1.0.
We map any raw score in [0, 1] into (epsilon, 1 - epsilon).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from tasks import TASK_INDEX, TaskSpec

# Strict open interval (0, 1) per validator wording.
_EPS = 0.02
_MIN = _EPS
_MAX = 1.0 - _EPS


def _to_open_interval(raw: float) -> float:
    """Map [0, 1] style raw score into (_MIN, _MAX)."""
    x = float(raw)
    if x <= 0.0:
        return _MIN
    if x >= 1.0:
        return _MAX
    # Keep interior values away from boundaries if they land very close.
    return max(_MIN, min(_MAX, x))


@dataclass
class GraderInput:
    """Snapshot needed for grading (mirrors environment state fields)."""

    task_id: str
    unread_emails_count: int
    urgent_emails_count: int
    spam_count: int
    response_queue: list[str]
    steps_taken: int
    max_steps: int


def _base_progress(spec: TaskSpec, g: GraderInput) -> float:
    """Fraction of inbox work cleared vs initial load."""
    initial_total = spec.unread_emails_count + spec.urgent_emails_count + spec.spam_count
    remaining = g.unread_emails_count + g.urgent_emails_count + g.spam_count
    cleared = max(0, initial_total - remaining)
    return cleared / max(initial_total, 1)


def grade_email_easy_001(g: GraderInput) -> float:
    """Easy: prioritize clearing urgent items via replies."""
    spec = TASK_INDEX["email-easy-001"]
    urgent_ratio = 1.0 - (g.urgent_emails_count / max(spec.urgent_emails_count, 1))
    progress = _base_progress(spec, g)
    urgent_replies = sum(1 for x in g.response_queue if x == "urgent_email_replied")
    reply_quality = min(1.0, urgent_replies / max(spec.urgent_emails_count, 1))
    raw = 0.5 * urgent_ratio + 0.3 * progress + 0.2 * reply_quality
    return _to_open_interval(raw)


def grade_email_medium_001(g: GraderInput) -> float:
    """Medium: balance spam removal and inbox progress."""
    spec = TASK_INDEX["email-medium-001"]
    spam_ratio = 1.0 - (g.spam_count / max(spec.spam_count, 1))
    progress = _base_progress(spec, g)
    raw = 0.45 * spam_ratio + 0.55 * progress
    return _to_open_interval(raw)


def grade_email_hard_001(g: GraderInput) -> float:
    """Hard: require both low urgent backlog and overall progress."""
    spec = TASK_INDEX["email-hard-001"]
    urgent_penalty = g.urgent_emails_count / max(spec.urgent_emails_count, 1)
    progress = _base_progress(spec, g)
    efficiency = 1.0 - min(1.0, g.steps_taken / max(spec.max_steps, 1))
    raw = 0.35 * (1.0 - urgent_penalty) + 0.45 * progress + 0.2 * efficiency
    return _to_open_interval(raw)


# Registry used by validators / introspection.
GRADERS: Dict[str, Callable[[GraderInput], float]] = {
    "email-easy-001": grade_email_easy_001,
    "email-medium-001": grade_email_medium_001,
    "email-hard-001": grade_email_hard_001,
}


def grade_task(task_id: str, g: GraderInput) -> float:
    if task_id not in GRADERS:
        return _to_open_interval(0.0)
    return GRADERS[task_id](g)
