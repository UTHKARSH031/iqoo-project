"""
LearnLens AI - SQLAlchemy ORM Models
Complete database schema for adaptive learning platform
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Enum
)
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    multi_answer = "multi_answer"
    true_false = "true_false"
    short_answer = "short_answer"


class MasteryLevel(str, enum.Enum):
    needs_attention = "needs_attention"
    developing = "developing"
    proficient = "proficient"
    mastered = "mastered"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default=UserRole.student)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    grade = Column(String, nullable=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    enrolled_subjects = Column(JSON, default=[])
    last_activity = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="student_profile")
    assessments = relationship("Assessment", back_populates="student")
    mastery_records = relationship("StudentTopicMastery", back_populates="student")
    achievements = relationship("Achievement", back_populates="student")
    practice_sessions = relationship("PracticeSession", back_populates="student")


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    department = Column(String, nullable=True)
    subjects_taught = Column(JSON, default=[])
    
    user = relationship("User", back_populates="teacher_profile")


class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    color = Column(String, default="#6366f1")
    
    topics = relationship("Topic", back_populates="subject")


class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty_weight = Column(Float, default=1.0)  # importance weight
    prerequisites = Column(JSON, default=[])  # list of topic IDs
    order_index = Column(Integer, default=0)
    
    subject = relationship("Subject", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
    mastery_records = relationship("StudentTopicMastery", back_populates="topic")


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"))
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default=QuestionType.mcq)
    options = Column(JSON, nullable=True)  # list of strings for MCQ
    correct_answer = Column(JSON, nullable=False)  # string or list
    explanation = Column(Text, nullable=True)
    difficulty = Column(String, default=DifficultyLevel.medium)
    learning_objective = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    topic = relationship("Topic", back_populates="questions")


class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    assessment_type = Column(String, default="diagnostic")  # diagnostic, practice, reassessment
    status = Column(String, default="pending")  # pending, in_progress, completed
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    score_percentage = Column(Float, default=0.0)
    time_taken_seconds = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("StudentProfile", back_populates="assessments")
    subject = relationship("Subject")
    answers = relationship("AssessmentAnswer", back_populates="assessment")


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    student_answer = Column(JSON, nullable=True)
    is_correct = Column(Boolean, default=False)
    time_taken_seconds = Column(Integer, default=0)
    
    assessment = relationship("Assessment", back_populates="answers")
    question = relationship("Question")


class StudentTopicMastery(Base):
    __tablename__ = "student_topic_mastery"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    mastery_score = Column(Float, default=0.0)  # 0-100
    mastery_level = Column(String, default=MasteryLevel.needs_attention)
    accuracy = Column(Float, default=0.0)
    attempt_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    recent_performance = Column(Float, default=0.0)  # last 5 questions accuracy
    confidence_level = Column(Float, default=0.0)
    improvement_trend = Column(Float, default=0.0)  # positive = improving
    last_assessed = Column(DateTime, nullable=True)
    history = Column(JSON, default=[])  # list of {date, score} for chart
    
    student = relationship("StudentProfile", back_populates="mastery_records")
    topic = relationship("Topic", back_populates="mastery_records")


class LearningRecommendation(Base):
    __tablename__ = "learning_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    priority_score = Column(Float, default=0.0)
    reason = Column(Text, nullable=True)
    recommended_action = Column(String, nullable=True)  # study, practice, review
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    topic = relationship("Topic")


class PracticeSession(Base):
    __tablename__ = "practice_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    session_score = Column(Float, default=0.0)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("StudentProfile", back_populates="practice_sessions")
    topic = relationship("Topic")


class ProgressRecord(Base):
    __tablename__ = "progress_records"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    date = Column(DateTime, default=datetime.utcnow)
    overall_mastery = Column(Float, default=0.0)
    topics_mastered = Column(Integer, default=0)
    assessment_accuracy = Column(Float, default=0.0)
    xp_earned = Column(Integer, default=0)
    
    subject = relationship("Subject")


class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"))
    badge_id = Column(String, nullable=False)
    badge_name = Column(String, nullable=False)
    badge_description = Column(Text, nullable=True)
    badge_icon = Column(String, nullable=True)
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("StudentProfile", back_populates="achievements")
