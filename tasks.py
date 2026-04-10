"""
Task definitions for OpenEnv Round 1.

Each task has distinct initial inbox statistics so graders can measure
task-specific objectives deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class Email:
    id: str
    sender: str
    subject: str
    body: str
    expected_action: int  # 0=urgent, 1=archive, 2=reply, 3=spam

@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    difficulty: str
    emails: List[Email]
    max_steps: int

# Easy Emails
easy_emails = [
    Email("e1", "boss@company.com", "URGENT: Server Down", "The main production server is down. Please fix it immediately!", 0),
    Email("e2", "newsletter@startup.com", "Weekly Tech News", "Here is your weekly digest of tech news...", 1),
    Email("e3", "mom@home.com", "Dinner tonight?", "Are you coming for dinner tonight? Let me know.", 2),
    Email("e4", "spam@lottery-winner.xyz", "You WON $1,000,000!", "Click here to claim your prize now! No hidden fees.", 3),
]

# Medium Emails
medium_emails = [
    Email("m1", "client@external.com", "Project deadline extension", "Can we push the deadline by two days? Let me know.", 2),
    Email("m2", "jira@company.com", "Ticket assigned: EX-102", "You have been assigned to handle EX-102. Please check it.", 1),
    Email("m3", "alert@monitoring.com", "High CPU Usage", "Server node-04 is experiencing 99% CPU for the last 5 minutes.", 0),
    Email("m4", "deals@shoppingsite.com", "Last chance for 50% off!", "Buy now before the sale ends.", 3),
    Email("m5", "hr@company.com", "Action Required: Benefits Enrollment", "Please reply with your updated healthcare forms.", 2),
]

# Hard Emails
hard_emails = [
    Email("h1", "ceo-assistant@company.com", "Meeting rescheduled", "The CEO wants to meet you in 10 minutes regarding the PR crisis.", 0),
    Email("h2", "noreply@github.com", "Daily summary", "2 pull requests merged today.", 1),
    Email("h3", "phishing-test@it-dept.com", "Password expiry notice", "Your password expires in 1 day. Click http://bit.ly/xyz to reset.", 3),
    Email("h4", "unknown@gmail.com", "Quick question regarding project", "Hi, I am reaching out from an external vendor. Can we schedule a call?", 2),
    Email("h5", "support@thirdparty.com", "API deprecation notice", "We are deprecating the API endpoint you are using. Please update code by next week.", 0),
    Email("h6", "recruiters@headhunt.com", "Amazing Job Opportunity", "Are you looking for a new role? We have a great fit.", 3),
]


TASK_LIST: List[TaskSpec] = [
    TaskSpec(
        task_id="email-easy-001",
        difficulty="easy",
        emails=easy_emails,
        max_steps=10,
    ),
    TaskSpec(
        task_id="email-medium-001",
        difficulty="medium",
        emails=medium_emails,
        max_steps=15,
    ),
    TaskSpec(
        task_id="email-hard-001",
        difficulty="hard",
        emails=hard_emails,
        max_steps=20,
    ),
]

TASK_INDEX: Dict[str, TaskSpec] = {t.task_id: t for t in TASK_LIST}
