from __future__ import annotations

import json
import os
import textwrap
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN") or "missing-key"
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
TEMPERATURE = 0.0
MAX_TOKENS = 180
MAX_STEPS = 7
BENCHMARK = "openenv-email-triage-v1"
TASK_IDS = ["email-easy-001", "email-medium-001", "email-hard-001"]

SYSTEM_PROMPT = (
    "You are an operations assistant. Return exactly one JSON object with keys "
    "kind and value. Allowed kind: set_priority, set_team, set_action, add_note, finalize. "
    "value must be a lowercase string."
)


@dataclass
class EpisodeResult:
    success: bool
    steps: int
    score: float
    rewards: List[float]


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: str = "none") -> None:
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def build_user_prompt(step: int, observation: Dict[str, object], history: List[str]) -> str:
    history_block = "\n".join(history[-4:]) if history else "None"
    return textwrap.dedent(
        f"""
        Step: {step}
        Task: {observation.get("task_id")}
        Difficulty: {observation.get("difficulty")}
        Email Subject: {observation.get("email_subject")}
        Email Body: {observation.get("email_body")}
        Constraints: {observation.get("constraints")}
        Current guess: priority={observation.get("predicted_priority")}, team={observation.get("predicted_team")}, action={observation.get("predicted_action")}
        Previous steps:
        {history_block}
        Return only JSON.
        """
    ).strip()


def local_fallback_policy(obs: Dict[str, object], step: int) -> Dict[str, str]:
    subject = (obs.get("email_subject") or "").lower()
    body = (obs.get("email_body") or "").lower()
    text = f"{subject} {body}"

    if step == 1:
        if "exfiltration" in text or "pii" in text or "incident" in text:
            return {"kind": "set_priority", "value": "critical"}
        return {"kind": "set_priority", "value": "high"}
    if step == 2:
        if "invoice" in text or "charge" in text or "payment" in text:
            return {"kind": "set_team", "value": "finance"}
        if "exfiltration" in text or "pii" in text:
            return {"kind": "set_team", "value": "security"}
        return {"kind": "set_team", "value": "support"}
    if step == 3:
        if "account" in text and "password" in text:
            return {"kind": "set_action", "value": "respond"}
        return {"kind": "set_action", "value": "escalate"}
    return {"kind": "finalize", "value": "done"}


def get_model_action(client: OpenAI, step: int, obs: Dict[str, object], history: List[str]) -> Dict[str, str]:
    prompt = build_user_prompt(step, obs, history)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        content = (completion.choices[0].message.content or "").strip()
        parsed = json.loads(content)
        kind = str(parsed.get("kind", "")).strip().lower()
        value = str(parsed.get("value", "")).strip().lower()
        if kind and value:
            return {"kind": kind, "value": value}
    except Exception:
        pass
    return local_fallback_policy(obs, step)


def http_post(path: str, payload: Dict[str, object]) -> Dict[str, object]:
    url = f"{ENV_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def run_task(client: OpenAI, task_id: str) -> EpisodeResult:
    rewards: List[float] = []
    history: List[str] = []
    steps_taken = 0

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    result = http_post("/reset", {"task_id": task_id})

    for step in range(1, MAX_STEPS + 1):
        if result.get("done"):
            break
        obs = result.get("observation", {})
        action_obj = get_model_action(client, step, obs, history)
        action_text = f"{action_obj['kind']}:{action_obj['value']}"
        error_val = "none"
        try:
            result = http_post("/step", action_obj)
            reward = float(result.get("reward", 0.0))
        except Exception as exc:
            error_val = str(exc).replace(" ", "_")
            reward = 0.0
            result = {"done": True, "info": {"grader_score": 0.0}}

        rewards.append(reward)
        done = bool(result.get("done", False))
        log_step(step=step, action=action_text, reward=reward, done=done, error=error_val)
        history.append(action_text)
        steps_taken = step
        if done:
            break

    info = result.get("info", {}) if isinstance(result, dict) else {}
    score = float(info.get("grader_score", 0.0))
    success = score >= 0.8
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return EpisodeResult(success=success, steps=steps_taken, score=score, rewards=rewards)


def main() -> None:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    all_scores: List[float] = []
    for task_id in TASK_IDS:
        result = run_task(client, task_id)
        all_scores.append(result.score)
    mean_score = sum(all_scores) / len(all_scores)
    print(f"[END] success={str(mean_score >= 0.8).lower()} steps={len(TASK_IDS)} score={mean_score:.3f} rewards=", flush=True)


if __name__ == "__main__":
    main()

