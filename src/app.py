from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.env import EmailTriageEnv
from src.models import EmailTriageAction


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


app = FastAPI(title="OpenEnv Email Triage", version="1.0.0")
env = EmailTriageEnv()


@app.get("/")
async def root():
    return {"service": "openenv-email-triage", "status": "ok"}


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/reset")
async def reset(payload: ResetRequest = ResetRequest()):
    return (await env.reset(task_id=payload.task_id)).model_dump()


@app.post("/step")
async def step(action: EmailTriageAction):
    return (await env.step(action)).model_dump()


@app.get("/state")
async def state():
    return await env.state()

