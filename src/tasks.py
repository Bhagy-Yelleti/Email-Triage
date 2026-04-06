from __future__ import annotations

from typing import Dict, List

from src.models import FinalAction, Priority, TaskSpec, Team


TASKS: List[TaskSpec] = [
    TaskSpec(
        task_id="email-easy-001",
        difficulty="easy",
        email_subject="Unable to access account after password reset",
        email_body=(
            "Hi team, I reset my password this morning and now I cannot log in. "
            "I have a customer demo in 2 hours. Please help quickly."
        ),
        expected_priority=Priority.high,
        expected_team=Team.support,
        expected_action=FinalAction.respond,
        constraints=["Do not ask for full password", "Provide secure reset workflow"],
        max_steps=5,
    ),
    TaskSpec(
        task_id="email-medium-001",
        difficulty="medium",
        email_subject="Duplicate charge on enterprise invoice INV-8821",
        email_body=(
            "Our finance team reports two charges for the same annual plan invoice. "
            "Please investigate and reverse the extra payment. CFO asked for update today."
        ),
        expected_priority=Priority.high,
        expected_team=Team.finance,
        expected_action=FinalAction.escalate,
        constraints=["No refund promises before verification", "Collect invoice reference"],
        max_steps=6,
    ),
    TaskSpec(
        task_id="email-hard-001",
        difficulty="hard",
        email_subject="Potential data exfiltration from shared drive",
        email_body=(
            "We noticed unusual bulk downloads from a contractor account around midnight. "
            "Some files may contain customer PII. Please advise immediate next actions."
        ),
        expected_priority=Priority.critical,
        expected_team=Team.security,
        expected_action=FinalAction.escalate,
        constraints=[
            "Treat as potential incident",
            "Do not share sensitive forensic details externally",
            "Initiate containment protocol",
        ],
        max_steps=7,
    ),
]

TASK_INDEX: Dict[str, TaskSpec] = {task.task_id: task for task in TASKS}

