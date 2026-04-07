"""
Task definitions for OpenEnv Round 1.

Each task has distinct initial inbox statistics so graders can measure
task-specific objectives deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    difficulty: str
    unread_emails_count: int
    urgent_emails_count: int
    spam_count: int
    max_steps: int


TASK_LIST: List[TaskSpec] = [
    TaskSpec(
        task_id="email-easy-001",
        difficulty="easy",
        unread_emails_count=14,
        urgent_emails_count=2,
        spam_count=1,
        max_steps=18,
    ),
    TaskSpec(
        task_id="email-medium-001",
        difficulty="medium",
        unread_emails_count=10,
        urgent_emails_count=4,
        spam_count=4,
        max_steps=22,
    ),
    TaskSpec(
        task_id="email-hard-001",
        difficulty="hard",
        unread_emails_count=16,
        urgent_emails_count=5,
        spam_count=3,
        max_steps=24,
    ),
]

TASK_INDEX: Dict[str, TaskSpec] = {t.task_id: t for t in TASK_LIST}
