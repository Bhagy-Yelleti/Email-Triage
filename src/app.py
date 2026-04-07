from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.env import EmailTriageEnv
from src.graders import grade_episode
from src.models import EmailState, EmailTriageAction
from src.tasks import TASKS


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


app = FastAPI(title="OpenEnv Email Triage", version="1.0.0")
env = EmailTriageEnv()


@app.get("/")
async def root():
    return {"service": "openenv-email-triage", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy", "ok": True}


@app.post("/reset")
async def reset(payload: ResetRequest = ResetRequest()):
    return (await env.reset(task_id=payload.task_id)).model_dump()


@app.post("/step")
async def step(action: EmailTriageAction):
    return (await env.step(action)).model_dump()


@app.get("/state")
async def state():
    return await env.state()


@app.get("/tasks")
async def list_tasks() -> Dict[str, Any]:
    """Expose all tasks with grader registration for Phase 2 validation."""
    tasks_out: List[Dict[str, Any]] = []
    for task in TASKS:
        # Use a partial state (1 step taken) to get a non-boundary score.
        partial_state = EmailState(
            episode_id="baseline",
            task_id=task.task_id,
            step_count=1,
        )
        result = grade_episode(task, partial_state)
        tasks_out.append(
            {
                "id": task.task_id,
                "difficulty": task.difficulty,
                "has_grader": True,
                "grader_name": f"grade_episode_{task.task_id.replace('-', '_')}",
                "score": result.score,
            }
        )
    return {
        "count": len(tasks_out),
        "tasks": tasks_out,
        "grader_task_ids": [t.task_id for t in TASKS],
    }


@app.get("/metadata")
async def metadata() -> Dict[str, Any]:
    """OpenEnv-style metadata for runtime validators."""
    task_scores: Dict[str, float] = {}
    for task in TASKS:
        partial_state = EmailState(
            episode_id="baseline",
            task_id=task.task_id,
            step_count=1,
        )
        result = grade_episode(task, partial_state)
        task_scores[task.task_id] = result.score
    return {
        "name": "openenv-email-triage-v1",
        "description": "Realistic email triage with 3 graded tasks; scores in (0,1) open interval.",
        "version": "1.0.0",
        "tasks_with_graders": list(task_scores.keys()),
        "task_scores": task_scores,
    }

