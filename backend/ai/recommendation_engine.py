"""
LearnLens AI - Recommendation Engine
Priority-based adaptive learning recommendation system.
Explains WHY each recommendation is generated.
"""
from typing import List, Dict, Any, Optional


class RecommendationEngine:
    """
    Adaptive recommendation engine that determines what the student
    should learn next, with explainability.
    
    Priority Score factors:
    - Mastery gap (how far below mastered = 80)     : weight 0.35
    - Recent performance drop                        : weight 0.25
    - Topic importance (difficulty_weight)           : weight 0.20
    - Improvement trend (negative = priority boost)  : weight 0.20
    """
    
    WEIGHTS = {
        "mastery_gap": 0.35,
        "recent_struggle": 0.25,
        "topic_importance": 0.20,
        "decline_penalty": 0.20,
    }
    
    def compute_priority(self, mastery_data: Dict[str, Any]) -> float:
        """
        Higher priority score = needs attention sooner.
        Score is normalized 0-100.
        """
        mastery_score = mastery_data.get("mastery_score", 0.0)
        recent_performance = mastery_data.get("recent_performance", 0.0)
        topic_importance = mastery_data.get("difficulty_weight", 1.0)
        improvement_trend = mastery_data.get("improvement_trend", 0.0)
        attempt_count = mastery_data.get("attempt_count", 0)
        
        # Mastery gap: distance from 'mastered' threshold (80)
        mastery_gap = max(0, 80 - mastery_score)  # 0-80 range
        mastery_gap_score = (mastery_gap / 80) * 100
        
        # Recent struggle: lower recent performance = higher priority
        recent_struggle_score = max(0, 100 - recent_performance)
        
        # Topic importance normalized to 0-100
        importance_score = min(100, topic_importance * 50)
        
        # Decline penalty: if trend is negative, boost priority
        decline_score = min(100, max(0, -improvement_trend * 3 + 50))
        
        # If never attempted, moderate priority (needs baseline)
        if attempt_count == 0:
            mastery_gap_score = 60
            recent_struggle_score = 60
        
        priority = (
            mastery_gap_score * self.WEIGHTS["mastery_gap"] +
            recent_struggle_score * self.WEIGHTS["recent_struggle"] +
            importance_score * self.WEIGHTS["topic_importance"] +
            decline_score * self.WEIGHTS["decline_penalty"]
        )
        
        return round(priority, 2)
    
    def generate_reason(self, mastery_data: Dict[str, Any]) -> str:
        """Generate human-readable explanation for the recommendation."""
        topic_name = mastery_data.get("topic_name", "this topic")
        mastery_score = mastery_data.get("mastery_score", 0.0)
        recent_performance = mastery_data.get("recent_performance", 0.0)
        improvement_trend = mastery_data.get("improvement_trend", 0.0)
        attempt_count = mastery_data.get("attempt_count", 0)
        mastery_level = mastery_data.get("mastery_level", "needs_attention")
        
        reasons = []
        
        if attempt_count == 0:
            return f"{topic_name} has not been assessed yet. Starting here builds your foundation."
        
        if mastery_score < 40:
            reasons.append(f"your current mastery is only {mastery_score:.0f}%")
        elif mastery_score < 60:
            reasons.append(f"you are still developing in this topic (mastery: {mastery_score:.0f}%)")
        elif mastery_score < 80:
            reasons.append(f"you are proficient but not yet mastered ({mastery_score:.0f}%)")
        
        if recent_performance < 50:
            reasons.append(f"you answered only {recent_performance:.0f}% correctly in recent attempts")
        elif recent_performance < mastery_score - 10:
            reasons.append("your recent performance has dipped below your overall level")
        
        if improvement_trend < -5:
            reasons.append(f"your mastery has declined by {abs(improvement_trend):.0f} points recently")
        
        if not reasons:
            reasons.append(f"maintaining consistent practice prevents skill degradation")
        
        reason_text = " and ".join(reasons[:2])
        return f"{topic_name} is recommended because {reason_text}."
    
    def determine_action(self, mastery_score: float) -> str:
        """Recommend the type of learning action."""
        if mastery_score < 40:
            return "study"      # learn the concept first
        elif mastery_score < 60:
            return "practice"   # needs more practice
        elif mastery_score < 80:
            return "review"     # targeted review
        else:
            return "maintain"   # keep skills sharp
    
    def determine_urgency(self, priority_score: float) -> str:
        if priority_score >= 70:
            return "high"
        elif priority_score >= 45:
            return "medium"
        else:
            return "low"
    
    def generate_recommendations(
        self,
        topic_mastery_list: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized learning recommendations.
        
        Args:
            topic_mastery_list: list of topic mastery dicts with mastery data
            limit: max recommendations to return
            
        Returns:
            Sorted list of recommendation dicts with priority and explanation
        """
        recommendations = []
        
        for tm in topic_mastery_list:
            # Don't recommend already mastered topics as high priority
            mastery_score = tm.get("mastery_score", 0.0)
            
            priority = self.compute_priority(tm)
            reason = self.generate_reason(tm)
            action = self.determine_action(mastery_score)
            urgency = self.determine_urgency(priority)
            
            recommendations.append({
                "topic_id": tm["topic_id"],
                "topic_name": tm["topic_name"],
                "subject_name": tm.get("subject_name", ""),
                "priority_score": priority,
                "reason": reason,
                "recommended_action": action,
                "mastery_score": mastery_score,
                "mastery_level": tm.get("mastery_level", "needs_attention"),
                "urgency": urgency,
            })
        
        # Sort by priority descending
        recommendations.sort(key=lambda x: x["priority_score"], reverse=True)
        return recommendations[:limit]
    
    def generate_ai_insights(
        self,
        topic_mastery_list: List[Dict[str, Any]],
        overall_mastery: float,
        assessment_accuracy: float
    ) -> List[Dict[str, Any]]:
        """Generate AI insight cards from real performance data."""
        insights = []
        
        if not topic_mastery_list:
            return insights
        
        # Find strongest topic
        attempted = [tm for tm in topic_mastery_list if tm.get("attempt_count", 0) > 0]
        if attempted:
            strongest = max(attempted, key=lambda x: x.get("mastery_score", 0))
            insights.append({
                "insight_type": "strength",
                "title": f"Strongest Topic: {strongest['topic_name']}",
                "description": f"Your strongest topic is {strongest['topic_name']} with {strongest.get('mastery_score', 0):.0f}% mastery. Keep it up!",
                "icon": "🏆",
                "priority": 1,
            })
            
            # Find weakest topic
            weakest = min(attempted, key=lambda x: x.get("mastery_score", 0))
            if weakest["topic_id"] != strongest["topic_id"]:
                insights.append({
                    "insight_type": "weakness",
                    "title": f"Needs Attention: {weakest['topic_name']}",
                    "description": f"{weakest['topic_name']} requires attention. Your accuracy dropped recently and mastery is at {weakest.get('mastery_score', 0):.0f}%.",
                    "icon": "⚠️",
                    "priority": 2,
                })
        
        # Check overall trend
        improving = [tm for tm in topic_mastery_list if tm.get("improvement_trend", 0) > 5]
        if improving:
            insights.append({
                "insight_type": "trend",
                "title": "Improvement Detected",
                "description": f"You have shown improvement in {len(improving)} topic(s) recently. Your study consistency is paying off!",
                "icon": "📈",
                "priority": 3,
            })
        
        # Practice difficulty suggestion
        if assessment_accuracy > 70:
            insights.append({
                "insight_type": "action",
                "title": "Ready for Higher Difficulty",
                "description": f"Your assessment accuracy is {assessment_accuracy:.0f}%. You are performing well — try hard-difficulty questions to accelerate mastery.",
                "icon": "🎯",
                "priority": 4,
            })
        else:
            insights.append({
                "insight_type": "action",
                "title": "Focus on Medium Difficulty",
                "description": "You improve faster when practicing medium-difficulty questions. Aim for consistency before tackling hard questions.",
                "icon": "💡",
                "priority": 4,
            })
        
        # Next action
        low_mastery = [tm for tm in topic_mastery_list if tm.get("mastery_score", 0) < 50 and tm.get("attempt_count", 0) > 0]
        if low_mastery:
            lowest = min(low_mastery, key=lambda x: x.get("mastery_score", 0))
            insights.append({
                "insight_type": "action",
                "title": "Recommended Next Action",
                "description": f"Complete the {lowest['topic_name']} adaptive practice set to boost your mastery from {lowest.get('mastery_score', 0):.0f}%.",
                "icon": "🚀",
                "priority": 5,
            })
        
        insights.sort(key=lambda x: x["priority"])
        return insights


recommendation_engine = RecommendationEngine()
