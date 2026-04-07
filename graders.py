"""
Deterministic task graders for Round 1 Phase 2.

Hackathon requirement: each task score must lie strictly in (0, 1) — not 0.0 nor 1.0.

Each grader accepts:
  - a GraderInput dataclass
  - a plain dict with the same fields
  - no arguments (returns a mid-range default score)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Union

from tasks import TASK_INDEX, TaskSpec

# Strict open interval boundaries.
_EPS = 0.05
_MIN = _EPS
_MAX = 1.0 - _EPS
_DEFAULT = 0.5  # returned when called with no args


def _to_open_interval(raw: float) -> float:
    """Map any float into the open interval (_MIN, _MAX)."""
    x = float(raw)
    if x <= 0.0:
        return _MIN
    if x >= 1.0:
        return _MAX
    return max(_MIN, min(_MAX, x))


@dataclass
class GraderInput:
    """Snapshot needed for grading (mirrors environment state fields)."""
    task_id: str = "email-easy-001"
    unread_emails_count: int = 0
    urgent_emails_count: int = 0
    spam_count: int = 0
    response_queue: list = field(default_factory=list)
    steps_taken: int = 1
    max_steps: int = 20


def _coerce(g: Optional[Union[GraderInput, Dict[str, Any]]], task_id: str) -> GraderInput:
    """Coerce dict or None into GraderInput."""
    if g is None:
        spec = TASK_INDEX[task_id]
        return GraderInput(
            task_id=task_id,
            unread_emails_count=spec.unread_emails_count // 2,
            urgent_emails_count=spec.urgent_emails_count // 2,
            spam_count=spec.spam_count // 2,
            response_queue=[],
            steps_taken=spec.max_steps // 2,
            max_steps=spec.max_steps,
        )
    if isinstance(g, dict):
        return GraderInput(
            task_id=g.get("task_id", task_id),
            unread_emails_count=int(g.get("unread_emails_count", 0)),
            urgent_emails_count=int(g.get("urgent_emails_count", 0)),
            spam_count=int(g.get("spam_count", 0)),
            response_queue=list(g.get("response_queue", [])),
            steps_taken=int(g.get("steps_taken", 1)),
            max_steps=int(g.get("max_steps", 20)),
        )
    return g


def _base_progress(spec: TaskSpec, g: GraderInput) -> float:
    """Fraction of inbox work cleared vs initial load."""
    initial_total = spec.unread_emails_count + spec.urgent_emails_count + spec.spam_count
    remaining = g.unread_emails_count + g.urgent_emails_count + g.spam_count
    cleared = max(0, initial_total - remaining)
    return cleared / max(initial_total, 1)


def grade_email_easy_001(g=None) -> float:
    """Easy: prioritize clearing urgent items via replies. Score in (0, 1)."""
    inp = _coerce(g, "email-easy-001")
    spec = TASK_INDEX["email-easy-001"]
    urgent_ratio = 1.0 - (inp.urgent_emails_count / max(spec.urgent_emails_count, 1))
    progress = _base_progress(spec, inp)
    urgent_replies = sum(1 for x in inp.response_queue if x == "urgent_email_replied")
    reply_quality = min(1.0, urgent_replies / max(spec.urgent_emails_count, 1))
    raw = 0.5 * urgent_ratio + 0.3 * progress + 0.2 * reply_quality
    return _to_open_interval(raw)


def grade_email_medium_001(g=None) -> float:
    """Medium: balance spam removal and inbox progress. Score in (0, 1)."""
    inp = _coerce(g, "email-medium-001")
    spec = TASK_INDEX["email-medium-001"]
    spam_ratio = 1.0 - (inp.spam_count / max(spec.spam_count, 1))
    progress = _base_progress(spec, inp)
    raw = 0.45 * spam_ratio + 0.55 * progress
    return _to_open_interval(raw)


def grade_email_hard_001(g=None) -> float:
    """Hard: require both low urgent backlog and overall progress. Score in (0, 1)."""
    inp = _coerce(g, "email-hard-001")
    spec = TASK_INDEX["email-hard-001"]
    urgent_penalty = inp.urgent_emails_count / max(spec.urgent_emails_count, 1)
    progress = _base_progress(spec, inp)
    efficiency = 1.0 - min(1.0, inp.steps_taken / max(spec.max_steps, 1))
    raw = 0.35 * (1.0 - urgent_penalty) + 0.45 * progress + 0.2 * efficiency
    return _to_open_interval(raw)


# Registry used by validators / introspection.
GRADERS: Dict[str, Callable] = {
    "email-easy-001": grade_email_easy_001,
    "email-medium-001": grade_email_medium_001,
    "email-hard-001": grade_email_hard_001,
}


def grade_task(task_id: str, g=None) -> float:
    if task_id not in GRADERS:
        return _to_open_interval(0.0)
    return GRADERS[task_id](g)
