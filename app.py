from __future__ import annotations

from fastapi import Body, FastAPI
from pydantic import BaseModel

from environment import EmailTriageEnv

app = FastAPI(title="OpenEnv Email Triage")
env = EmailTriageEnv()


@app.get("/")
def root():
    # Keep the original root payload unchanged.
    return {"service": "openenv-email-triage", "status": "ok"}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/reset")
def reset():
    # Reset environment and return initial state.
    return env.reset()


@app.post("/reset")
def reset_post():
    # OpenEnv validators typically call POST /reset.
    return env.reset()


class StepRequest(BaseModel):
    action: int


@app.post("/step/{action}")
def step(action: int):
    # Apply integer action and return RL-style transition tuple.
    return env.step(action)


@app.post("/step")
def step_post(payload: StepRequest = Body(...)):
    # Alternate contract: POST /step with JSON body {"action": <int>}.
    return env.step(payload.action)


@app.get("/state")
def state():
    # Return current state without mutating environment.
    return env.state()

