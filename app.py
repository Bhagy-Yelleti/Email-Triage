from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field

from environment import EmailTriageEnv
from graders import GRADERS, GraderInput
from tasks import TASK_LIST

app = FastAPI(title="OpenEnv Email Triage", version="1.0.0")
env = EmailTriageEnv()


class ResetBody(BaseModel):
    task_id: Optional[str] = None


@app.get("/")
def root():
    return {"service": "openenv-email-triage", "status": "ok"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/reset")
def reset_get():
    return env.reset()


@app.post("/reset")
def reset_post(payload: ResetBody = Body(default_factory=ResetBody)):
    return env.reset(task_id=payload.task_id)


class StepRequest(BaseModel):
    action: int = Field(..., ge=0, le=3)


@app.post("/step/{action}")
def step_path(action: int):
    return env.step(action)


@app.post("/step")
def step_body(payload: StepRequest = Body(...)):
    return env.step(payload.action)


@app.get("/state")
def state():
    return env.state()


@app.get("/tasks")
def list_tasks() -> Dict[str, Any]:
    """Expose at least 3 tasks with explicit grader registration (Phase 2)."""
    tasks_out: List[Dict[str, Any]] = []
    for spec in TASK_LIST:
        tid = spec.task_id
        # Baseline deterministic score for this task at its initial state.
        # Must remain strictly inside (0, 1).
        baseline = GRADERS[tid](
            GraderInput(
                task_id=tid,
                unread_emails_count=spec.unread_emails_count,
                urgent_emails_count=spec.urgent_emails_count,
                spam_count=spec.spam_count,
                response_queue=[],
                steps_taken=1,
                max_steps=spec.max_steps,
            )
        )
        tasks_out.append(
            {
                "id": tid,
                "difficulty": spec.difficulty,
                "has_grader": tid in GRADERS,
                "grader_name": GRADERS[tid].__name__ if tid in GRADERS else None,
                "score": baseline,
            }
        )
    return {"count": len(tasks_out), "tasks": tasks_out, "grader_task_ids": list(GRADERS.keys())}


@app.get("/metadata")
def metadata():
    """Optional OpenEnv-style metadata for runtime validators."""
    task_scores = {}
    for spec in TASK_LIST:
        tid = spec.task_id
        task_scores[tid] = GRADERS[tid](
            GraderInput(
                task_id=tid,
                unread_emails_count=spec.unread_emails_count,
                urgent_emails_count=spec.urgent_emails_count,
                spam_count=spec.spam_count,
                response_queue=[],
                steps_taken=1,
                max_steps=spec.max_steps,
            )
        )
    return {
        "name": "openenv-email-triage-v1",
        "description": "Realistic email triage with 3 graded tasks; scores in (0,1) open interval.",
        "version": "1.0.0",
        "tasks_with_graders": list(task_scores.keys()),
        "task_scores": task_scores,
    }
