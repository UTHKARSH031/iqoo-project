"""
LearnLens AI - Evaluation Router
GET /evaluation/metrics
GET /evaluation/confusion-matrix
GET /evaluation/recommendation-accuracy

Computes real metrics on the mastery classification and recommendation engine
using the seeded demo dataset as evaluation data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from ai.mastery_engine import mastery_engine
from ai.recommendation_engine import recommendation_engine

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/metrics")
def get_evaluation_metrics(db: Session = Depends(get_db)):
    """
    Compute evaluation metrics for the mastery classification engine.
    
    Method:
    - Take all StudentTopicMastery records as ground truth
    - Apply the mastery engine classification
    - Compare classified level vs actual stored level
    - Compute Accuracy, Precision, Recall, F1 per class
    """
    mastery_records = db.query(models.StudentTopicMastery).all()
    
    if not mastery_records:
        return {"error": "No mastery data available. Run seed first."}
    
    # Labels
    label_map = {
        "needs_attention": 0,
        "developing": 1,
        "proficient": 2,
        "mastered": 3,
    }
    label_names = ["Needs Attention", "Developing", "Proficient", "Mastered"]
    
    y_true = []
    y_pred = []
    
    for record in mastery_records:
        # Ground truth: stored mastery level (from seeded data)
        true_label = label_map.get(record.mastery_level, 0)
        
        # Prediction: what the engine would classify this score as
        predicted_level = mastery_engine.classify_mastery_level(record.mastery_score)
        pred_label = label_map.get(predicted_level, 0)
        
        y_true.append(true_label)
        y_pred.append(pred_label)
    
    # Compute confusion matrix
    n_classes = 4
    confusion = [[0] * n_classes for _ in range(n_classes)]
    for true, pred in zip(y_true, y_pred):
        confusion[true][pred] += 1
    
    # Compute per-class metrics
    class_metrics = []
    for c in range(n_classes):
        tp = confusion[c][c]
        fp = sum(confusion[r][c] for r in range(n_classes) if r != c)
        fn = sum(confusion[c][p] for p in range(n_classes) if p != c)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        class_metrics.append({
            "class": label_names[c],
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "support": sum(1 for y in y_true if y == c),
        })
    
    # Overall accuracy
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    accuracy = correct / len(y_true) if y_true else 0
    
    # Macro averages
    macro_precision = sum(m["precision"] for m in class_metrics) / n_classes
    macro_recall = sum(m["recall"] for m in class_metrics) / n_classes
    macro_f1 = sum(m["f1_score"] for m in class_metrics) / n_classes
    
    return {
        "accuracy": round(accuracy, 4),
        "macro_precision": round(macro_precision, 4),
        "macro_recall": round(macro_recall, 4),
        "macro_f1": round(macro_f1, 4),
        "total_samples": len(y_true),
        "class_metrics": class_metrics,
        "confusion_matrix": confusion,
        "label_names": label_names,
        "methodology": {
            "engine_type": "Rule-based Mastery Classification",
            "thresholds": {"mastered": 80, "proficient": 60, "developing": 40, "needs_attention": 0},
            "evaluation_set": "Seeded demo dataset (student mastery records)",
            "note": "Metrics evaluate the consistency of the rule-based classifier against seeded ground truth labels. High accuracy is expected by design — this validates the rule engine's stability."
        }
    }


@router.get("/confusion-matrix")
def get_confusion_matrix(db: Session = Depends(get_db)):
    """Get confusion matrix for mastery classification."""
    mastery_records = db.query(models.StudentTopicMastery).all()
    
    label_map = {"needs_attention": 0, "developing": 1, "proficient": 2, "mastered": 3}
    label_names = ["Needs Attention", "Developing", "Proficient", "Mastered"]
    
    n_classes = 4
    confusion = [[0] * n_classes for _ in range(n_classes)]
    
    for record in mastery_records:
        true_label = label_map.get(record.mastery_level, 0)
        predicted_level = mastery_engine.classify_mastery_level(record.mastery_score)
        pred_label = label_map.get(predicted_level, 0)
        confusion[true_label][pred_label] += 1
    
    return {
        "matrix": confusion,
        "labels": label_names,
    }


@router.get("/recommendation-accuracy")
def get_recommendation_accuracy(db: Session = Depends(get_db)):
    """
    Evaluate recommendation engine accuracy.
    Check: Do the engine's top recommendations match the lowest-mastery topics?
    A good recommendation should prioritize topics with low mastery.
    """
    students = db.query(models.StudentProfile).all()
    
    correct_recommendations = 0
    total_evaluated = 0
    
    per_student_results = []
    
    for student in students:
        mastery_records = db.query(models.StudentTopicMastery).filter(
            models.StudentTopicMastery.student_id == student.id
        ).all()
        
        if len(mastery_records) < 2:
            continue
        
        # Build topic mastery data
        topic_mastery_list = []
        for mr in mastery_records:
            topic = db.query(models.Topic).filter(models.Topic.id == mr.topic_id).first()
            if not topic:
                continue
            topic_mastery_list.append({
                "topic_id": topic.id,
                "topic_name": topic.name,
                "subject_name": "",
                "difficulty_weight": topic.difficulty_weight,
                "mastery_score": mr.mastery_score,
                "mastery_level": mr.mastery_level,
                "accuracy": mr.accuracy,
                "attempt_count": mr.attempt_count,
                "recent_performance": mr.recent_performance,
                "improvement_trend": mr.improvement_trend or 0.0,
                "confidence_level": mr.confidence_level,
            })
        
        # Get recommendations
        recommendations = recommendation_engine.generate_recommendations(topic_mastery_list, limit=3)
        
        if not recommendations:
            continue
        
        # Ground truth: topics that truly need attention (mastery < 50)
        true_weak = set(t["topic_id"] for t in topic_mastery_list if t["mastery_score"] < 50)
        
        # Check how many of top 3 recommendations are genuinely weak topics
        rec_topic_ids = set(r["topic_id"] for r in recommendations)
        
        true_positives = len(rec_topic_ids & true_weak)
        precision = true_positives / len(rec_topic_ids) if rec_topic_ids else 0
        recall = true_positives / len(true_weak) if true_weak else 1.0
        
        user = db.query(models.User).filter(models.User.id == student.user_id).first()
        per_student_results.append({
            "student_name": user.full_name if user else f"Student {student.id}",
            "weak_topics_count": len(true_weak),
            "recommendations_count": len(rec_topic_ids),
            "correctly_recommended": true_positives,
            "precision": round(precision, 2),
            "recall": round(recall, 2),
        })
        
        correct_recommendations += true_positives
        total_evaluated += len(rec_topic_ids)
    
    overall_precision = (
        sum(r["precision"] for r in per_student_results) / len(per_student_results)
        if per_student_results else 0
    )
    overall_recall = (
        sum(r["recall"] for r in per_student_results) / len(per_student_results)
        if per_student_results else 0
    )
    f1 = (
        2 * overall_precision * overall_recall / (overall_precision + overall_recall)
        if (overall_precision + overall_recall) > 0 else 0
    )
    
    return {
        "overall_precision": round(overall_precision, 4),
        "overall_recall": round(overall_recall, 4),
        "f1_score": round(f1, 4),
        "students_evaluated": len(per_student_results),
        "per_student_results": per_student_results,
        "methodology": "Precision: fraction of recommended topics that are genuinely weak. Recall: fraction of weak topics that were recommended."
    }
