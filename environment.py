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
    # Final grader score for the task when episode ends (strictly in (0,1)).
    episode_grader_score: Optional[float] = None


class EmailTriageEnv:
    """
    Email triage RL-style environment with per-task specs and registered graders.

    Actions:
    0 = mark as urgent
    1 = archive
    2 = reply
    3 = mark spam
    """

    def __init__(self) -> None:
        self._state = EmailTriageState()
        self._task_cursor = 0
        self._completed_task_scores: Dict[str, float] = {}

    def _apply_task_spec(self, spec: TaskSpec) -> None:
        self._state = EmailTriageState(
            task_id=spec.task_id,
            emails=list(spec.emails),
            current_email_index=0,
            action_history=[],
            steps_taken=0,
            max_steps=spec.max_steps,
            episode_grader_score=None,
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
        obs = {
            "task_id": self._state.task_id,
            "steps_taken": self._state.steps_taken,
            "max_steps": self._state.max_steps,
            "emails_remaining": len(self._state.emails) - self._state.current_email_index,
            "total_emails": len(self._state.emails),
        }
        
        if self._state.current_email_index < len(self._state.emails):
            current = self._state.emails[self._state.current_email_index]
            obs["current_email"] = {
                "id": current.id,
                "sender": current.sender,
                "subject": current.subject,
                "body": current.body,
            }
        else:
            obs["current_email"] = None
            
        g_in = self._grader_input()
        obs["current_grader_score"] = grade_task(self._state.task_id, g_in)
        
        return obs

    def state(self) -> Dict[str, object]:
        g_in = self._grader_input()
        current_partial = grade_task(self._state.task_id, g_in)
        
        return {
            "task_id": self._state.task_id,
            "current_email_index": self._state.current_email_index,
            "action_history": list(self._state.action_history),
            "steps_taken": self._state.steps_taken,
            "max_steps": self._state.max_steps,
            "episode_grader_score": self._state.episode_grader_score,
            "current_grader_score": current_partial,
            "completed_task_scores": dict(self._completed_task_scores),
            "registered_tasks": [t.task_id for t in TASK_LIST],
        }

    def _grader_input(self) -> GraderInput:
        return GraderInput(
            task_id=self._state.task_id,
            emails=self._state.emails,
            action_history=list(self._state.action_history),
            steps_taken=self._state.steps_taken,
            max_steps=self._state.max_steps,
        )

    def _step_reward_open(self, raw: float) -> float:
        """Step rewards also stay strictly inside (0, 1) for validator consistency."""
        x = float(raw)
        if x <= 0.0:
            return 0.01
        if x >= 1.0:
            return 0.99
        return max(0.01, min(0.99, x))

    def step(self, action: int) -> Dict[str, object]:
        if action not in {0, 1, 2, 3}:
            self._advance_step()
            return {
                "state": self._observation(),
                "reward": self._step_reward_open(0.0),
                "done": self._is_done(),
            }

        reward = 0.0

        if self._state.current_email_index < len(self._state.emails):
            current = self._state.emails[self._state.current_email_index]
            self._state.action_history.append(action)
            self._state.current_email_index += 1
            
            # Partial reward based on correct action
            if action == current.expected_action:
                reward = 1.0  # correct triage
            else:
                reward = 0.0  # incorrect triage
        else:
            # no more emails
            reward = 0.0

        self._advance_step()
        reward = self._step_reward_open(reward)

        done = self._is_done()
        if done and self._state.episode_grader_score is None:
            final = grade_task(self._state.task_id, self._grader_input())
            self._state.episode_grader_score = final
            self._completed_task_scores[self._state.task_id] = final

        return {"state": self._observation(), "reward": reward, "done": done}

    def _advance_step(self) -> None:
        self._state.steps_taken += 1

    def _is_done(self) -> bool:
        no_work_left = self._state.current_email_index >= len(self._state.emails)
        return no_work_left or self._state.steps_taken >= self._state.max_steps
