"""
LearnLens AI - Assessment Router
POST /assessment/start
POST /assessment/submit
GET  /assessment/results/{assessment_id}
GET  /assessment/history
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from database import get_db
import models
import schemas
from auth import decode_access_token
from ai.question_generator import question_generator
from ai.mastery_engine import mastery_engine
from ai.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/assessment", tags=["Assessment"])


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


def _get_or_create_question(db: Session, q_data: dict, topic_id: int) -> models.Question:
    """Get existing question or create it if it doesn't exist."""
    q_id = q_data.get("id")
    if q_id:
        existing = db.query(models.Question).filter(models.Question.id == q_id).first()
        if existing:
            return existing
    
    question = models.Question(
        topic_id=topic_id,
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
    return question


@router.post("/start")
def start_assessment(
    request: schemas.AssessmentStartRequest,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Start a new assessment and return questions."""
    subject = db.query(models.Subject).filter(models.Subject.id == request.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Get topics for this subject
    topics = db.query(models.Topic).filter(
        models.Topic.subject_id == request.subject_id
    ).order_by(models.Topic.order_index).all()
    
    if not topics:
        raise HTTPException(status_code=404, detail="No topics found for subject")
    
    # Generate questions
    all_questions = []
    questions_per_topic = max(1, request.num_questions // len(topics))
    extra = request.num_questions - (questions_per_topic * len(topics))
    
    topic_codes = [t.code for t in topics]
    
    if request.assessment_type == "diagnostic":
        # Balanced diagnostic: sample from all topics
        raw_questions = question_generator.generate_diagnostic_questions(
            topic_codes, questions_per_topic=questions_per_topic
        )
    else:
        # For practice/reassessment: get student's mastery to adapt difficulty
        raw_questions = []
        for topic in topics:
            mastery_rec = db.query(models.StudentTopicMastery).filter(
                models.StudentTopicMastery.student_id == student.id,
                models.StudentTopicMastery.topic_id == topic.id
            ).first()
            mastery_score = mastery_rec.mastery_score if mastery_rec else 50.0
            
            qs = question_generator.get_questions_for_topic(
                topic.code,
                num_questions=questions_per_topic,
                student_mastery=mastery_score
            )
            raw_questions.extend(qs)
    
    # Limit to requested number
    raw_questions = raw_questions[:request.num_questions]
    
    # Create assessment record
    assessment = models.Assessment(
        student_id=student.id,
        subject_id=request.subject_id,
        assessment_type=request.assessment_type,
        status="in_progress",
        total_questions=len(raw_questions),
        started_at=datetime.utcnow(),
    )
    db.add(assessment)
    db.flush()
    
    # Build question objects and response
    questions_out = []
    for q_data in raw_questions:
        # Find topic
        topic = next((t for t in topics if t.code == q_data.get("topic_code")), topics[0])
        question = _get_or_create_question(db, q_data, topic.id)
        
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
        "assessment_id": assessment.id,
        "questions": questions_out,
        "subject_name": subject.name,
        "assessment_type": request.assessment_type,
        "total_questions": len(questions_out),
    }


@router.post("/submit")
def submit_assessment(
    request: schemas.AssessmentSubmitRequest,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit assessment answers and get results with mastery update."""
    assessment = db.query(models.Assessment).filter(
        models.Assessment.id == request.assessment_id,
        models.Assessment.student_id == student.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    if assessment.status == "completed":
        raise HTTPException(status_code=400, detail="Assessment already submitted")
    
    # Process answers
    correct_total = 0
    topic_answers: dict = {}  # topic_id -> list of {is_correct, difficulty}
    
    for ans in request.answers:
        question = db.query(models.Question).filter(
            models.Question.id == ans.question_id
        ).first()
        if not question:
            continue
        
        # Check correctness
        correct_answer = question.correct_answer
        student_answer = ans.student_answer
        
        is_correct = False
        if isinstance(correct_answer, list):
            if isinstance(student_answer, list):
                is_correct = set(correct_answer) == set(student_answer)
        else:
            is_correct = str(student_answer).strip().lower() == str(correct_answer).strip().lower()
        
        if is_correct:
            correct_total += 1
        
        # Store answer
        db_answer = models.AssessmentAnswer(
            assessment_id=assessment.id,
            question_id=question.id,
            student_answer=student_answer,
            is_correct=is_correct,
            time_taken_seconds=ans.time_taken_seconds,
        )
        db.add(db_answer)
        
        # Group by topic
        topic_id = question.topic_id
        if topic_id not in topic_answers:
            topic_answers[topic_id] = []
        topic_answers[topic_id].append({
            "is_correct": is_correct,
            "difficulty": question.difficulty,
        })
    
    # Calculate topic results and update mastery
    topic_results = []
    for topic_id, answers in topic_answers.items():
        topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
        
        # Get existing mastery
        existing_mastery_rec = db.query(models.StudentTopicMastery).filter(
            models.StudentTopicMastery.student_id == student.id,
            models.StudentTopicMastery.topic_id == topic_id
        ).first()
        
        existing_mastery_data = None
        mastery_before = 0.0
        if existing_mastery_rec:
            mastery_before = existing_mastery_rec.mastery_score
            existing_mastery_data = {
                "mastery_score": existing_mastery_rec.mastery_score,
                "accuracy": existing_mastery_rec.accuracy,
                "attempt_count": existing_mastery_rec.attempt_count,
                "correct_count": existing_mastery_rec.correct_count,
            }
        
        # Compute new mastery
        new_mastery_data = mastery_engine.compute_mastery(topic_id, answers, existing_mastery_data)
        mastery_after = new_mastery_data["mastery_score"]
        
        # Topic accuracy
        topic_correct = sum(1 for a in answers if a["is_correct"])
        topic_accuracy = (topic_correct / len(answers) * 100) if answers else 0
        
        # Update or create mastery record
        if existing_mastery_rec:
            existing_mastery_rec.mastery_score = mastery_after
            existing_mastery_rec.mastery_level = new_mastery_data["mastery_level"]
            existing_mastery_rec.accuracy = new_mastery_data["accuracy"]
            existing_mastery_rec.attempt_count = (existing_mastery_rec.attempt_count or 0) + len(answers)
            existing_mastery_rec.correct_count = (existing_mastery_rec.correct_count or 0) + topic_correct
            existing_mastery_rec.recent_performance = new_mastery_data["recent_performance"]
            existing_mastery_rec.confidence_level = new_mastery_data["confidence_level"]
            existing_mastery_rec.improvement_trend = new_mastery_data["improvement_trend"]
            existing_mastery_rec.last_assessed = datetime.utcnow()
            # Append to history
            history = existing_mastery_rec.history or []
            history.append({"date": datetime.utcnow().isoformat(), "score": mastery_after})
            existing_mastery_rec.history = history
        else:
            mastery_level = mastery_engine.classify_mastery_level(mastery_after)
            new_rec = models.StudentTopicMastery(
                student_id=student.id,
                topic_id=topic_id,
                mastery_score=mastery_after,
                mastery_level=mastery_level,
                accuracy=new_mastery_data["accuracy"],
                attempt_count=len(answers),
                correct_count=topic_correct,
                recent_performance=new_mastery_data["recent_performance"],
                confidence_level=new_mastery_data["confidence_level"],
                improvement_trend=0.0,
                last_assessed=datetime.utcnow(),
                history=[{"date": datetime.utcnow().isoformat(), "score": mastery_after}],
            )
            db.add(new_rec)
        
        topic_results.append({
            "topic_id": topic_id,
            "topic_name": topic.name if topic else "Unknown",
            "total_questions": len(answers),
            "correct_answers": topic_correct,
            "accuracy": round(topic_accuracy, 1),
            "mastery_before": round(mastery_before, 1),
            "mastery_after": round(mastery_after, 1),
            "mastery_delta": round(mastery_after - mastery_before, 1),
        })
    
    # Update assessment
    score_pct = (correct_total / len(request.answers) * 100) if request.answers else 0
    assessment.correct_answers = correct_total
    assessment.total_questions = len(request.answers)
    assessment.score_percentage = round(score_pct, 1)
    assessment.status = "completed"
    assessment.completed_at = datetime.utcnow()
    
    # Award XP & Record Progress Point
    xp_earned = correct_total * 10 + (50 if score_pct >= 70 else 0)
    student.total_xp = (student.total_xp or 0) + xp_earned
    student.current_streak = (student.current_streak or 0) + 1
    student.last_activity = datetime.utcnow()
    
    # Calculate current overall mastery across all topics
    all_tm = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.student_id == student.id
    ).all()
    overall_m = (sum(m.mastery_score for m in all_tm) / len(all_tm)) if all_tm else 0.0
    
    pr = models.ProgressRecord(
        student_id=student.id,
        subject_id=assessment.subject_id,
        date=datetime.utcnow(),
        overall_mastery=round(overall_m, 1),
        topics_mastered=len([m for m in all_tm if m.mastery_score >= 80]),
        assessment_accuracy=round(score_pct, 1),
        xp_earned=xp_earned,
    )
    db.add(pr)
    
    # Generate recommendations
    from routers.student import build_topic_mastery_list
    topic_mastery_list = build_topic_mastery_list(student, db)
    recommendations = recommendation_engine.generate_recommendations(topic_mastery_list, limit=3)
    
    db.commit()
    
    return {
        "assessment_id": assessment.id,
        "total_questions": len(request.answers),
        "correct_answers": correct_total,
        "score_percentage": round(score_pct, 1),
        "topic_results": topic_results,
        "xp_earned": xp_earned,
        "message": _generate_result_message(score_pct, correct_total, len(request.answers)),
        "recommendations": recommendations,
    }


def _generate_result_message(score_pct: float, correct: int, total: int) -> str:
    if score_pct >= 80:
        return f"Excellent work! You answered {correct}/{total} correctly. You're showing strong mastery!"
    elif score_pct >= 60:
        return f"Good effort! {correct}/{total} correct. Let's work on the weak areas to reach mastery."
    elif score_pct >= 40:
        return f"Keep going! {correct}/{total} correct. Practice the recommended topics to improve."
    else:
        return f"Don't worry — {correct}/{total} correct. Every assessment helps us personalize your path."


@router.get("/results/{assessment_id}")
def get_assessment_results(
    assessment_id: int,
    student: models.StudentProfile = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get results for a specific assessment."""
    assessment = db.query(models.Assessment).filter(
        models.Assessment.id == assessment_id,
        models.Assessment.student_id == student.id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    answers = db.query(models.AssessmentAnswer).filter(
        models.AssessmentAnswer.assessment_id == assessment_id
    ).all()
    
    answer_details = []
    for ans in answers:
        q = db.query(models.Question).filter(models.Question.id == ans.question_id).first()
        if q:
            topic = db.query(models.Topic).filter(models.Topic.id == q.topic_id).first()
            answer_details.append({
                "question_text": q.question_text,
                "student_answer": ans.student_answer,
                "correct_answer": q.correct_answer,
                "is_correct": ans.is_correct,
                "explanation": q.explanation,
                "topic_name": topic.name if topic else "Unknown",
                "difficulty": q.difficulty,
            })
    
    return {
        "assessment_id": assessment.id,
        "subject_id": assessment.subject_id,
        "assessment_type": assessment.assessment_type,
        "score_percentage": assessment.score_percentage,
        "correct_answers": assessment.correct_answers,
        "total_questions": assessment.total_questions,
        "completed_at": assessment.completed_at,
        "answers": answer_details,
    }
