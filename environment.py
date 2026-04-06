from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class EmailTriageState:
    unread_emails_count: int = 12
    urgent_emails_count: int = 3
    spam_count: int = 2
    response_queue: List[str] = field(default_factory=list)
    steps_taken: int = 0
    max_steps: int = 20


class EmailTriageEnv:
    """
    Lightweight deterministic RL-style environment for email triage.

    Actions:
    0 = mark as urgent
    1 = archive
    2 = reply
    3 = mark spam
    """

    def __init__(self) -> None:
        self._state = EmailTriageState()

    def reset(self) -> Dict[str, object]:
        self._state = EmailTriageState()
        return self.state()

    def state(self) -> Dict[str, object]:
        return {
            "unread_emails_count": self._state.unread_emails_count,
            "urgent_emails_count": self._state.urgent_emails_count,
            "spam_count": self._state.spam_count,
            "response_queue": list(self._state.response_queue),
            "steps_taken": self._state.steps_taken,
            "max_steps": self._state.max_steps,
        }

    def step(self, action: int) -> Dict[str, object]:
        if action not in {0, 1, 2, 3}:
            # Invalid action gets zero reward but still advances time.
            self._advance_step()
            return {"state": self.state(), "reward": 0.0, "done": self._is_done()}

        reward = 0.4  # neutral default reward

        # Prioritize available urgent emails first.
        has_urgent = self._state.urgent_emails_count > 0
        has_spam = self._state.spam_count > 0

        if action == 0:  # mark as urgent
            if self._state.unread_emails_count > self._state.urgent_emails_count + self._state.spam_count:
                self._state.urgent_emails_count += 1
                reward = 0.7  # reasonable action
            else:
                reward = 0.0  # wrong action when no regular mail exists

        elif action == 1:  # archive
            if self._state.unread_emails_count > 0 and not has_urgent:
                self._state.unread_emails_count -= 1
                reward = 0.7
            elif has_urgent:
                reward = 0.0
            else:
                reward = 0.4

        elif action == 2:  # reply
            if has_urgent:
                self._state.urgent_emails_count -= 1
                self._state.unread_emails_count = max(0, self._state.unread_emails_count - 1)
                self._state.response_queue.append("urgent_email_replied")
                reward = 1.0  # correct urgent handling
            elif self._state.unread_emails_count > 0:
                self._state.unread_emails_count -= 1
                self._state.response_queue.append("normal_email_replied")
                reward = 0.7
            else:
                reward = 0.4

        elif action == 3:  # mark spam
            if has_spam:
                self._state.spam_count -= 1
                self._state.unread_emails_count = max(0, self._state.unread_emails_count - 1)
                reward = 0.7
            else:
                reward = 0.0

        self._advance_step()
        reward = max(0.0, min(1.0, float(reward)))
        return {"state": self.state(), "reward": reward, "done": self._is_done()}

    def _advance_step(self) -> None:
        self._state.steps_taken += 1

    def _is_done(self) -> bool:
        no_work_left = (
            self._state.unread_emails_count <= 0
            and self._state.urgent_emails_count <= 0
            and self._state.spam_count <= 0
        )
        return no_work_left or self._state.steps_taken >= self._state.max_steps

