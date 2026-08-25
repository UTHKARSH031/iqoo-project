"""
LearnLens AI - Mastery Engine
Explainable rule-based mastery calculation system.
Computes topic-level mastery scores from assessment data.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class MasteryEngine:
    """
    Explainable mastery scoring engine.
    
    Mastery Score (0-100) is computed using weighted factors:
    - Base accuracy (40%)
    - Difficulty-adjusted performance (25%)
    - Recent performance trend (20%)
    - Attempt confidence (15%)
    
    Mastery Levels:
    - 0-39:   Needs Attention
    - 40-59:  Developing
    - 60-79:  Proficient
    - 80-100: Mastered
    """
    
    MASTERY_WEIGHTS = {
        "base_accuracy": 0.40,
        "difficulty_adjusted": 0.25,
        "recent_performance": 0.20,
        "confidence": 0.15,
    }
    
    MASTERY_LEVELS = [
        (80, "mastered"),
        (60, "proficient"),
        (40, "developing"),
        (0, "needs_attention"),
    ]
    
    DIFFICULTY_MULTIPLIERS = {
        "easy": 0.7,
        "medium": 1.0,
        "hard": 1.4,
    }
    
    def classify_mastery_level(self, score: float) -> str:
        for threshold, level in self.MASTERY_LEVELS:
            if score >= threshold:
                return level
        return "needs_attention"
    
    def calculate_difficulty_adjusted_score(
        self, 
        answers: List[Dict[str, Any]]
    ) -> float:
        """
        Compute accuracy weighted by question difficulty.
        Harder questions contribute more when answered correctly.
        """
        if not answers:
            return 0.0
        
        weighted_correct = 0.0
        total_weight = 0.0
        
        for ans in answers:
            difficulty = ans.get("difficulty", "medium")
            multiplier = self.DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
            total_weight += multiplier
            if ans.get("is_correct", False):
                weighted_correct += multiplier
        
        return (weighted_correct / total_weight * 100) if total_weight > 0 else 0.0
    
    def calculate_recent_performance(
        self, 
        answers: List[Dict[str, Any]], 
        window: int = 5
    ) -> float:
        """Calculate accuracy on the last N questions."""
        recent = answers[-window:] if len(answers) >= window else answers
        if not recent:
            return 0.0
        correct = sum(1 for a in recent if a.get("is_correct", False))
        return (correct / len(recent)) * 100
    
    def calculate_confidence_level(
        self, 
        attempt_count: int, 
        accuracy: float
    ) -> float:
        """
        Confidence = how reliable the mastery score is.
        Low attempts → low confidence even with high accuracy.
        """
        if attempt_count == 0:
            return 0.0
        # Log-based confidence scaling
        import math
        confidence_from_attempts = min(100, math.log(attempt_count + 1) / math.log(21) * 100)
        # Mix confidence with accuracy
        return (confidence_from_attempts * 0.6 + accuracy * 0.4)
    
    def compute_mastery(
        self,
        topic_id: int,
        all_answers: List[Dict[str, Any]],
        existing_mastery: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compute full mastery data for a topic.
        
        Returns:
            mastery_score: 0-100
            mastery_level: string
            accuracy: base accuracy
            difficulty_adjusted: weighted accuracy
            recent_performance: last 5 accuracy
            confidence_level: reliability of the score
            improvement_trend: positive = getting better
        """
        if not all_answers:
            if existing_mastery:
                return existing_mastery
            return {
                "mastery_score": 0.0,
                "mastery_level": "needs_attention",
                "accuracy": 0.0,
                "attempt_count": 0,
                "correct_count": 0,
                "recent_performance": 0.0,
                "confidence_level": 0.0,
                "improvement_trend": 0.0,
            }
        
        total = len(all_answers)
        correct = sum(1 for a in all_answers if a.get("is_correct", False))
        accuracy = (correct / total * 100) if total > 0 else 0.0
        
        difficulty_adjusted = self.calculate_difficulty_adjusted_score(all_answers)
        recent_performance = self.calculate_recent_performance(all_answers)
        confidence = self.calculate_confidence_level(total, accuracy)
        
        # Compute weighted mastery score
        mastery_score = (
            accuracy * self.MASTERY_WEIGHTS["base_accuracy"] +
            difficulty_adjusted * self.MASTERY_WEIGHTS["difficulty_adjusted"] +
            recent_performance * self.MASTERY_WEIGHTS["recent_performance"] +
            confidence * self.MASTERY_WEIGHTS["confidence"]
        )
        
        # Compute improvement trend
        improvement_trend = 0.0
        if existing_mastery and existing_mastery.get("mastery_score", 0) > 0:
            old_score = existing_mastery["mastery_score"]
            # Weighted blend: 60% new data, 40% old
            mastery_score = mastery_score * 0.6 + old_score * 0.4
            improvement_trend = mastery_score - old_score
        
        return {
            "mastery_score": round(min(100, max(0, mastery_score)), 1),
            "mastery_level": self.classify_mastery_level(mastery_score),
            "accuracy": round(accuracy, 1),
            "attempt_count": total,
            "correct_count": correct,
            "recent_performance": round(recent_performance, 1),
            "confidence_level": round(confidence, 1),
            "improvement_trend": round(improvement_trend, 1),
        }
    
    def compute_overall_mastery(self, topic_mastery_list: List[Dict[str, Any]]) -> float:
        """Compute weighted overall mastery across all topics."""
        if not topic_mastery_list:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for tm in topic_mastery_list:
            # Weight by topic importance and confidence
            weight = tm.get("difficulty_weight", 1.0) * (
                0.3 + 0.7 * tm.get("confidence_level", 50) / 100
            )
            weighted_sum += tm.get("mastery_score", 0) * weight
            total_weight += weight
        
        return round(weighted_sum / total_weight, 1) if total_weight > 0 else 0.0


mastery_engine = MasteryEngine()
