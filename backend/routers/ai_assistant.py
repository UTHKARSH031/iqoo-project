"""
LearnLens AI - AI Assistant Router
POST /ai/explain
POST /ai/hint
GET  /ai/insights
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
import models
import schemas
from auth import decode_access_token
from ai.llm_service import llm_service
from ai.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


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


@router.post("/explain")
def explain_concept(
    request: schemas.AIExplainRequest,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get AI explanation for a topic concept."""
    topic = db.query(models.Topic).filter(models.Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get student's mastery
    mastery_rec = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.student_id == student.id,
        models.StudentTopicMastery.topic_id == request.topic_id
    ).first()
    mastery_score = mastery_rec.mastery_score if mastery_rec else 0.0
    
    content = llm_service.get_explanation(
        topic_code=topic.code,
        topic_name=topic.name,
        action=request.action,
        mastery_score=mastery_score,
        context=request.context,
    )
    
    return {
        "content": content,
        "topic_name": topic.name,
        "mastery_score": mastery_score,
        "action": request.action,
    }


@router.post("/hint")
def get_hint(
    request: schemas.AIHintRequest,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get a hint for a specific question without revealing the answer."""
    question = db.query(models.Question).filter(models.Question.id == request.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    topic = db.query(models.Topic).filter(models.Topic.id == question.topic_id).first()
    
    hint = llm_service.get_hint_for_question(
        question_text=question.question_text,
        topic_name=topic.name if topic else "this topic",
        correct_answer=str(question.correct_answer),
        student_answer=str(request.student_answer) if request.student_answer else None,
    )
    
    return {
        "hint": hint,
        "question_id": request.question_id,
        "topic_name": topic.name if topic else "Unknown",
    }


@router.get("/insights")
def get_ai_insights(
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get personalized AI insights from student performance data."""
    from routers.student import build_topic_mastery_list
    topic_mastery_list = build_topic_mastery_list(student, db)
    
    if not topic_mastery_list:
        overall_mastery = 0.0
        assessment_accuracy = 0.0
    else:
        from ai.mastery_engine import mastery_engine
        overall_mastery = mastery_engine.compute_overall_mastery(topic_mastery_list)
        assessment_accuracy = sum(t["recent_performance"] for t in topic_mastery_list) / len(topic_mastery_list)
    
    insights = recommendation_engine.generate_ai_insights(
        topic_mastery_list, overall_mastery, assessment_accuracy
    )
    
    return {"insights": insights, "overall_mastery": overall_mastery}
