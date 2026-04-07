from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import Body, FastAPI
from pydantic import BaseModel, Field

from environment import EmailTriageEnv
from graders import GRADERS
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
        tasks_out.append(
            {
                "id": tid,
                "difficulty": spec.difficulty,
                "has_grader": tid in GRADERS,
                "grader_name": GRADERS[tid].__name__ if tid in GRADERS else None,
            }
        )
    return {"count": len(tasks_out), "tasks": tasks_out, "grader_task_ids": list(GRADERS.keys())}


@app.get("/metadata")
def metadata():
    """Optional OpenEnv-style metadata for runtime validators."""
    return {
        "name": "openenv-email-triage-v1",
        "description": "Realistic email triage with 3 graded tasks; scores in (0,1) open interval.",
        "version": "1.0.0",
    }
