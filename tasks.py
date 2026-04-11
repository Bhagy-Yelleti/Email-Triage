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
    task_seed: int = 42

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
    Email("h3", "legal@company.com", "FWD: Confidential litigation", "Do NOT forward this. We need to escalate the evidence bundle by 5PM. Context required.", 0, "urgent", 10, "high", "negative", "5PM", "flag", None),
]

# Dynamic Flagship Task Emails
dyn_hard_emails = [
    Email("d1", "ceo@company.com", "URGENT: Press Leak", "A leak just hit the press. Fix this in the next 10 minutes.", 0, "urgent", 10, "high", "negative", "10 minutes", "flag", None),
    Email("d2", "fraud-alert@bank.com", "Suspicious Account Activity", "We detected unusual login attempts from Russia. Secure the account.", 0, "urgent", 9, "high", "negative", "ASAP", "flag", None),
    Email("d3", "angry-customer@client.com", "Service Outage", "We have been offline for 2 hours! Unacceptable. Escalating.", 2, "work", 8, "high", "negative", "now", "reply", "We are looking into the outage right now."),
    Email("d4", "hr@company.com", "Performance Review Setup", "Please set up your yearly review by tomorrow.", 1, "work", 5, "medium", "neutral", "tomorrow", "archive", None),
    Email("d5", "promo@sass.com", "Black Friday Deal", "Get 90% off our sass product for a limited time.", 3, "spam", 1, "low", "positive", "none", "spam", None),
]

# Adversarial Enterprise Inbox (Flagship Hard Task)
adv_hard_emails = [
    Email("a1", "ceo@company.com", "Project Alpha Launch", "We need to clear the launch blocks ASAP.", 0, "urgent", 10, "high", "neutral", "EOD", "escalate", "Escalating now."),
    Email("a2", "ceo-support@company-security.com", "URGENT: Mandatory Password Reset", "Your corporate account was flagged. Reset immediately.", 3, "phishing", 0, "high", "negative", "ASAP", "quarantine", None),
    Email("a3", "fraud@bank-alerts.com", "Suspicious login attempt", "Unknown login from IP 192.168.0.1. Please click to review.", 3, "phishing", 0, "high", "negative", "now", "quarantine", None),
    Email("a4", "legal@company.com", "FWD: Confidential litigation", "Do NOT forward this. We need to escalate the evidence bundle by 5PM.", 0, "urgent", 10, "high", "negative", "5PM", "escalate", None),
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
    TaskSpec(
        task_id="email-dyn-hard-001",
        difficulty="hard-dynamic",
        emails=dyn_hard_emails,
        max_steps=30,
    ),
    TaskSpec(
        task_id="email-adv-hard-001",
        difficulty="hard-adversarial",
        emails=adv_hard_emails,
        max_steps=35,
        task_seed=1337,
    ),
]

TASK_INDEX: Dict[str, TaskSpec] = {t.task_id: t for t in TASK_LIST}
