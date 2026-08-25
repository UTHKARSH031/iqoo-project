"""
LearnLens AI - Pydantic Schemas
Request/Response validation models
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str
    role: str = "student"


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    full_name: str
    role: str


class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ── Subject / Topic Schemas ────────────────────────────────────────────────────

class SubjectOut(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    icon: Optional[str]
    color: str
    
    class Config:
        from_attributes = True


class TopicOut(BaseModel):
    id: int
    subject_id: int
    name: str
    code: str
    description: Optional[str]
    difficulty_weight: float
    order_index: int
    
    class Config:
        from_attributes = True


# ── Mastery Schemas ────────────────────────────────────────────────────────────

class TopicMasteryOut(BaseModel):
    topic_id: int
    topic_name: str
    topic_code: str
    subject_id: int
    subject_name: str
    mastery_score: float
    mastery_level: str
    accuracy: float
    attempt_count: int
    correct_count: int
    recent_performance: float
    confidence_level: float
    improvement_trend: float
    last_assessed: Optional[datetime]
    history: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class OverallMasteryOut(BaseModel):
    overall_score: float
    topics_mastered: int
    topics_developing: int
    topics_needs_attention: int
    assessment_accuracy: float
    current_streak: int
    total_xp: int
    level: int
    topic_mastery: List[TopicMasteryOut]


# ── Recommendation Schemas ─────────────────────────────────────────────────────

class RecommendationOut(BaseModel):
    topic_id: int
    topic_name: str
    subject_name: str
    priority_score: float
    reason: str
    recommended_action: str
    mastery_score: float
    mastery_level: str
    urgency: str  # high, medium, low


# ── Assessment Schemas ─────────────────────────────────────────────────────────

class AssessmentStartRequest(BaseModel):
    subject_id: int
    assessment_type: str = "diagnostic"
    num_questions: int = 10


class QuestionOut(BaseModel):
    id: int
    question_text: str
    question_type: str
    options: Optional[List[str]]
    difficulty: str
    topic_name: str
    topic_id: int
    learning_objective: Optional[str]


class AssessmentOut(BaseModel):
    assessment_id: int
    questions: List[QuestionOut]
    subject_name: str
    assessment_type: str
    total_questions: int


class AnswerSubmit(BaseModel):
    question_id: int
    student_answer: Any
    time_taken_seconds: int = 0


class AssessmentSubmitRequest(BaseModel):
    assessment_id: int
    answers: List[AnswerSubmit]


class TopicResultOut(BaseModel):
    topic_id: int
    topic_name: str
    total_questions: int
    correct_answers: int
    accuracy: float
    mastery_before: float
    mastery_after: float
    mastery_delta: float


class AssessmentResultOut(BaseModel):
    assessment_id: int
    total_questions: int
    correct_answers: int
    score_percentage: float
    topic_results: List[TopicResultOut]
    time_taken_seconds: int
    xp_earned: int
    message: str
    recommendations: List[RecommendationOut]


# ── Practice Schemas ───────────────────────────────────────────────────────────

class PracticeGenerateRequest(BaseModel):
    topic_id: int
    difficulty: Optional[str] = None  # auto-selected if None
    num_questions: int = 5


class PracticeSubmitRequest(BaseModel):
    session_id: int
    topic_id: int
    answers: List[AnswerSubmit]


class PracticeResultOut(BaseModel):
    session_id: int
    topic_name: str
    questions_attempted: int
    questions_correct: int
    session_score: float
    mastery_before: float
    mastery_after: float
    mastery_delta: float
    xp_earned: int
    message: str


# ── AI Assistant Schemas ───────────────────────────────────────────────────────

class AIExplainRequest(BaseModel):
    topic_id: int
    action: str  # explain, example, hint, practice, summarize
    context: Optional[str] = None  # additional context


class AIExplainResponse(BaseModel):
    content: str
    topic_name: str
    mastery_score: float
    action: str


class AIHintRequest(BaseModel):
    question_id: int
    student_answer: Optional[Any] = None


class AIInsightOut(BaseModel):
    insight_type: str  # strength, weakness, trend, action
    title: str
    description: str
    icon: str
    priority: int


# ── Student Dashboard Schema ───────────────────────────────────────────────────

class StudentDashboardOut(BaseModel):
    user: UserOut
    overall_mastery: float
    current_streak: int
    total_xp: int
    level: int
    assessment_accuracy: float
    topics_mastered: int
    topics_needing_attention: int
    recent_assessments: List[Dict[str, Any]]
    progress_history: List[Dict[str, Any]]
    topic_mastery: List[TopicMasteryOut]
    recommendations: List[RecommendationOut]
    insights: List[AIInsightOut]
    achievements: List[Dict[str, Any]]


# ── Teacher Dashboard Schema ───────────────────────────────────────────────────

class TeacherDashboardOut(BaseModel):
    total_students: int
    average_class_mastery: float
    average_accuracy: float
    students_needing_attention: int
    topic_performance: List[Dict[str, Any]]
    performance_distribution: List[Dict[str, Any]]
    improvement_trends: List[Dict[str, Any]]
    recent_assessments: List[Dict[str, Any]]
    weak_topics: List[Dict[str, Any]]
    student_list: List[Dict[str, Any]]


class TopicInsightOut(BaseModel):
    topic_id: int
    topic_name: str
    subject_name: str
    class_average_mastery: float
    students_struggling: int
    students_proficient: int
    common_mistakes: List[str]
    ai_recommendation: str
    mastery_distribution: List[Dict[str, Any]]
