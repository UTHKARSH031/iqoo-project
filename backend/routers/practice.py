"""
LearnLens AI - Practice Router
POST /practice/generate
POST /practice/submit
GET  /practice/history
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import get_db
import models
import schemas
from auth import decode_access_token
from ai.question_generator import question_generator
from ai.mastery_engine import mastery_engine

router = APIRouter(prefix="/practice", tags=["Practice"])


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


@router.post("/generate")
def generate_practice(
    request: schemas.PracticeGenerateRequest,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Generate targeted practice questions for a specific topic."""
    topic = db.query(models.Topic).filter(models.Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Get student's current mastery for this topic
    mastery_rec = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.student_id == student.id,
        models.StudentTopicMastery.topic_id == request.topic_id
    ).first()
    mastery_score = mastery_rec.mastery_score if mastery_rec else 50.0
    
    # Generate questions
    raw_questions = question_generator.get_questions_for_topic(
        topic_code=topic.code,
        difficulty=request.difficulty,
        num_questions=request.num_questions,
        student_mastery=mastery_score,
    )
    
    # Create practice session
    session = models.PracticeSession(
        student_id=student.id,
        topic_id=topic.id,
    )
    db.add(session)
    db.flush()
    
    # Create question records
    questions_out = []
    for q_data in raw_questions:
        question = models.Question(
            topic_id=topic.id,
            question_text=q_data["question_text"],
            question_type=q_data["question_type"],
            options=q_data.get("options"),
            correct_answer=q_data["correct_answer"],
            explanation=q_data.get("explanation"),
            difficulty=q_data["difficulty"],
            learning_objective=q_data.get("learning_objective"),
            is_ai_generated=True,
        )
        db.add(question)
        db.flush()
        
        questions_out.append({
            "id": question.id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "options": question.options,
            "difficulty": question.difficulty,
            "topic_name": topic.name,
            "topic_id": topic.id,
            "learning_objective": question.learning_objective,
        })
    
    db.commit()
    
    return {
        "session_id": session.id,
        "topic_id": topic.id,
        "topic_name": topic.name,
        "current_mastery": mastery_score,
        "difficulty_selected": request.difficulty or "auto",
        "questions": questions_out,
        "context": f"Based on your {mastery_score:.0f}% mastery, these questions are tailored to help you improve.",
    }


@router.post("/submit")
def submit_practice(
    request: schemas.PracticeSubmitRequest,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit practice session answers and update mastery."""
    session = db.query(models.PracticeSession).filter(
        models.PracticeSession.id == request.session_id,
        models.PracticeSession.student_id == student.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Practice session not found")
    
    topic = db.query(models.Topic).filter(models.Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Process answers
    correct_count = 0
    answer_data = []
    
    for ans in request.answers:
        question = db.query(models.Question).filter(models.Question.id == ans.question_id).first()
        if not question:
            continue
        
        correct_answer = question.correct_answer
        student_answer = ans.student_answer
        
        is_correct = False
        if isinstance(correct_answer, list):
            if isinstance(student_answer, list):
                is_correct = set(str(x) for x in correct_answer) == set(str(x) for x in student_answer)
        else:
            is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()
        
        if is_correct:
            correct_count += 1
        
        answer_data.append({"is_correct": is_correct, "difficulty": question.difficulty})
    
    total = len(request.answers) if request.answers else 1
    session_score = (correct_count / total) * 100
    
    # Get existing mastery
    mastery_rec = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.student_id == student.id,
        models.StudentTopicMastery.topic_id == request.topic_id
    ).first()
    
    mastery_before = mastery_rec.mastery_score if mastery_rec else 0.0
    
    existing_data = None
    if mastery_rec:
        existing_data = {
            "mastery_score": mastery_rec.mastery_score,
            "accuracy": mastery_rec.accuracy,
            "attempt_count": mastery_rec.attempt_count,
            "correct_count": mastery_rec.correct_count,
        }
    
    # Compute new mastery
    new_mastery_data = mastery_engine.compute_mastery(request.topic_id, answer_data, existing_data)
    mastery_after = new_mastery_data["mastery_score"]
    
    # Update mastery
    if mastery_rec:
        mastery_rec.mastery_score = mastery_after
        mastery_rec.mastery_level = new_mastery_data["mastery_level"]
        mastery_rec.accuracy = new_mastery_data["accuracy"]
        mastery_rec.attempt_count = (mastery_rec.attempt_count or 0) + total
        mastery_rec.correct_count = (mastery_rec.correct_count or 0) + correct_count
        mastery_rec.recent_performance = new_mastery_data["recent_performance"]
        mastery_rec.improvement_trend = new_mastery_data["improvement_trend"]
        mastery_rec.last_assessed = datetime.utcnow()
        history = mastery_rec.history or []
        history.append({"date": datetime.utcnow().isoformat(), "score": mastery_after})
        mastery_rec.history = history
    else:
        new_rec = models.StudentTopicMastery(
            student_id=student.id,
            topic_id=request.topic_id,
            mastery_score=mastery_after,
            mastery_level=new_mastery_data["mastery_level"],
            accuracy=new_mastery_data["accuracy"],
            attempt_count=total,
            correct_count=correct_count,
            recent_performance=new_mastery_data["recent_performance"],
            confidence_level=new_mastery_data["confidence_level"],
            improvement_trend=0.0,
            last_assessed=datetime.utcnow(),
            history=[{"date": datetime.utcnow().isoformat(), "score": mastery_after}],
        )
        db.add(new_rec)
    
    # Update session
    session.questions_attempted = total
    session.questions_correct = correct_count
    session.session_score = round(session_score, 1)
    session.completed_at = datetime.utcnow()
    
    # Award XP & Record Progress Point
    xp_earned = correct_count * 8 + (30 if session_score >= 70 else 0)
    student.total_xp = (student.total_xp or 0) + xp_earned
    
    all_tm = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.student_id == student.id
    ).all()
    overall_m = (sum(m.mastery_score for m in all_tm) / len(all_tm)) if all_tm else 0.0
    
    pr = models.ProgressRecord(
        student_id=student.id,
        subject_id=topic.subject_id if topic else 1,
        date=datetime.utcnow(),
        overall_mastery=round(overall_m, 1),
        topics_mastered=len([m for m in all_tm if m.mastery_score >= 80]),
        assessment_accuracy=round(session_score, 1),
        xp_earned=xp_earned,
    )
    db.add(pr)
    
    db.commit()
    
    return {
        "session_id": session.id,
        "topic_name": topic.name,
        "questions_attempted": total,
        "questions_correct": correct_count,
        "session_score": round(session_score, 1),
        "mastery_before": round(mastery_before, 1),
        "mastery_after": round(mastery_after, 1),
        "mastery_delta": round(mastery_after - mastery_before, 1),
        "xp_earned": xp_earned,
        "message": _practice_message(session_score, mastery_after - mastery_before),
    }


def _practice_message(score: float, delta: float) -> str:
    if delta > 10:
        return f"🚀 Excellent! Your mastery improved by {delta:.1f} points. Keep this momentum!"
    elif delta > 0:
        return f"📈 Good progress! Mastery improved by {delta:.1f} points. Practice more to accelerate!"
    elif score >= 70:
        return "✅ Well done! Your mastery is holding steady. Try harder difficulty to push further."
    else:
        return "💪 Keep practicing! Review the explanations and try again."
