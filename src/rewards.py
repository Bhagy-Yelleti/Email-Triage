from __future__ import annotations

from src.models import EmailState, RewardSignal, TaskSpec


def compute_dense_reward(task: TaskSpec, state: EmailState, action_valid: bool) -> RewardSignal:
    components: dict[str, float] = {}

    if not action_valid:
        return RewardSignal(
            value=0.0,
            components={"invalid_action": 0.0},
            rationale="Invalid action format; no positive signal granted.",
        )

    components["priority_alignment"] = 0.15 if state.predicted_priority == task.expected_priority else 0.03
    components["team_alignment"] = 0.20 if state.predicted_team == task.expected_team else 0.03
    components["action_alignment"] = 0.25 if state.predicted_action == task.expected_action else 0.03

    # Encourage progress but decay with unnecessary long trajectories.
    steps_left = max(task.max_steps - state.step_count, 0)
    components["efficiency"] = min(0.15, 0.02 * steps_left)

    if state.done:
        terminal_bonus = 0.25 if (
            state.predicted_priority == task.expected_priority
            and state.predicted_team == task.expected_team
            and state.predicted_action == task.expected_action
        ) else 0.05
        components["terminal_bonus"] = terminal_bonus

    reward_val = sum(components.values()) - state.penalties
    reward_val = max(0.0, min(1.0, reward_val))
    return RewardSignal(
        value=round(reward_val, 3),
        components={k: round(v, 3) for k, v in components.items()},
        rationale="Dense reward reflects correctness, safety, and efficiency.",
    )

