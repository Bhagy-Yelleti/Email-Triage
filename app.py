from __future__ import annotations

from fastapi import FastAPI

from environment import EmailTriageEnv

app = FastAPI(title="OpenEnv Email Triage")
env = EmailTriageEnv()


@app.get("/")
def root():
    # Keep the original root payload unchanged.
    return {"service": "openenv-email-triage", "status": "ok"}


@app.get("/reset")
def reset():
    # Reset environment and return initial state.
    return env.reset()


@app.post("/step/{action}")
def step(action: int):
    # Apply integer action and return RL-style transition tuple.
    return env.step(action)


@app.get("/state")
def state():
    # Return current state without mutating environment.
    return env.state()

