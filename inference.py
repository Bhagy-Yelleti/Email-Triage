from __future__ import annotations

import os
import json
import re
from typing import Any, Dict, List, Optional

import requests
from openai import OpenAI

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")  # IMPORTANT: no default (per submission checklist)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or HF_TOKEN

MAX_STEPS = 5
TEMPERATURE = 0.0
MAX_TOKENS = 32

SYSTEM_PROMPT = (
    "You are an RL controller for an email triage environment. "
    "At each step, choose ONE action as an integer in {0,1,2,3} only. "
    "Return a JSON object with exactly one key: action."
)


def _parse_action(text: str) -> int:
    text = (text or "").strip()
    # Try JSON first.
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "action" in data:
            a = int(data["action"])
            return a
    except Exception:
        pass
    # Fallback: extract first integer.
    m = re.search(r"-?\\d+", text)
    if not m:
        return -1
    return int(m.group(0))


def _http_post_json(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{ENV_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _http_post(path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{ENV_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    if payload is None:
        resp = requests.post(url, timeout=30)
    else:
        resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: int, reward: float, done: bool, error: str) -> None:
    done_val = str(done).lower()
    error_val = (error or "none").replace(" ", "_")
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def get_model_action(client: OpenAI, step: int, state: Dict[str, Any]) -> int:
    user_prompt = (
        f"Step: {step}\n"
        f"State: {json.dumps(state, separators=(',', ':'))}\n"
        "Return JSON with action in {0,1,2,3}."
    )
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=False,
    )
    content = (completion.choices[0].message.content or "").strip()
    return _parse_action(content)


def main() -> None:
    if OPENAI_API_KEY is None:
        raise RuntimeError("Missing API key. Provide OPENAI_API_KEY or HF_TOKEN.")

    client = OpenAI(base_url=API_BASE_URL, api_key=OPENAI_API_KEY)

    task_name = "email-triage"
    env_name = "openenv-email-triage"
    rewards: List[float] = []
    state: Dict[str, Any] = {}

    log_start(task=task_name, env=env_name, model=MODEL_NAME)

    # Reset (OpenEnv expects POST /reset).
    try:
        reset_payload = _http_post("/reset", payload={})
    except Exception:
        # Fallback for environments that only support GET /reset.
        reset_payload = requests.get(f"{ENV_BASE_URL.rstrip('/')}/reset", timeout=30).json()
    state = reset_payload.get("state", reset_payload) if isinstance(reset_payload, dict) else {}

    done = False
    for step in range(1, MAX_STEPS + 1):
        if done:
            break

        error_val = "none"
        reward = 0.0
        action = 0

        try:
            action = get_model_action(client, step, state)
            # Clamp to valid action space for safety.
            if action not in {0, 1, 2, 3}:
                action = 1

            # Prefer POST /step with body {"action": int}.
            resp = _http_post_json("/step", {"action": action})
            state = resp.get("state", {})
            reward = float(resp.get("reward", 0.0))
            done = bool(resp.get("done", False))
        except Exception as exc:
            error_val = str(exc)
            reward = 0.0
            done = True

        reward = max(0.0, min(1.0, float(reward)))
        rewards.append(reward)
        log_step(step=step, action=action, reward=reward, done=done, error=error_val)

    score = sum(rewards) / len(rewards) if rewards else 0.0
    success = score >= 0.6
    log_end(success=success, steps=len(rewards), score=score, rewards=rewards)


if __name__ == "__main__":
    main()

