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
from typing import Any, Callable, Dict, List, Optional, Union

from tasks import TASK_INDEX, TaskSpec, Email

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
    emails: List[Email] = field(default_factory=list)
    action_history: List[int] = field(default_factory=list)
    steps_taken: int = 1
    max_steps: int = 20


def _coerce(g: Optional[Union[GraderInput, Dict[str, Any]]], task_id: str) -> GraderInput:
    """Coerce dict or None into GraderInput."""
    if g is None:
        spec = TASK_INDEX[task_id]
        return GraderInput(
            task_id=task_id,
            emails=list(spec.emails),
            action_history=[],
            steps_taken=1,
            max_steps=spec.max_steps,
        )
    if isinstance(g, dict):
        return GraderInput(
            task_id=g.get("task_id", task_id),
            emails=g.get("emails", []),  # we assume it's correctly formatted when from dict for now
            action_history=list(g.get("action_history", [])),
            steps_taken=int(g.get("steps_taken", 1)),
            max_steps=int(g.get("max_steps", 20)),
        )
    return g


def _base_score(g: GraderInput) -> float:
    """Calculate the accuracy based on expected actions."""
    if not g.emails:
        return 0.0
        
    correct = 0
    for i, email in enumerate(g.emails):
        if i < len(g.action_history):
            if g.action_history[i] == email.expected_action:
                correct += 1
                
    # Penalty for not completing all
    completion_ratio = len(g.action_history) / len(g.emails)
    accuracy = (correct / len(g.emails)) if g.emails else 0.0
    
    return 0.8 * accuracy + 0.2 * completion_ratio


def grade_email_easy_001(g=None) -> float:
    inp = _coerce(g, "email-easy-001")
    raw = _base_score(inp)
    return _to_open_interval(raw)


def grade_email_medium_001(g=None) -> float:
    inp = _coerce(g, "email-medium-001")
    # Medium might have stricter requirements for efficiency
    raw = _base_score(inp)
    efficiency = 1.0 - min(1.0, (inp.steps_taken - len(inp.action_history)) / max(inp.max_steps, 1))
    return _to_open_interval(0.8 * raw + 0.2 * efficiency)


def grade_email_hard_001(g=None) -> float:
    inp = _coerce(g, "email-hard-001")
    raw = _base_score(inp)
    # Hard requires almost perfect steps to completion
    efficiency = 1.0 - min(1.0, (inp.steps_taken - len(inp.action_history)) / max(inp.max_steps, 1))
    return _to_open_interval(0.7 * raw + 0.3 * efficiency)


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
