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
# Validator injects API_KEY; fall back to OPENAI_API_KEY or HF_TOKEN
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")

MAX_STEPS = 30
TEMPERATURE = 0.0
MAX_TOKENS = 32

TASK_IDS = ["email-easy-001", "email-medium-001", "email-hard-001"]

SYSTEM_PROMPT = (
    "You are an AI assistant helping triage emails. "
    "At each step, you will be given the current email (sender, subject, body). "
    "Choose ONE action as an integer in {0,1,2,3} only: "
    "0=mark as urgent, 1=archive, 2=reply, 3=mark spam. "
    "Return a JSON object with exactly one key: 'action'."
)


def _parse_action(text: str) -> int:
    text = (text or "").strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "action" in data:
            return int(data["action"])
    except Exception:
        pass
    m = re.search(r"\d+", text)
    if not m:
        return 2
    return int(m.group(0))


def _post(path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    url = f"{ENV_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    resp = requests.post(url, json=payload or {}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: int, reward: float, done: bool, error: str) -> None:
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} "
        f"done={str(done).lower()} error={error or 'none'}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} "
        f"score={score:.3f} rewards={rewards_str}",
        flush=True,
    )


def get_model_action(client: OpenAI, step: int, state: Dict[str, Any]) -> int:
    user_prompt = (
        f"Step: {step}\n"
        f"State: {json.dumps(state, separators=(',', ':'))}\n"
        "Return JSON with action in {0,1,2,3}."
    )
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = (completion.choices[0].message.content or "").strip()
        return _parse_action(content)
    except Exception:
        return 2  # default: reply action


def run_episode(client: OpenAI, task_id: str) -> List[float]:
    """Run a single episode for the given task_id. Returns list of rewards."""
    log_start(task=task_id, env="openenv-email-triage", model=MODEL_NAME)

    resp = _post("/reset", {"task_id": task_id})
    state = resp if isinstance(resp, dict) else {}

    rewards: List[float] = []
    done = False

    for step in range(1, MAX_STEPS + 1):
        if done:
            break

        error_val = "none"
        reward = 0.0
        action = 2

        try:
            action = get_model_action(client, step, state)
            if action not in {0, 1, 2, 3}:
                action = 2

            result = _post("/step", {"action": action})
            state = result.get("state", result)
            reward = float(result.get("reward", 0.0))
            done = bool(result.get("done", False))
        except Exception as exc:
            error_val = str(exc)[:80]
            reward = 0.0
            done = True

        reward = max(0.0, min(1.0, reward))
        rewards.append(reward)
        log_step(step=step, action=action, reward=reward, done=done, error=error_val)

    score = sum(rewards) / len(rewards) if rewards else 0.0
    success = score >= 0.5
    log_end(success=success, steps=len(rewards), score=score, rewards=rewards)
    return rewards


def main() -> None:
    if API_KEY is None:
        raise RuntimeError("Missing API key. Provide API_KEY, OPENAI_API_KEY, or HF_TOKEN.")

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    all_rewards: List[float] = []

    # Run ALL 3 tasks so completed_task_scores has entries for each
    for task_id in TASK_IDS:
        rewards = run_episode(client, task_id)
        all_rewards.extend(rewards)

    total_score = sum(all_rewards) / len(all_rewards) if all_rewards else 0.0
    print(f"[TOTAL] tasks={len(TASK_IDS)} score={total_score:.3f}", flush=True)


if __name__ == "__main__":
    main()
