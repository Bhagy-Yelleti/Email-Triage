from __future__ import annotations

from src.models import EmailState, GraderResult, TaskSpec


def grade_episode(task: TaskSpec, state: EmailState) -> GraderResult:
    priority_score = 1.0 if state.predicted_priority == task.expected_priority else 0.0
    team_score = 1.0 if state.predicted_team == task.expected_team else 0.0
    action_score = 1.0 if state.predicted_action == task.expected_action else 0.0

    # Efficiency gives partial credit for using fewer steps.
    step_ratio = min(1.0, state.step_count / max(task.max_steps, 1))
    efficiency_score = max(0.0, 1.0 - step_ratio)

    # Heavier weight on critical decision dimensions.
    weighted = (
        0.35 * priority_score
        + 0.30 * team_score
        + 0.25 * action_score
        + 0.10 * efficiency_score
    )

    # Penalties are tracked in-state and clipped here.
    raw = weighted - state.penalties
    score = max(0.0, min(1.0, raw))
    passed = score >= 0.80

    components = {
        "priority": round(priority_score, 3),
        "team": round(team_score, 3),
        "action": round(action_score, 3),
        "efficiency": round(efficiency_score, 3),
        "penalties": round(state.penalties, 3),
        "weighted_raw": round(weighted, 3),
    }
    explanation = (
        f"Priority={priority_score:.1f}, Team={team_score:.1f}, "
        f"Action={action_score:.1f}, Efficiency={efficiency_score:.2f}, "
        f"Penalty={state.penalties:.2f}"
    )
    return GraderResult(
        task_id=task.task_id,
        score=round(score, 3),
        components=components,
        passed=passed,
        explanation=explanation,
    )

