from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Team(str, Enum):
    support = "support"
    finance = "finance"
    security = "security"
    engineering = "engineering"
    compliance = "compliance"


class FinalAction(str, Enum):
    respond = "respond"
    escalate = "escalate"
    defer = "defer"
    close = "close"


class TaskSpec(BaseModel):
    task_id: str
    difficulty: str
    email_subject: str
    email_body: str
    expected_priority: Priority
    expected_team: Team
    expected_action: FinalAction
    constraints: List[str] = Field(default_factory=list)
    max_steps: int = 6


class EmailState(BaseModel):
    episode_id: str
    step_count: int = 0
    task_id: str
    done: bool = False
    history: List[str] = Field(default_factory=list)
    predicted_priority: Optional[Priority] = None
    predicted_team: Optional[Team] = None
    predicted_action: Optional[FinalAction] = None
    penalties: float = 0.0


class EmailTriageAction(BaseModel):
    kind: str = Field(
        ...,
        description="One of: set_priority, set_team, set_action, add_note, finalize",
    )
    value: str = Field(..., description="Action payload")


class EmailTriageObservation(BaseModel):
    episode_id: str
    task_id: str
    difficulty: str
    email_subject: str
    email_body: str
    constraints: List[str]
    step_count: int
    max_steps: int
    predicted_priority: Optional[Priority]
    predicted_team: Optional[Team]
    predicted_action: Optional[FinalAction]
    partial_score: float = 0.0
    last_message: str = ""


class RewardSignal(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0)
    components: Dict[str, float] = Field(default_factory=dict)
    rationale: str = ""


class StepResult(BaseModel):
    observation: EmailTriageObservation
    reward: float = Field(..., ge=-1.0, le=1.0)
    done: bool
    info: Dict[str, object] = Field(default_factory=dict)


class GraderResult(BaseModel):
    task_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    components: Dict[str, float]
    passed: bool
    explanation: str
