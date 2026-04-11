from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from graders import GraderInput, grade_task
from tasks import TASK_INDEX, TASK_LIST, TaskSpec, Email

@dataclass
class EmailTriageState:
    task_id: str = "email-easy-001"
    emails: List[Email] = field(default_factory=list)
    current_email_index: int = 0
    action_history: List[int] = field(default_factory=list)
    steps_taken: int = 0
    max_steps: int = 20
    episode_grader_score: Optional[float] = None
    
    current_inbox: List[str] = field(default_factory=list)
    selected_email: Optional[str] = None
    classified_labels: Dict[str, Dict[str, str]] = field(default_factory=dict)
    pending_threads: List[str] = field(default_factory=list)
    reward_so_far: float = 0.0
    resolved_count: int = 0
    flow_step: str = "inspect_inbox"
    
    # Internal trackers for grading
    priority_order: List[int] = field(default_factory=list)
    replies: Dict[str, str] = field(default_factory=dict)
    thread_statuses: Dict[str, str] = field(default_factory=dict)

class EmailTriageEnv:
    """
    Email triage RL-style environment updated for multi-step transitions.
    """

    def __init__(self) -> None:
        self._state = EmailTriageState()
        self._task_cursor = 0
        self._completed_task_scores: Dict[str, float] = {}

    def _apply_task_spec(self, spec: TaskSpec) -> None:
        self._state = EmailTriageState(
            task_id=spec.task_id,
            emails=list(spec.emails),
            current_inbox=[e.id for e in spec.emails],
            pending_threads=[e.id for e in spec.emails if "RE:" in e.subject or "follow-up" in e.subject.lower()],
            max_steps=spec.max_steps,
        )

    def reset(self, task_id: Optional[str] = None) -> Dict[str, object]:
        if task_id and task_id in TASK_INDEX:
            spec = TASK_INDEX[task_id]
        else:
            spec = TASK_LIST[self._task_cursor % len(TASK_LIST)]
            self._task_cursor += 1
        self._apply_task_spec(spec)
        return self._observation()

    def _observation(self) -> Dict[str, object]:
        g_in = self._grader_input()
        current_score = grade_task(self._state.task_id, g_in)
        
        obs = {
            "task_id": self._state.task_id,
            "steps_taken": self._state.steps_taken,
            "max_steps": self._state.max_steps,
            "emails_remaining": len(self._state.current_inbox),
            "total_emails": len(self._state.emails),
            "current_grader_score": current_score,
            "flow_step": self._state.flow_step,
        }
        
        if self._state.selected_email:
            current = next((e for e in self._state.emails if e.id == self._state.selected_email), None)
            if current:
                obs["current_email"] = {
                    "id": current.id,
                    "sender": current.sender,
                    "subject": current.subject,
                    "body": current.body,
                    "category": current.category,
                    "priority_score": current.priority_score,
                    "urgency_level": current.urgency_level,
                    "sentiment": current.sentiment,
                    "deadline_extracted": current.deadline_extracted,
                    "action_recommendation": current.action_recommendation,
                    "suggested_reply": current.suggested_reply,
                }
            else:
                obs["current_email"] = None
        else:
            obs["current_email"] = None
            
        return obs

    def state(self) -> Dict[str, object]:
        g_in = self._grader_input()
        current_score = grade_task(self._state.task_id, g_in)
        
        return {
            "task_id": self._state.task_id,
            "current_task": self._state.task_id,
            "current_email_index": self._state.current_email_index,
            "action_history": list(self._state.action_history),
            "steps_taken": self._state.steps_taken,
            "max_steps": self._state.max_steps,
            "episode_grader_score": self._state.episode_grader_score,
            "current_grader_score": current_score,
            "current_inbox": list(self._state.current_inbox),
            "inbox_queue": list(self._state.current_inbox),
            "selected_email": self._state.selected_email,
            "classified_labels": dict(self._state.classified_labels),
            "pending_threads": list(self._state.pending_threads),
            "thread_status": list(self._state.pending_threads),
            "reward_so_far": self._state.reward_so_far,
            "resolved_count": self._state.resolved_count,
            "flow_step": self._state.flow_step,
            "done": len(self._state.current_inbox) == 0 or self._state.steps_taken >= self._state.max_steps,
        }

    def _grader_input(self) -> GraderInput:
        return GraderInput(
            task_id=self._state.task_id,
            emails=self._state.emails,
            action_history=list(self._state.action_history),
            steps_taken=self._state.steps_taken,
            max_steps=self._state.max_steps,
            classified_labels=self._state.classified_labels,
            priority_order=self._state.priority_order,
            replies=self._state.replies,
            thread_statuses=self._state.thread_statuses,
            resolved_count=self._state.resolved_count,
        )

    def _step_reward_open(self, raw: float) -> float:
        x = float(raw)
        if x <= 0.0: return 0.01
        if x >= 1.0: return 0.99
        return max(0.01, min(0.99, x))

    def step(self, action: int, category: Optional[str] = None, urgency_level: Optional[str] = None, priority_order: Optional[List[int]] = None, reply: Optional[str] = None, thread_status: Optional[str] = None, selected_email_id: Optional[str] = None) -> Dict[str, object]:
        self._state.action_history.append(action)
        self._state.steps_taken += 1
        
        penalty = 0.0
        
        # Maps user's example flow:
        # action 0 = inspect -> moves to select
        # action 5 = select email
        # action 1 = prioritize
        # action 2 = classify
        # action 3 = reply/action
        # action 4 = resolve
        
        if action == 0:
            self._state.flow_step = "select_email"
            
        elif action == 5:
            if selected_email_id and selected_email_id in self._state.current_inbox:
                self._state.selected_email = selected_email_id
                self._state.flow_step = "classify"
            else:
                penalty -= 0.10 # Invalid email selection
                
        elif action == 1:
            if priority_order:
                self._state.priority_order = priority_order
                self._state.flow_step = "select_email"
                
        elif action == 2:
            if self._state.selected_email:
                if self._state.selected_email not in self._state.classified_labels:
                    self._state.classified_labels[self._state.selected_email] = {}
                if category:
                    self._state.classified_labels[self._state.selected_email]["category"] = category
                if urgency_level:
                    self._state.classified_labels[self._state.selected_email]["urgency_level"] = urgency_level
                self._state.flow_step = "action_or_reply"
            else:
                penalty -= 0.10
                
        elif action == 3:
            if self._state.selected_email:
                if reply:
                    self._state.replies[self._state.selected_email] = reply
                if thread_status:
                    self._state.thread_statuses[self._state.selected_email] = thread_status
                
                # Check for wrong spam escalation penalty
                current_email = next((e for e in self._state.emails if e.id == self._state.selected_email), None)
                if current_email and thread_status == "spam" and current_email.expected_action != "spam":
                    penalty -= 0.15 # Wrong escalation
                    
                self._state.flow_step = "resolve"
            else:
                penalty -= 0.10
                
        elif action == 4:
            if self._state.selected_email in self._state.current_inbox:
                self._state.current_inbox.remove(self._state.selected_email)
                if self._state.selected_email in self._state.pending_threads:
                    self._state.pending_threads.remove(self._state.selected_email)
                self._state.resolved_count += 1
                self._state.selected_email = None
                self._state.flow_step = "inspect_inbox"
            else:
                penalty -= 0.10
                
        else:
            penalty -= 0.10 # Unknown action / Repeated action

        # Infinite loop penalty
        if self._state.steps_taken > self._state.max_steps * 1.5:
            penalty -= 0.10
            
        # ====================
        # Dynamic Events Logic
        # ====================
        if self._state.task_id == "email-dyn-hard-001":
            # Check if critical email is unresolved for too long (e.g. CEO email 'd1')
            if "d1" in self._state.current_inbox and self._state.steps_taken == 6:
                follow_up = Email("d1_esc", "ceo@company.com", "URGENT: Press Leak ESCALATION", "Why hasn't this been fixed yet?!", 0, "urgent", 10, "high", "negative", "NOW", "flag", None)
                self._state.emails.append(follow_up)
                self._state.current_inbox.append("d1_esc")
                
            # If a deadline is missed due to step progression
            if "d2" in self._state.current_inbox and self._state.steps_taken == 4: # Fraud alert
                # Boost priority implicitly dynamically handled by grader
                pass
                
            # Wrong action creates customer escalation
            if action == 4 and self._state.selected_email == "d3":
                labels = self._state.classified_labels.get("d3", {})
                if labels.get("category", "") != "work" or labels.get("urgency_level", "") != "high":
                    follow_up = Email("d3_esc", "angry-customer@client.com", "UNACCEPTABLE OUTAGE", "I am canceling my subscription.", 2, "work", 10, "high", "negative", "now", "reply", "We sincerely apologize.")
                    self._state.emails.append(follow_up)
                    self._state.current_inbox.append("d3_esc")
                    
        # ====================
            
        old_score = self._state.reward_so_far
        g_in = self._grader_input()
        new_score = grade_task(self._state.task_id, g_in)
        
        # The step reward is the delta of the grader score plus any penalties
        step_reward = max(0.0, new_score - old_score) + penalty
        self._state.reward_so_far = new_score
        
        done = len(self._state.current_inbox) == 0 or self._state.steps_taken >= self._state.max_steps
        
        if done and self._state.episode_grader_score is None:
            self._state.episode_grader_score = new_score
            self._completed_task_scores[self._state.task_id] = new_score
            
        return {
            "state": self._observation(),
            "reward": self._step_reward_open(step_reward),
            "done": done
        }
