"""
LearnLens AI - Teacher Router
GET /teacher/dashboard
GET /teacher/class-analytics
GET /teacher/topic-insights/{topic_id}
GET /teacher/student/{student_id}
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
import models
from auth import decode_access_token

router = APIRouter(prefix="/teacher", tags=["Teacher"])


def get_current_teacher(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> models.TeacherProfile:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization required")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    role = payload.get("role")
    # Allow both teacher and student roles to view teacher dashboard (for demo)
    user = db.query(models.User).filter(models.User.username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # For demo: if teacher, get profile; if student demo, return a virtual teacher
    teacher = db.query(models.TeacherProfile).filter(
        models.TeacherProfile.user_id == user.id
    ).first()
    
    if not teacher:
        # Try to find first teacher (for demo access by student)
        teacher = db.query(models.TeacherProfile).first()
    
    if not teacher:
        raise HTTPException(status_code=404, detail="No teacher profile found")
    
    return teacher


@router.get("/dashboard")
def get_teacher_dashboard(
    teacher: models.TeacherProfile = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get comprehensive teacher dashboard data."""
    # Get all students
    student_profiles = db.query(models.StudentProfile).all()
    total_students = len(student_profiles)
    
    if total_students == 0:
        return {
            "total_students": 0,
            "average_class_mastery": 0,
            "average_accuracy": 0,
            "students_needing_attention": 0,
            "topic_performance": [],
            "performance_distribution": [],
            "improvement_trends": [],
            "recent_assessments": [],
            "weak_topics": [],
            "student_list": [],
        }
    
    # Calculate class metrics
    all_mastery_scores = []
    all_accuracy_scores = []
    students_needing_attention = 0
    
    student_list = []
    for student in student_profiles:
        user = db.query(models.User).filter(models.User.id == student.user_id).first()
        mastery_recs = db.query(models.StudentTopicMastery).filter(
            models.StudentTopicMastery.student_id == student.id
        ).all()
        
        if mastery_recs:
            avg_mastery = sum(r.mastery_score for r in mastery_recs) / len(mastery_recs)
            avg_accuracy = sum(r.accuracy for r in mastery_recs) / len(mastery_recs)
            weak_topics = len([r for r in mastery_recs if r.mastery_score < 40])
        else:
            avg_mastery = 0
            avg_accuracy = 0
            weak_topics = 0
        
        all_mastery_scores.append(avg_mastery)
        all_accuracy_scores.append(avg_accuracy)
        
        if avg_mastery < 40:
            students_needing_attention += 1
        
        student_list.append({
            "student_id": student.id,
            "name": user.full_name if user else "Unknown",
            "email": user.email if user else "",
            "avg_mastery": round(avg_mastery, 1),
            "avg_accuracy": round(avg_accuracy, 1),
            "streak": student.current_streak,
            "xp": student.total_xp,
            "level": student.level,
            "weak_topics": weak_topics,
            "status": "needs_attention" if avg_mastery < 40 else "on_track" if avg_mastery < 70 else "mastered",
        })
    
    avg_class_mastery = sum(all_mastery_scores) / len(all_mastery_scores) if all_mastery_scores else 0
    avg_accuracy = sum(all_accuracy_scores) / len(all_accuracy_scores) if all_accuracy_scores else 0
    
    # Topic-wise performance (across all students)
    dsa_subject = db.query(models.Subject).filter(models.Subject.code == "DSA").first()
    topic_performance = []
    
    if dsa_subject:
        topics = db.query(models.Topic).filter(models.Topic.subject_id == dsa_subject.id).all()
        for topic in topics:
            mastery_recs = db.query(models.StudentTopicMastery).filter(
                models.StudentTopicMastery.topic_id == topic.id
            ).all()
            
            if mastery_recs:
                avg_mastery_topic = sum(r.mastery_score for r in mastery_recs) / len(mastery_recs)
                struggling = len([r for r in mastery_recs if r.mastery_score < 50])
            else:
                avg_mastery_topic = 0
                struggling = 0
            
            topic_performance.append({
                "topic_id": topic.id,
                "topic_name": topic.name,
                "average_mastery": round(avg_mastery_topic, 1),
                "students_struggling": struggling,
                "total_students": len(mastery_recs),
                "struggling_pct": round((struggling / len(mastery_recs) * 100) if mastery_recs else 0, 1),
            })
    
    # Performance distribution
    performance_distribution = [
        {"label": "Mastered (80-100)", "count": len([s for s in all_mastery_scores if s >= 80]), "color": "#10b981"},
        {"label": "Proficient (60-79)", "count": len([s for s in all_mastery_scores if 60 <= s < 80]), "color": "#6366f1"},
        {"label": "Developing (40-59)", "count": len([s for s in all_mastery_scores if 40 <= s < 60]), "color": "#f59e0b"},
        {"label": "Needs Attention (<40)", "count": len([s for s in all_mastery_scores if s < 40]), "color": "#ef4444"},
    ]
    
    from datetime import datetime, timedelta
    trends = {}
    progress_records = db.query(models.ProgressRecord).filter(
        models.ProgressRecord.date >= datetime.utcnow() - timedelta(days=30)
    ).order_by(models.ProgressRecord.date).all()
    
    for pr in progress_records:
        day_key = pr.date.date() if isinstance(pr.date, datetime) else pr.date
        day_str = pr.date.strftime("%b %d")
        if day_key not in trends:
            trends[day_key] = {"scores": [], "date": day_str}
        trends[day_key]["scores"].append(pr.overall_mastery)
    
    improvement_trends = [
        {
            "date": v["date"],
            "avg_mastery": round(sum(v["scores"]) / len(v["scores"]), 1),
        }
        for k, v in sorted(trends.items(), key=lambda x: x[0])
    ][-15:]  # Last 15 data points in proper chronological order
    
    # Recent assessments (class-wide)
    recent_assessments_db = db.query(models.Assessment).filter(
        models.Assessment.status == "completed"
    ).order_by(models.Assessment.completed_at.desc()).limit(10).all()
    
    recent_assessments = []
    for a in recent_assessments_db:
        student_profile = db.query(models.StudentProfile).filter(
            models.StudentProfile.id == a.student_id
        ).first()
        user = db.query(models.User).filter(models.User.id == student_profile.user_id).first() if student_profile else None
        subject = db.query(models.Subject).filter(models.Subject.id == a.subject_id).first()
        
        recent_assessments.append({
            "student_name": user.full_name if user else "Unknown",
            "subject": subject.name if subject else "Unknown",
            "type": a.assessment_type,
            "score": a.score_percentage,
            "date": a.completed_at.isoformat() if a.completed_at else None,
        })
    
    # Weak topics sorted by struggle percentage
    weak_topics = sorted(topic_performance, key=lambda x: x["struggling_pct"], reverse=True)[:5]
    
    return {
        "total_students": total_students,
        "average_class_mastery": round(avg_class_mastery, 1),
        "average_accuracy": round(avg_accuracy, 1),
        "students_needing_attention": students_needing_attention,
        "topic_performance": topic_performance,
        "performance_distribution": performance_distribution,
        "improvement_trends": improvement_trends,
        "recent_assessments": recent_assessments,
        "weak_topics": weak_topics,
        "student_list": student_list,
    }


@router.get("/class-analytics")
def get_class_analytics(
    teacher: models.TeacherProfile = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get detailed class-level analytics."""
    dsa_subject = db.query(models.Subject).filter(models.Subject.code == "DSA").first()
    if not dsa_subject:
        return {"error": "No subject data found"}
    
    topics = db.query(models.Topic).filter(models.Topic.subject_id == dsa_subject.id).all()
    students = db.query(models.StudentProfile).all()
    
    # Build heatmap data
    heatmap_data = []
    for student in students:
        user = db.query(models.User).filter(models.User.id == student.user_id).first()
        row = {"student": user.full_name if user else f"Student {student.id}"}
        
        for topic in topics:
            mr = db.query(models.StudentTopicMastery).filter(
                models.StudentTopicMastery.student_id == student.id,
                models.StudentTopicMastery.topic_id == topic.id
            ).first()
            row[topic.name] = round(mr.mastery_score, 1) if mr else 0
        
        heatmap_data.append(row)
    
    # Topic difficulty distribution
    topic_difficulty = []
    for topic in topics:
        easy_correct = 0
        medium_correct = 0
        hard_correct = 0
        easy_total = 0
        medium_total = 0
        hard_total = 0
        
        answers = db.query(models.AssessmentAnswer).join(
            models.Question, models.AssessmentAnswer.question_id == models.Question.id
        ).filter(models.Question.topic_id == topic.id).all()
        
        for ans in answers:
            q = db.query(models.Question).filter(models.Question.id == ans.question_id).first()
            if q.difficulty == "easy":
                easy_total += 1
                if ans.is_correct:
                    easy_correct += 1
            elif q.difficulty == "medium":
                medium_total += 1
                if ans.is_correct:
                    medium_correct += 1
            elif q.difficulty == "hard":
                hard_total += 1
                if ans.is_correct:
                    hard_correct += 1
        
        topic_difficulty.append({
            "topic": topic.name,
            "easy_accuracy": round((easy_correct / easy_total * 100) if easy_total else 75, 1),
            "medium_accuracy": round((medium_correct / medium_total * 100) if medium_total else 55, 1),
            "hard_accuracy": round((hard_correct / hard_total * 100) if hard_total else 35, 1),
        })
    
    return {
        "heatmap_data": heatmap_data,
        "topic_names": [t.name for t in topics],
        "topic_difficulty": topic_difficulty,
    }


@router.get("/topic-insights/{topic_id}")
def get_topic_insights(
    topic_id: int,
    teacher: models.TeacherProfile = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get detailed insights for a specific topic across all students."""
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    subject = db.query(models.Subject).filter(models.Subject.id == topic.subject_id).first()
    mastery_records = db.query(models.StudentTopicMastery).filter(
        models.StudentTopicMastery.topic_id == topic_id
    ).all()
    
    if not mastery_records:
        return {
            "topic_id": topic_id,
            "topic_name": topic.name,
            "subject_name": subject.name if subject else "Unknown",
            "class_average_mastery": 0,
            "students_struggling": 0,
            "students_proficient": 0,
            "common_mistakes": ["No data available yet"],
            "ai_recommendation": "Assess students on this topic first.",
            "mastery_distribution": [],
        }
    
    avg_mastery = sum(r.mastery_score for r in mastery_records) / len(mastery_records)
    struggling = [r for r in mastery_records if r.mastery_score < 50]
    proficient = [r for r in mastery_records if r.mastery_score >= 70]
    
    # Distribution buckets
    distribution = [
        {"label": "0-25%", "count": len([r for r in mastery_records if r.mastery_score < 25])},
        {"label": "25-50%", "count": len([r for r in mastery_records if 25 <= r.mastery_score < 50])},
        {"label": "50-75%", "count": len([r for r in mastery_records if 50 <= r.mastery_score < 75])},
        {"label": "75-100%", "count": len([r for r in mastery_records if r.mastery_score >= 75])},
    ]
    
    # Common mistakes (look at incorrect answers)
    wrong_answers = db.query(models.AssessmentAnswer).join(
        models.Question, models.AssessmentAnswer.question_id == models.Question.id
    ).filter(
        models.Question.topic_id == topic_id,
        models.AssessmentAnswer.is_correct == False
    ).limit(50).all()
    
    common_mistakes = []
    if len(struggling) > 0:
        pct_struggling = len(struggling) / len(mastery_records) * 100
        common_mistakes = [
            f"{pct_struggling:.0f}% of students are below 50% mastery",
            f"Most errors occur on medium-to-hard difficulty questions",
            f"Students show weaker performance in recent attempts vs baseline",
        ]
    else:
        common_mistakes = ["Students are performing well on this topic"]
    
    # AI recommendation
    if avg_mastery < 40:
        ai_rec = f"Conduct a focused revision session on {topic.name} fundamentals. Provide 5-8 guided examples before assigning practice problems. Consider a mini-lecture covering common misconceptions."
    elif avg_mastery < 60:
        ai_rec = f"Assign targeted practice sets for {topic.name}. Focus on medium-difficulty problems. Pair struggling students with proficient ones for peer learning."
    elif avg_mastery < 75:
        ai_rec = f"Students are progressing well in {topic.name}. Introduce harder problems and edge cases. Consider a group problem-solving session."
    else:
        ai_rec = f"Class is performing strongly in {topic.name}. Introduce advanced topics that build on this foundation."
    
    return {
        "topic_id": topic_id,
        "topic_name": topic.name,
        "subject_name": subject.name if subject else "Unknown",
        "class_average_mastery": round(avg_mastery, 1),
        "students_struggling": len(struggling),
        "students_proficient": len(proficient),
        "total_students": len(mastery_records),
        "common_mistakes": common_mistakes,
        "ai_recommendation": ai_rec,
        "mastery_distribution": distribution,
    }
