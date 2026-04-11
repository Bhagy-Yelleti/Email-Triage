from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from tasks import TASK_INDEX, TaskSpec, Email

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
    task_id: str = "email-easy-001"
    emails: List[Email] = field(default_factory=list)
    action_history: List[int] = field(default_factory=list)
    steps_taken: int = 1
    max_steps: int = 20
    classified_labels: Dict[str, Dict[str, str]] = field(default_factory=dict)
    priority_order: List[int] = field(default_factory=list)
    replies: Dict[str, str] = field(default_factory=dict)
    thread_statuses: Dict[str, str] = field(default_factory=dict)
    resolved_count: int = 0

def _coerce(g: Optional[Union[GraderInput, Dict[str, Any]]], task_id: str) -> GraderInput:
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
            emails=g.get("emails", []),
            action_history=list(g.get("action_history", [])),
            steps_taken=int(g.get("steps_taken", 1)),
            max_steps=int(g.get("max_steps", 20)),
            classified_labels=g.get("classified_labels", {}),
            priority_order=g.get("priority_order", []),
            replies=g.get("replies", {}),
            thread_statuses=g.get("thread_statuses", {}),
            resolved_count=int(g.get("resolved_count", 0)),
        )
    return g

def grade_email_easy_001(g=None) -> float:
    inp = _coerce(g, "email-easy-001")
    if not inp.emails: return _to_open_interval(0.0)
    
    # Task 1: Single Email Classification
    # Reward: +0.3 category, +0.3 urgency, +0.4 action
    
    score = 0.0
    email = inp.emails[0]
    labels = inp.classified_labels.get(email.id, {})
    
    # 0.3 category
    if labels.get("category", "").lower() == email.category.lower():
        score += 0.3
    
    # 0.3 urgency
    if labels.get("urgency_level", "").lower() == email.urgency_level.lower():
        score += 0.3
        
    # 0.4 action (assumed set in thread_statuses for grading action)
    if inp.thread_statuses.get(email.id, "").lower() == email.expected_action.lower():
        score += 0.4
        
    return _to_open_interval(score)

def grade_email_medium_001(g=None) -> float:
    inp = _coerce(g, "email-medium-001")
    if not inp.emails: return _to_open_interval(0.0)
    
    # Task 2: Multi-Email Queue Prioritization
    # Reward: +0.4 correct ordering, +0.3 classification, +0.3 action recommendation
    
    # Check priority ordering
    # For medium task, correct priority corresponds to urgency.
    expected_priority = sorted(inp.emails, key=lambda x: (x.urgency_level != 'high', x.urgency_level != 'medium', x.urgency_level != 'low'))
    expected_ids = [e.id for e in expected_priority]
    
    score = 0.0
    if inp.priority_order:
        # Check rank correlation or basic exact match on top 2
        # If top 2 are correct high-urgency tasks:
        if len(inp.priority_order) >= 2:
            # Assume agent priority_order maps to indices or ids. Since the schema says List[int], we compare indices.
            idx1, idx2 = inp.priority_order[0], inp.priority_order[1]
            if idx1 < len(inp.emails) and idx2 < len(inp.emails):
                if inp.emails[idx1].urgency_level == 'high' and inp.emails[idx2].urgency_level == 'high':
                    score += 0.4
                elif inp.emails[idx1].urgency_level == 'high' or inp.emails[idx2].urgency_level == 'high':
                    score += 0.2
                    
    cls_score = 0.0
    act_score = 0.0
    for email in inp.emails:
        labels = inp.classified_labels.get(email.id, {})
        if labels.get("category", "").lower() == email.category.lower():
            cls_score += 0.5 / len(inp.emails) # partial
        if labels.get("urgency_level", "").lower() == email.urgency_level.lower():
            cls_score += 0.5 / len(inp.emails)
            
        if inp.thread_statuses.get(email.id, "").lower() == email.expected_action.lower():
            act_score += 1.0 / len(inp.emails)
            
    score += (cls_score * 0.3)
    score += (act_score * 0.3)
    
    return _to_open_interval(score)

def grade_email_hard_001(g=None) -> float:
    inp = _coerce(g, "email-hard-001")
    if not inp.emails: return _to_open_interval(0.0)
    
    # Task 3: Thread-Based Workflow Resolution
    # Reward: +0.2 thread understanding, +0.2 urgency, +0.2 reply quality, +0.2 correct action, +0.2 fast completion
    
    score = 0.0
    
    thr_score = 0.0
    urg_score = 0.0
    rep_score = 0.0
    act_score = 0.0
    
    for email in inp.emails:
        labels = inp.classified_labels.get(email.id, {})
        if labels.get("urgency_level", "").lower() == email.urgency_level.lower():
            urg_score += 1.0 / len(inp.emails)
            
        if email.id in inp.replies and email.suggested_reply:
            if "we" in inp.replies[email.id].lower() or "migrate" in inp.replies[email.id].lower():
                rep_score += 1.0 / len(inp.emails)
                
        if inp.thread_statuses.get(email.id, "").lower() == email.expected_action.lower():
            act_score += 1.0 / len(inp.emails)
            
        if email.id in inp.thread_statuses and "thread_status" in labels:
            thr_score += 1.0 / len(inp.emails)
            
    score += (thr_score * 0.2)
    score += (urg_score * 0.2)
    score += (rep_score * 0.2)
    score += (act_score * 0.2)
    
    efficiency = 1.0 - min(1.0, (inp.steps_taken - inp.resolved_count * 2) / max(inp.max_steps, 1))
    score += (max(0, efficiency) * 0.2)
    
    return _to_open_interval(score)

GRADERS: Dict[str, Callable] = {
    "email-easy-001": grade_email_easy_001,
    "email-medium-001": grade_email_medium_001,
    "email-hard-001": grade_email_hard_001,
}

def grade_task(task_id: str, g=None) -> float:
    if task_id not in GRADERS:
        return _to_open_interval(0.0)
    return GRADERS[task_id](g)
