"""
Task definitions for OpenEnv Round 1.

Each task has distinct initial inbox statistics so graders can measure
task-specific objectives deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Email:
    id: str
    sender: str
    subject: str
    body: str
    expected_action: int  # 0=urgent, 1=archive, 2=reply, 3=spam
    category: str
    priority_score: int
    urgency_level: str
    sentiment: str
    deadline_extracted: Optional[str]
    action_recommendation: str
    suggested_reply: Optional[str] = None

@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    difficulty: str
    emails: List[Email]
    max_steps: int

# Easy Emails
easy_emails = [
    Email("e1", "boss@company.com", "URGENT: Server Down", "The main production server is down. Please fix it immediately!", 2, "urgent", 10, "high", "negative", "ASAP", "reply", "I am on it."),
]

# Medium Emails
medium_emails = [
    Email("m1", "client@external.com", "Project deadline extension", "Can we push the deadline by two days? Let me know.", 2, "work", 7, "medium", "neutral", "2 days", "reply", "Yes, we can push the deadline."),
    Email("m2", "jira@company.com", "Ticket assigned: EX-102", "You have been assigned to handle EX-102. Please check it.", 1, "work", 4, "low", "neutral", None, "archive"),
    Email("m3", "alert@monitoring.com", "High CPU Usage", "Server node-04 is experiencing 99% CPU for the last 5 minutes.", 0, "urgent", 9, "high", "negative", "now", "flag"),
    Email("m4", "deals@shoppingsite.com", "Last chance for 50% off!", "Buy now before the sale ends.", 3, "spam", 2, "low", "positive", "EOD", "spam"),
    Email("m5", "hr@company.com", "Action Required: Benefits Enrollment", "Please reply with your updated healthcare forms.", 2, "work", 8, "high", "neutral", "tomorrow", "reply", "Please find forms attached."),
]

# Hard Emails
hard_emails = [
    Email("h1", "ceo-assistant@company.com", "RE: Meeting rescheduled", "Following up on our earlier thread. The CEO wants to meet you in 10 minutes regarding the PR crisis. We need a drafted response.", 2, "urgent", 10, "high", "negative", "10 minutes", "follow_up", "We are actively working on the issue."),
    Email("h2", "support@thirdparty.com", "RE: API deprecation notice", "As discussed yesterday, we are deprecating the API. What is your migration timeline?", 2, "work", 8, "high", "negative", "next week", "reply", "We will migrate by end of week."),
]


TASK_LIST: List[TaskSpec] = [
    TaskSpec(
        task_id="email-easy-001",
        difficulty="easy",
        emails=easy_emails,
        max_steps=15,
    ),
    TaskSpec(
        task_id="email-medium-001",
        difficulty="medium",
        emails=medium_emails,
        max_steps=18,
    ),
    TaskSpec(
        task_id="email-hard-001",
        difficulty="hard",
        emails=hard_emails,
        max_steps=24,
    ),
]

TASK_INDEX: Dict[str, TaskSpec] = {t.task_id: t for t in TASK_LIST}
