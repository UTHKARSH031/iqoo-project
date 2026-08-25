"""
LearnLens AI - Database Seed Script
Creates demo data for hackathon demonstration.
All data is deterministic and consistent across resets.

Demo Credentials:
  Teacher: teacher@learnlens.ai / demo123
  Student (Alice): alice@learnlens.ai / demo123
  Student (Bob):   bob@learnlens.ai / demo123
  Student (Carol): carol@learnlens.ai / demo123
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from models import Base
from auth import get_password_hash
import json


def seed_database():
    print("Resetting and seeding clean LearnLens AI database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # ─── Subjects ──────────────────────────────────────────────────────────
        subjects_data = [
            {
                "name": "Data Structures & Algorithms",
                "code": "DSA",
                "description": "Core computer science concepts including arrays, trees, graphs, and algorithm design",
                "icon": "🧩",
                "color": "#6366f1",
            },
            {
                "name": "Machine Learning",
                "code": "ML",
                "description": "Foundations of machine learning, supervised/unsupervised learning, and model evaluation",
                "icon": "🤖",
                "color": "#f59e0b",
            },
            {
                "name": "Mathematics",
                "code": "MATH",
                "description": "Calculus, Linear Algebra, and Discrete Mathematics for computing",
                "icon": "📐",
                "color": "#10b981",
            },
        ]
        
        subjects = {}
        for sd in subjects_data:
            s = models.Subject(**sd)
            db.add(s)
            db.flush()
            subjects[sd["code"]] = s
        
        # ─── Topics ────────────────────────────────────────────────────────────
        topics_data = {
            "DSA": [
                {"name": "Arrays", "code": "arrays", "description": "Array operations, searching, sorting algorithms", "difficulty_weight": 1.0, "order_index": 1},
                {"name": "Linked Lists", "code": "linked_lists", "description": "Singly/doubly linked lists, cycle detection, reversal", "difficulty_weight": 1.2, "order_index": 2},
                {"name": "Stacks", "code": "stacks", "description": "LIFO data structure, call stack, expression evaluation", "difficulty_weight": 1.1, "order_index": 3},
                {"name": "Queues", "code": "queues", "description": "FIFO data structure, BFS, priority queues", "difficulty_weight": 1.1, "order_index": 4},
                {"name": "Trees", "code": "trees", "description": "Binary trees, BST, AVL, tree traversals", "difficulty_weight": 1.5, "order_index": 5},
                {"name": "Graphs", "code": "graphs", "description": "Graph representations, BFS, DFS, shortest paths", "difficulty_weight": 1.8, "order_index": 6},
                {"name": "Dynamic Programming", "code": "dynamic_programming", "description": "Memoization, tabulation, classic DP problems", "difficulty_weight": 2.0, "order_index": 7},
                {"name": "Sorting Algorithms", "code": "sorting_algorithms", "description": "Quick sort, merge sort, bubble sort, selection sort", "difficulty_weight": 1.4, "order_index": 8},
                {"name": "Heaps & Priority Queues", "code": "heaps", "description": "Min-heap, max-heap, heapify, priority queue scheduling", "difficulty_weight": 1.5, "order_index": 9},
                {"name": "Recursion & Backtracking", "code": "backtracking", "description": "N-Queens, Sudoku solver, subset generation, permutations", "difficulty_weight": 1.7, "order_index": 10},
                {"name": "System Architecture", "code": "system_design", "description": "Load balancing, caching, database sharding, microservices", "difficulty_weight": 1.9, "order_index": 11},
                {"name": "Bit Manipulation", "code": "bit_manipulation", "description": "Bitwise operations, mask manipulation, binary arithmetic", "difficulty_weight": 1.3, "order_index": 12},
            ],
            "ML": [
                {"name": "Supervised Learning", "code": "supervised_learning", "description": "Classification, regression, model training", "difficulty_weight": 1.2, "order_index": 1},
                {"name": "Unsupervised Learning", "code": "unsupervised_learning", "description": "Clustering, dimensionality reduction", "difficulty_weight": 1.5, "order_index": 2},
                {"name": "Model Evaluation", "code": "model_evaluation", "description": "Metrics, cross-validation, overfitting", "difficulty_weight": 1.3, "order_index": 3},
                {"name": "Neural Networks", "code": "neural_networks", "description": "Perceptrons, backpropagation, deep learning", "difficulty_weight": 2.0, "order_index": 4},
            ],
            "MATH": [
                {"name": "Limits & Continuity", "code": "limits", "description": "Limits, continuity, L'Hôpital's rule", "difficulty_weight": 1.0, "order_index": 1},
                {"name": "Derivatives", "code": "derivatives", "description": "Differentiation rules, chain rule, applications", "difficulty_weight": 1.2, "order_index": 2},
                {"name": "Integrals", "code": "integrals", "description": "Integration techniques, applications", "difficulty_weight": 1.4, "order_index": 3},
                {"name": "Linear Algebra", "code": "linear_algebra", "description": "Vectors, matrices, eigenvalues", "difficulty_weight": 1.6, "order_index": 4},
            ],
        }
        
        topics = {}
        for subject_code, topic_list in topics_data.items():
            subject = subjects[subject_code]
            for td in topic_list:
                t = models.Topic(subject_id=subject.id, **td)
                db.add(t)
                db.flush()
                topics[td["code"]] = t
        
        db.commit()
        print("✅ Database reset successfully with subjects and topics! Zero pre-seeded users.")
        print("\nNote: Create your teacher and student accounts via the Register tab on the Login page.")
    
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
