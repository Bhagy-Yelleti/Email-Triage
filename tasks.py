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
    Email("e1", "boss@company.com", "URGENT: Server Down", "The main production server is down. Please fix it immediately!", 0, "work", 10, "high", "negative", "ASAP", "flag"),
    Email("e2", "newsletter@startup.com", "Weekly Tech News", "Here is your weekly digest of tech news...", 1, "promotions", 2, "low", "neutral", None, "archive"),
    Email("e3", "mom@home.com", "Dinner tonight?", "Are you coming for dinner tonight? Let me know.", 2, "personal", 5, "medium", "positive", "tonight", "reply", "Yes, I will be there!"),
    Email("e4", "spam@lottery-winner.xyz", "You WON $1,000,000!", "Click here to claim your prize now! No hidden fees.", 3, "spam", 1, "low", "neutral", None, "spam"),
    Email("e5", "refunds@shopping.com", "Refund Request Received", "We have received your refund request for order #123. Please reply to confirm.", 2, "finance", 6, "medium", "neutral", "within 2 days", "reply", "I confirm the refund request for order #123."),
    Email("e6", "noreply@bank.com", "Bank fraud alert", "We detected unusual activity on your credit card. Log in immediately to verify.", 0, "finance", 9, "high", "negative", "immediately", "flag"),
]

# Medium Emails
medium_emails = [
    Email("m1", "client@external.com", "Project deadline extension", "Can we push the deadline by two days? Let me know.", 2, "work", 7, "medium", "neutral", "2 days", "reply", "Yes, we can push the deadline. I will update the timeline."),
    Email("m2", "jira@company.com", "Ticket assigned: EX-102", "You have been assigned to handle EX-102. Please check it.", 1, "work", 4, "low", "neutral", None, "archive"),
    Email("m3", "alert@monitoring.com", "High CPU Usage", "Server node-04 is experiencing 99% CPU for the last 5 minutes.", 0, "work", 9, "high", "negative", "now", "flag"),
    Email("m4", "deals@shoppingsite.com", "Last chance for 50% off!", "Buy now before the sale ends.", 3, "promotions", 2, "low", "positive", "EOD", "spam"),
    Email("m5", "hr@company.com", "Action Required: Benefits Enrollment", "Please reply with your updated healthcare forms.", 2, "work", 8, "high", "neutral", "tomorrow", "reply", "Please find my updated healthcare forms attached."),
    Email("m6", "university@college.edu", "College assignment reminder", "Your final term paper is due this Friday.", 0, "work", 8, "high", "neutral", "this Friday", "flag"),
]

# Hard Emails
hard_emails = [
    Email("h1", "ceo-assistant@company.com", "Meeting rescheduled", "The CEO wants to meet you in 10 minutes regarding the PR crisis.", 0, "work", 10, "high", "negative", "10 minutes", "flag"),
    Email("h2", "noreply@github.com", "Daily summary", "2 pull requests merged today.", 1, "work", 3, "low", "neutral", None, "archive"),
    Email("h3", "phishing-test@it-dept.com", "Password expiry notice", "Your password expires in 1 day. Click http://bit.ly/xyz to reset.", 3, "spam", 1, "low", "neutral", "1 day", "spam"),
    Email("h4", "unknown@gmail.com", "Quick question regarding project", "Hi, I am reaching out from an external vendor. Can we schedule a call?", 2, "work", 6, "medium", "neutral", None, "reply", "Hello, yes we can schedule a call, how about tomorrow at 2 PM?"),
    Email("h5", "support@thirdparty.com", "API deprecation notice", "We are deprecating the API endpoint you are using. Please update code by next week.", 0, "work", 8, "high", "negative", "next week", "flag"),
    Email("h6", "recruiters@headhunt.com", "Amazing Job Opportunity", "Are you looking for a new role? We have a great fit.", 3, "promotions", 2, "low", "positive", None, "spam"),
    Email("h7", "careers@toptech.com", "Internship confirmation", "Congratulations! We would like to offer you the internship position. Please reply to accept.", 2, "work", 9, "high", "positive", "EOD", "reply", "Thank you! I am thrilled to accept the internship offer."),
    Email("h8", "security@apple-id-verify.com", "OTP phishing scam", "Your account will be locked. Enter your OTP immediately to verify your identity.", 3, "spam", 10, "high", "negative", "immediately", "spam"),
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
