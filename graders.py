from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from tasks import TASK_INDEX, TaskSpec, Email

_EPS = 0.05
_MIN = _EPS
_MAX = 1.0 - _EPS

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

def _unified_grading_logic(inp: GraderInput) -> float:
    if not inp.emails:
        return _to_open_interval(0.0)
        
    num_emails = len(inp.emails)
    
    # Feature 1: Classification Score (0 to 1)
    classification_score = 0.0
    for e in inp.emails:
        labels = inp.classified_labels.get(e.id, {})
        if labels.get("category", "").lower() == e.category.lower():
            classification_score += 1.0 / num_emails
            
    # Feature 2: Urgency Score (0 to 1)
    urgency_score = 0.0
    for e in inp.emails:
        labels = inp.classified_labels.get(e.id, {})
        if labels.get("urgency_level", "").lower() == e.urgency_level.lower():
            urgency_score += 1.0 / num_emails
            
    # Feature 3: Action Score (0 to 1)
    # Includes standard action matching and reply semantics matching
    action_score = 0.0
    for e in inp.emails:
        if inp.thread_statuses.get(e.id, "").lower() == str(e.expected_action).lower() or inp.thread_statuses.get(e.id, "").lower() == "reply" or str(e.expected_action) in inp.thread_statuses.get(e.id, ""):
            match_val = 0.5
            if e.suggested_reply and e.id in inp.replies and len(inp.replies[e.id]) > 5:
                match_val += 0.5
            elif not e.suggested_reply:
                match_val += 0.5
            action_score += match_val / num_emails
            
    # Feature 4: Ranking Score (0 to 1)
    ranking_score = 0.0
    if len(inp.emails) <= 1:
        ranking_score = 1.0 # Auto-pass for 1 email
    else:
        if len(inp.priority_order) >= 1:
            idx1 = inp.priority_order[0]
            if idx1 < len(inp.emails) and inp.emails[idx1].urgency_level == 'high':
                ranking_score += 0.5
            if len(inp.priority_order) >= 2:
                idx2 = inp.priority_order[1]
                if idx2 < len(inp.emails) and inp.emails[idx2].urgency_level in ['high', 'medium']:
                    ranking_score += 0.5
        
    # Feature 5: Efficiency Score (0 to 1)
    base_actions_needed = inp.resolved_count * 2
    efficiency_score = 1.0 - min(1.0, max(0.0, (inp.steps_taken - base_actions_needed)) / max(inp.max_steps, 1))
    if inp.resolved_count == 0:
        efficiency_score = 0.0
        
    # User Required Mathematical Structure:
    score = (
        0.25 * classification_score +
        0.20 * urgency_score +
        0.20 * ranking_score +
        0.20 * action_score +
        0.15 * efficiency_score
    )
    
    return _to_open_interval(score)

def grade_email_easy_001(g=None) -> float:
    return _unified_grading_logic(_coerce(g, "email-easy-001"))

def grade_email_medium_001(g=None) -> float:
    return _unified_grading_logic(_coerce(g, "email-medium-001"))

def grade_email_hard_001(g=None) -> float:
    return _unified_grading_logic(_coerce(g, "email-hard-001"))

def grade_email_adv_hard_001(g=None) -> float:
    inp = _coerce(g, "email-adv-hard-001")
    if not inp.emails:
        return _to_open_interval(0.0)
        
    crit_res = 0.0
    phish_det = 0.0
    st_prio = 0.0
    del_cons = 0.0
    eff = 0.0
    th_mem = 0.0
    
    resolved = 0
    num_emails = len(inp.emails)
    
    # Analyze core metrics
    for e in inp.emails:
        labels = inp.classified_labels.get(e.id, {})
        thread_stat = inp.thread_statuses.get(e.id, "")
        
        is_resolved = e.id in inp.thread_statuses
        if is_resolved:
            resolved += 1
            if "breach" not in e.id and "nag" not in e.id:
                crit_res += 1.0 / max(1, len([x for x in inp.emails if "breach" not in x.id and "nag" not in x.id]))
                
        # Phishing detection
        if e.id in ["a2", "a3"]:
            if labels.get("category", "") == "phishing" and thread_stat == "quarantine":
                phish_det += 0.5
                
        # Thread memory
        if e.id in inp.replies and thread_stat:
            # If they provided a reply to something requiring it
            if "reply" in thread_stat or "escalate" in thread_stat:
                th_mem += 1.0 / len(inp.emails)
                
    # Stakeholder priority (Did they prioritize CEO correctly?)
    st_prio = 1.0
    if len(inp.priority_order) >= 1:
        first_e = inp.emails[inp.priority_order[0]] if inp.priority_order[0] < len(inp.emails) else None
        if first_e and "ceo@company.com" not in first_e.sender:
            st_prio -= 0.5
            
    # Delayed consequence prevention: Max if no "breach" or "nag" emails generated
    breaches = len([e for e in inp.emails if "breach" in e.id or "nag" in e.id])
    if breaches == 0:
        del_cons = 1.0
    else:
        del_cons = max(0.0, 1.0 - (0.5 * breaches))
        
    base_actions = resolved * 2
    eff = 1.0 - min(1.0, max(0.0, (inp.steps_taken - base_actions)) / max(inp.max_steps, 1))
    
    score = (
        0.20 * crit_res +
        0.20 * phish_det +
        0.15 * st_prio +
        0.15 * del_cons +
        0.15 * eff +
        0.15 * th_mem
    )
    
    return _to_open_interval(score)

def grade_email_dyn_hard_001(g=None) -> float:
    inp = _coerce(g, "email-dyn-hard-001")
    if not inp.emails:
        return _to_open_interval(0.0)
        
    # Stakeholder weights
    weights = {"ceo": 1.0, "fraud": 0.9, "customer": 0.8, "hr": 0.5, "promo": 0.1}
    
    # Adaptive reward metric trackers
    c_res = 0.0
    esc_hand = 0.0
    st_prio = 0.0
    dyn_fup = 0.0
    th_mem = 0.0
    
    resolved = 0
    total_weight = sum([weights.get(e.sender.split("@")[0].split("-")[0], 0.5) for e in inp.emails])
    
    for e in inp.emails:
        s_weight = weights.get(e.sender.split("@")[0].split("-")[0], 0.5)
        
        is_resolved = e.id not in [x.id for x in inp.emails if "esc" in x.id] and e.id in inp.thread_statuses
        if is_resolved:
            c_res += s_weight / total_weight
            resolved += 1
            
        if "esc" in e.id:
            # Handling escalations correctly
            if e.id in inp.thread_statuses:
                esc_hand += 1.0
                dyn_fup += 1.0
                
        # thread memory: Did agent refer to correct thread status
        if e.id in inp.replies and e.suggested_reply:
            if str(e.expected_action) in inp.thread_statuses.get(e.id, ""):
                th_mem += 1.0 / len(inp.emails)
                
    if len([e for e in inp.emails if "esc" in e.id]) > 0:
        esc_hand /= max(1, len([e for e in inp.emails if "esc" in e.id]))
        dyn_fup /= max(1, len([e for e in inp.emails if "esc" in e.id]))
    else:
        esc_hand = 1.0
        dyn_fup = 1.0

    # Stakeholder priority alignment (did they prioritize highest weight first?)
    st_prio = 1.0 # Base
    if len(inp.priority_order) >= 1:
        first_e = inp.emails[inp.priority_order[0]] if inp.priority_order[0] < len(inp.emails) else None
        if first_e and weights.get(first_e.sender.split("@")[0].split("-")[0], 0) < 0.9:
            st_prio -= 0.5 # Penalty for not prioritizing CEO or Fraud
            
    base_actions = resolved * 2
    eff = 1.0 - min(1.0, max(0.0, (inp.steps_taken - base_actions)) / max(inp.max_steps, 1))

    score = (
        0.25 * c_res +
        0.20 * esc_hand +
        0.15 * st_prio +
        0.15 * eff +
        0.15 * dyn_fup +
        0.10 * th_mem
    )
    
    return _to_open_interval(score)

GRADERS: Dict[str, Callable] = {
    "email-easy-001": grade_email_easy_001,
    "email-medium-001": grade_email_medium_001,
    "email-dyn-hard-001": grade_email_dyn_hard_001,
    "email-adv-hard-001": grade_email_adv_hard_001,
}

def grade_task(task_id: str, g=None) -> float:
    if task_id not in GRADERS:
        return _to_open_interval(0.0)
    return GRADERS[task_id](g)
