"""
LearnLens AI - Student Router
GET /student/dashboard
GET /student/mastery
GET /student/recommendations
GET /student/subjects
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
import models
import schemas
from auth import decode_access_token
from ai.mastery_engine import mastery_engine
from ai.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/student", tags=["Student"])


def get_current_student(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> models.StudentProfile:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(models.StudentProfile).filter(
        models.StudentProfile.user_id == user.id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    return profile


def build_topic_mastery_list(student: models.StudentProfile, db: Session):
    """Build topic mastery data with topic/subject info."""
    mastery_records = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.student_id == student.id
    ).all()
    
    # Auto-initialize baseline mastery records for new students
    if not mastery_records:
        all_topics = db.query(models.Topic).all()
        for t in all_topics:
            new_tm = models.StudentTopicMastery(
                student_id=student.id,
                topic_id=t.id,
                mastery_score=0.0,
                mastery_level="needs_attention",
                accuracy=0.0,
                attempt_count=0,
                correct_count=0,
                recent_performance=0.0,
                confidence_level=0.0,
                improvement_trend=0.0,
                history=[]
            )
            db.add(new_tm)
        db.commit()
        mastery_records = db.query(models.StudentTopicMastery).filter(
            models.StudentTopicMastery.student_id == student.id
        ).all()
    
    result = []
    for mr in mastery_records:
        topic = db.query(models.Topic).filter(models.Topic.id == mr.topic_id).first()
        if not topic:
            continue
        subject = db.query(models.Subject).filter(models.Subject.id == topic.subject_id).first()
        if not subject:
            continue
        
        result.append({
            "topic_id": topic.id,
            "topic_name": topic.name,
            "topic_code": topic.code,
            "subject_id": subject.id,
            "subject_name": subject.name,
            "difficulty_weight": topic.difficulty_weight,
            "mastery_score": mr.mastery_score,
            "mastery_level": mr.mastery_level,
            "accuracy": mr.accuracy,
            "attempt_count": mr.attempt_count,
            "correct_count": mr.correct_count,
            "recent_performance": mr.recent_performance,
            "confidence_level": mr.confidence_level,
            "improvement_trend": mr.improvement_trend,
            "last_assessed": mr.last_assessed,
            "history": mr.history or [],
        })
    
    return result


@router.get("/dashboard")
def get_student_dashboard(
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get comprehensive student dashboard data."""
    user = db.query(models.User).filter(models.User.id == student.user_id).first()
    topic_mastery_list = build_topic_mastery_list(student, db)
    
    # Overall mastery
    overall_mastery = mastery_engine.compute_overall_mastery(topic_mastery_list)
    
    # Counts
    mastered_count = len([t for t in topic_mastery_list if t["mastery_score"] >= 80])
    needs_attention = len([t for t in topic_mastery_list if t["mastery_score"] < 40])
    
    # Assessment accuracy (weighted average of recent_performance)
    if topic_mastery_list:
        assessment_accuracy = sum(t["recent_performance"] for t in topic_mastery_list) / len(topic_mastery_list)
    else:
        assessment_accuracy = 0.0
    
    # Recommendations
    recommendations_raw = recommendation_engine.generate_recommendations(topic_mastery_list, limit=5)
    
    # Recent assessments
    assessments = db.query(models.Assessment).filter(
        models.Assessment.student_id == student.id,
        models.Assessment.status == "completed"
    ).order_by(models.Assessment.completed_at.desc()).limit(5).all()
    
    recent_assessments = []
    for a in assessments:
        subj = db.query(models.Subject).filter(models.Subject.id == a.subject_id).first()
        recent_assessments.append({
            "id": a.id,
            "subject": subj.name if subj else "Unknown",
            "type": a.assessment_type,
            "score": a.score_percentage,
            "date": a.completed_at.isoformat() if a.completed_at else None,
            "total_questions": a.total_questions,
            "correct": a.correct_answers,
        })
    
    # Progress history
    progress_records = db.query(models.ProgressRecord).filter(
        models.ProgressRecord.student_id == student.id
    ).order_by(models.ProgressRecord.date).limit(30).all()
    
    progress_history = [
        {
            "date": pr.date.strftime("%b %d"),
            "mastery": pr.overall_mastery,
            "accuracy": pr.assessment_accuracy,
            "xp": pr.xp_earned,
        }
        for pr in progress_records
    ]
    
    # Achievements
    achievements = db.query(models.Achievement).filter(
        models.Achievement.student_id == student.id
    ).all()
    
    achievements_out = [
        {
            "badge_id": a.badge_id,
            "badge_name": a.badge_name,
            "description": a.badge_description,
            "icon": a.badge_icon,
            "earned_at": a.earned_at.isoformat(),
        }
        for a in achievements
    ]
    
    # AI Insights
    insights = recommendation_engine.generate_ai_insights(
        topic_mastery_list, overall_mastery, assessment_accuracy
    )
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role,
        },
        "overall_mastery": overall_mastery,
        "current_streak": student.current_streak,
        "total_xp": student.total_xp,
        "level": student.level,
        "assessment_accuracy": round(assessment_accuracy, 1),
        "topics_mastered": mastered_count,
        "topics_needing_attention": needs_attention,
        "recent_assessments": recent_assessments,
        "progress_history": progress_history,
        "topic_mastery": topic_mastery_list,
        "recommendations": recommendations_raw,
        "insights": insights,
        "achievements": achievements_out,
    }


@router.get("/mastery")
def get_student_mastery(
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get detailed topic-wise mastery data."""
    topic_mastery_list = build_topic_mastery_list(student, db)
    overall = mastery_engine.compute_overall_mastery(topic_mastery_list)
    
    return {
        "overall_mastery": overall,
        "topic_mastery": topic_mastery_list,
        "mastered_count": len([t for t in topic_mastery_list if t["mastery_score"] >= 80]),
        "developing_count": len([t for t in topic_mastery_list if 40 <= t["mastery_score"] < 60]),
        "needs_attention_count": len([t for t in topic_mastery_list if t["mastery_score"] < 40]),
    }


@router.get("/recommendations")
def get_recommendations(
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get personalized learning recommendations."""
    topic_mastery_list = build_topic_mastery_list(student, db)
    recommendations = recommendation_engine.generate_recommendations(topic_mastery_list, limit=5)
    return {"recommendations": recommendations}


@router.get("/subjects")
def get_subjects(db: Session = Depends(get_db)):
    """Get all available subjects with their topics."""
    subjects = db.query(models.Subject).all()
    result = []
    for s in subjects:
        topics = db.query(models.Topic).filter(
            models.Topic.subject_id == s.id
        ).order_by(models.Topic.order_index).all()
        result.append({
            "id": s.id,
            "name": s.name,
            "code": s.code,
            "description": s.description,
            "icon": s.icon,
            "color": s.color,
            "topics": [
                {
                    "id": t.id,
                    "name": t.name,
                    "code": t.code,
                    "description": t.description,
                    "difficulty_weight": t.difficulty_weight,
                    "order_index": t.order_index,
                }
                for t in topics
            ],
        })
    return result
