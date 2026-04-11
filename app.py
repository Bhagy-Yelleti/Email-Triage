from __future__ import annotations

from typing import Any, Dict, List, Optional
import os

from fastapi import Body, FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from environment import EmailTriageEnv
from graders import GRADERS, GraderInput
from tasks import TASK_LIST

app = FastAPI(title="OpenEnv Email Triage", version="1.0.0")
env = EmailTriageEnv()


class ResetBody(BaseModel):
    task_id: Optional[str] = None


from pathlib import Path

@app.get("/", response_class=HTMLResponse)
async def home():
    return Path(os.path.join(os.path.dirname(__file__), "frontend.html")).read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "healthy", "ok": True}


@app.get("/reset")
def reset_get():
    return env.reset()


@app.post("/reset")
def reset_post(payload: ResetBody = Body(default_factory=ResetBody)):
    return env.reset(task_id=payload.task_id)


class StepRequest(BaseModel):
    action: int = Field(..., ge=0, le=5)
    category: Optional[str] = None
    urgency_level: Optional[str] = None
    priority_order: Optional[List[int]] = None
    reply: Optional[str] = None
    thread_status: Optional[str] = None
    selected_email_id: Optional[str] = None

@app.post("/step/{action}")
def step_path(action: int):
    return env.step(action)

@app.post("/step")
def step_body(payload: StepRequest = Body(...)):
    return env.step(
        payload.action, 
        payload.category, 
        payload.urgency_level, 
        payload.priority_order, 
        payload.reply, 
        payload.thread_status, 
        payload.selected_email_id
    )


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
                emails=list(spec.emails),
                action_history=[],
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
                emails=list(spec.emails),
                action_history=[],
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


@app.get("/schema")
def schema():
    """OpenEnv runtime schema endpoint — returns action, observation, and state schemas."""
    return {
        "action": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 5,
                    "description": "0=inspect, 1=prioritize, 2=classify, 3=reply/action, 4=resolve",
                },
                "category": {"type": "string"},
                "urgency_level": {"type": "string"},
                "priority_order": {"type": "array", "items": {"type": "integer"}},
                "reply": {"type": "string"},
                "thread_status": {"type": "string"},
                "selected_email_id": {"type": "string"}
            },
            "required": ["action"],
        },
        "observation": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "steps_taken": {"type": "integer"},
                "max_steps": {"type": "integer"},
                "emails_remaining": {"type": "integer"},
                "total_emails": {"type": "integer"},
                "current_email": {
                    "type": ["object", "null"],
                    "properties": {
                        "id": {"type": "string"},
                        "sender": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "category": {"type": "string"},
                        "priority_score": {"type": "integer"},
                        "urgency_level": {"type": "string"},
                        "sentiment": {"type": "string"},
                        "deadline_extracted": {"type": ["string", "null"]},
                        "action_recommendation": {"type": "string"},
                        "suggested_reply": {"type": ["string", "null"]}
                    }
                },
                "current_grader_score": {"type": "number"},
            },
        },
        "state": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "current_email_index": {"type": "integer"},
                "action_history": {"type": "array", "items": {"type": "integer"}},
                "steps_taken": {"type": "integer"},
                "max_steps": {"type": "integer"},
                "episode_grader_score": {"type": ["number", "null"]},
                "current_grader_score": {"type": "number"},
                "current_inbox": {"type": "array", "items": {"type": "string"}},
                "selected_email": {"type": ["string", "null"]},
                "classified_labels": {"type": "object"},
                "pending_threads": {"type": "array", "items": {"type": "string"}},
                "reward_so_far": {"type": "number"},
                "resolved_count": {"type": "integer"},
                "flow_step": {"type": "string"}
            },
        },
    }


@app.post("/mcp")
def mcp(payload: Dict[str, Any] = Body(default={})):
    """Minimal JSON-RPC 2.0 endpoint for OpenEnv MCP compatibility."""
    method = payload.get("method", "")
    req_id = payload.get("id", 1)
    if method == "tools/list":
        result = {
            "tools": [
                {"name": "reset", "description": "Reset the environment"},
                {"name": "step", "description": "Take a step in the environment"},
                {"name": "state", "description": "Get current state"},
            ]
        }
    elif method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "openenv-email-triage", "version": "1.0.0"},
        }
    else:
        result = {"status": "ok", "service": "openenv-email-triage"}
    return {"jsonrpc": "2.0", "id": req_id, "result": result}
