"Shared data models for MathTutor AI."

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any
import datetime
import uuid


class Subject(str, Enum):
    ALGEBRA = "algebra"
    GEOMETRY = "geometria"
    PHYSICS = "fisica"
    CALCULUS = "calculo"


class VerificationStatus(str, Enum):
    VERIFIED = "Verified"
    NUMERICAL_CHECK = "Numerical check"
    CANNOT_VERIFY = "Could not verify"
    OUT_OF_SCOPE = "Out of scope"


@dataclass
class SolutionStep:
    step_number: int
    previous_expr: str
    operation: str
    resulting_expr: str
    explanation_brief: str
    explanation_detailed: str
    restrictions: Optional[str] = None


@dataclass
class SolutionResult:
    exercise_id: str
    subject: Subject
    original_input: str
    interpreted_input: str
    domain_assumptions: str
    steps: List[SolutionStep] = field(default_factory=list)
    final_answer: str = ""
    units: Optional[str] = None
    verification_status: VerificationStatus = VerificationStatus.VERIFIED
    verification_reason: str = ""
    substitution_check: Optional[str] = None
    plot_data: Optional[Dict[str, Any]] = None


@dataclass
class StudentAttempt:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    exercise_id: str = ""
    topic: str = ""
    difficulty_level: int = 1
    seed: Optional[int] = None
    user_answer: str = ""
    is_correct: bool = False
    hints_used: int = 0
    attempt_count: int = 1
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class UserProfile:
    id: str = "default_student"
    name: str = "Student"
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)
    preferences: Dict[str, Any] = field(default_factory=dict)
