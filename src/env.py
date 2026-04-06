from __future__ import annotations

import uuid
from typing import Dict, Optional

from src.graders import grade_episode
from src.models import (
    EmailState,
    EmailTriageAction,
    EmailTriageObservation,
    FinalAction,
    Priority,
    StepResult,
    Team,
)
from src.rewards import compute_dense_reward
from src.tasks import TASK_INDEX, TASKS


class EmailTriageEnv:
    def __init__(self) -> None:
        self._state: Optional[EmailState] = None
        self._task_cursor = 0

    @property
    def active_task(self):
        if self._state is None:
            return TASKS[0]
        return TASK_INDEX[self._state.task_id]

    def _to_obs(self, last_message: str = "") -> EmailTriageObservation:
        if self._state is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")
        task = TASK_INDEX[self._state.task_id]
        grader = grade_episode(task, self._state)
        return EmailTriageObservation(
            episode_id=self._state.episode_id,
            task_id=task.task_id,
            difficulty=task.difficulty,
            email_subject=task.email_subject,
            email_body=task.email_body,
            constraints=task.constraints,
            step_count=self._state.step_count,
            max_steps=task.max_steps,
            predicted_priority=self._state.predicted_priority,
            predicted_team=self._state.predicted_team,
            predicted_action=self._state.predicted_action,
            partial_score=grader.score,
            last_message=last_message,
        )

    async def reset(self, task_id: Optional[str] = None) -> StepResult:
        if task_id and task_id in TASK_INDEX:
            task = TASK_INDEX[task_id]
        else:
            task = TASKS[self._task_cursor % len(TASKS)]
            self._task_cursor += 1

        self._state = EmailState(episode_id=str(uuid.uuid4()), task_id=task.task_id)
        obs = self._to_obs(last_message="Environment reset successfully.")
        return StepResult(observation=obs, reward=0.0, done=False, info={"task_id": task.task_id})

    async def step(self, action: EmailTriageAction) -> StepResult:
        if self._state is None:
            return await self.reset()

        if self._state.done:
            obs = self._to_obs(last_message="Episode already done. Please reset.")
            return StepResult(observation=obs, reward=0.0, done=True, info={"warning": "done"})

        task = TASK_INDEX[self._state.task_id]
        self._state.step_count += 1
        self._state.history.append(f"{action.kind}:{action.value}")

        action_valid, msg = self._apply_action(action)
        if not action_valid:
            self._state.penalties += 0.05

        if action.kind == "finalize" or self._state.step_count >= task.max_steps:
            self._state.done = True

        reward_signal = compute_dense_reward(task, self._state, action_valid=action_valid)
        grader = grade_episode(task, self._state)
        obs = self._to_obs(last_message=msg)
        info: Dict[str, object] = {
            "task_id": task.task_id,
            "grader_score": grader.score,
            "grader_components": grader.components,
            "reward_components": reward_signal.components,
            "rationale": reward_signal.rationale,
        }
        return StepResult(
            observation=obs,
            reward=reward_signal.value,
            done=self._state.done,
            info=info,
        )

    async def state(self) -> Dict[str, object]:
        if self._state is None:
            return {"initialized": False}
        task = TASK_INDEX[self._state.task_id]
        grader = grade_episode(task, self._state)
        return {
            "initialized": True,
            "state": self._state.model_dump(),
            "grader": grader.model_dump(),
            "task": task.model_dump(),
        }

    def _apply_action(self, action: EmailTriageAction) -> tuple[bool, str]:
        value = (action.value or "").strip().lower()
        kind = action.kind.strip().lower()

        if kind == "set_priority":
            if value in {p.value for p in Priority}:
                self._state.predicted_priority = Priority(value)
                return True, f"Priority set to {value}."
            return False, f"Invalid priority value: {value}"

        if kind == "set_team":
            if value in {t.value for t in Team}:
                self._state.predicted_team = Team(value)
                return True, f"Team set to {value}."
            return False, f"Invalid team value: {value}"

        if kind == "set_action":
            if value in {a.value for a in FinalAction}:
                self._state.predicted_action = FinalAction(value)
                return True, f"Final action set to {value}."
            return False, f"Invalid final action value: {value}"

        if kind == "add_note":
            if not value:
                self._state.penalties += 0.02
                return False, "Empty note is discouraged."
            return True, "Note recorded."

        if kind == "finalize":
            return True, "Episode finalized by agent."

        self._state.penalties += 0.03
        return False, f"Unknown action kind: {kind}"

