from __future__ import annotations

import os
from typing import List

import requests

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
MAX_STEPS = 5


def main() -> None:
    rewards: List[float] = []
    print("[START] task=email-triage env=openenv-email-triage", flush=True)

    # Initialize state before taking actions.
    requests.get(f"{ENV_BASE_URL}/reset", timeout=30).raise_for_status()

    # Fixed baseline policy for reproducible scoring.
    policy_actions = [2, 2, 3, 1, 2]
    done = False

    for idx, action in enumerate(policy_actions, start=1):
        response = requests.post(f"{ENV_BASE_URL}/step/{action}", timeout=30)
        response.raise_for_status()
        payload = response.json()
        reward = float(payload.get("reward", 0.0))
        done = bool(payload.get("done", False))
        rewards.append(reward)
        print(
            f"[STEP] step={idx} action={action} reward={reward:.2f} done={str(done).lower()}",
            flush=True,
        )
        if done or idx >= MAX_STEPS:
            break

    avg_score = sum(rewards) / len(rewards) if rewards else 0.0
    print(
        f"[END] success={str(avg_score >= 0.6).lower()} steps={len(rewards)} score={avg_score:.3f}",
        flush=True,
    )


if __name__ == "__main__":
    main()

