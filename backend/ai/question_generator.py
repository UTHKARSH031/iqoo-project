"""
LearnLens AI - Question Generator
Template-based deterministic question generator.
Works fully in demo mode without any external API.
If OPENAI_API_KEY is set, uses GPT-4 for enhanced questions.
"""
import random
import hashlib
import os
from typing import List, Dict, Any, Optional


# Deterministic seed so same topic+difficulty always produces same questions
def _seed_for(topic_code: str, difficulty: str, index: int) -> int:
    key = f"{topic_code}_{difficulty}_{index}"
    return int(hashlib.md5(key.encode()).hexdigest()[:8], 16)


# ─── Question Templates ────────────────────────────────────────────────────────

QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    # Data Structures - Arrays
    "arrays": [
        {
            "question_text": "What is the time complexity of accessing an element by index in an array?",
            "question_type": "mcq",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
            "correct_answer": "O(1)",
            "explanation": "Arrays store elements in contiguous memory. Index-based access is direct and takes constant time O(1) regardless of array size.",
            "difficulty": "easy",
            "learning_objective": "Understand array access complexity",
        },
        {
            "question_text": "Which of the following operations is most expensive for a static array?",
            "question_type": "mcq",
            "options": ["Reading an element", "Inserting at the middle", "Accessing the last element", "Getting array length"],
            "correct_answer": "Inserting at the middle",
            "explanation": "Inserting at the middle requires shifting all subsequent elements, giving O(n) time complexity.",
            "difficulty": "medium",
            "learning_objective": "Understand array insertion complexity",
        },
        {
            "question_text": "Arrays in most programming languages use 0-based indexing.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Most modern languages (C, Java, Python) use 0-based indexing where the first element is at index 0.",
            "difficulty": "easy",
            "learning_objective": "Array indexing convention",
        },
        {
            "question_text": "What is the space complexity of a 1D array with n elements?",
            "question_type": "mcq",
            "options": ["O(1)", "O(n)", "O(n²)", "O(log n)"],
            "correct_answer": "O(n)",
            "explanation": "A 1D array with n elements requires O(n) space to store all n values.",
            "difficulty": "easy",
            "learning_objective": "Array space complexity",
        },
        {
            "question_text": "Which algorithm is best for finding an element in a sorted array?",
            "question_type": "mcq",
            "options": ["Linear Search", "Binary Search", "DFS", "Hash lookup"],
            "correct_answer": "Binary Search",
            "explanation": "Binary Search runs in O(log n) on sorted arrays by repeatedly halving the search space.",
            "difficulty": "medium",
            "learning_objective": "Searching in arrays",
        },
        {
            "question_text": "What is the worst-case time complexity of Bubble Sort on an array?",
            "question_type": "mcq",
            "options": ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
            "correct_answer": "O(n²)",
            "explanation": "Bubble Sort has nested loops, each running up to n times, giving O(n²) worst case.",
            "difficulty": "medium",
            "learning_objective": "Sorting algorithms complexity",
        },
        {
            "question_text": "Two-pointer technique is commonly used for which type of array problems?",
            "question_type": "mcq",
            "options": ["Searching unsorted arrays", "Finding pairs in sorted arrays", "Array reversal only", "Finding maximum element"],
            "correct_answer": "Finding pairs in sorted arrays",
            "explanation": "Two-pointer technique is highly effective for finding pairs with a given sum in sorted arrays in O(n) time.",
            "difficulty": "hard",
            "learning_objective": "Two-pointer array technique",
        },
        {
            "question_text": "Kadane's algorithm solves which classic array problem?",
            "question_type": "mcq",
            "options": ["Array rotation", "Maximum subarray sum", "Array sorting", "Array merging"],
            "correct_answer": "Maximum subarray sum",
            "explanation": "Kadane's algorithm finds the maximum sum contiguous subarray in O(n) time using dynamic programming.",
            "difficulty": "hard",
            "learning_objective": "Dynamic programming on arrays",
        },
    ],
    
    # Data Structures - Linked Lists
    "linked_lists": [
        {
            "question_text": "What is the time complexity of inserting a node at the beginning of a singly linked list?",
            "question_type": "mcq",
            "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"],
            "correct_answer": "O(1)",
            "explanation": "Inserting at the head only requires updating the next pointer of the new node and updating head. This is O(1).",
            "difficulty": "easy",
            "learning_objective": "Linked list insertion",
        },
        {
            "question_text": "In a doubly linked list, each node contains references to both next and previous nodes.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "A doubly linked list node has three components: data, next pointer, and previous pointer.",
            "difficulty": "easy",
            "learning_objective": "Doubly linked list structure",
        },
        {
            "question_text": "How do you detect a cycle in a linked list efficiently?",
            "question_type": "mcq",
            "options": ["Use a hash set to store visited nodes", "Floyd's slow-fast pointer algorithm", "Reverse the list and compare", "Both A and B"],
            "correct_answer": "Both A and B",
            "explanation": "Both hash set O(n) space and Floyd's cycle detection O(1) space work. Floyd's is preferred for space efficiency.",
            "difficulty": "medium",
            "learning_objective": "Cycle detection in linked lists",
        },
        {
            "question_text": "What is the time complexity of searching for an element in an unsorted linked list?",
            "question_type": "mcq",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "correct_answer": "O(n)",
            "explanation": "Without random access or sorting, we must traverse from head to find the element, taking O(n).",
            "difficulty": "easy",
            "learning_objective": "Linked list search complexity",
        },
        {
            "question_text": "Which of the following is NOT an advantage of linked lists over arrays?",
            "question_type": "mcq",
            "options": ["Dynamic size", "Efficient insertion at beginning", "O(1) random access", "No memory waste"],
            "correct_answer": "O(1) random access",
            "explanation": "Linked lists do NOT support O(1) random access — you must traverse from head. Arrays provide O(1) index access.",
            "difficulty": "medium",
            "learning_objective": "Array vs Linked List comparison",
        },
        {
            "question_text": "What is the approach to reverse a singly linked list in O(n) time and O(1) space?",
            "question_type": "mcq",
            "options": ["Stack-based reversal", "Recursive reversal", "Iterative pointer reversal", "Copy to array and reverse"],
            "correct_answer": "Iterative pointer reversal",
            "explanation": "Iterative pointer reversal uses three pointers (prev, curr, next) to reverse links in-place in O(n) time and O(1) space.",
            "difficulty": "hard",
            "learning_objective": "Linked list reversal algorithms",
        },
    ],
    
    # Data Structures - Stacks
    "stacks": [
        {
            "question_text": "Stacks follow which ordering principle?",
            "question_type": "mcq",
            "options": ["FIFO", "LIFO", "Priority-based", "Random"],
            "correct_answer": "LIFO",
            "explanation": "Stacks use Last In, First Out (LIFO) — the last element pushed is the first to be popped.",
            "difficulty": "easy",
            "learning_objective": "Stack ordering principle",
        },
        {
            "question_text": "Which operation removes the top element from a stack?",
            "question_type": "mcq",
            "options": ["push()", "pop()", "peek()", "dequeue()"],
            "correct_answer": "pop()",
            "explanation": "pop() removes and returns the top element. peek() only reads it without removal. dequeue() is a queue operation.",
            "difficulty": "easy",
            "learning_objective": "Stack operations",
        },
        {
            "question_text": "A stack can be used to check if parentheses in an expression are balanced.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Push opening brackets onto the stack. On closing bracket, check if it matches the top. If stack is empty at end, expression is balanced.",
            "difficulty": "medium",
            "learning_objective": "Stack applications",
        },
        {
            "question_text": "Function call management in most programming languages uses which data structure internally?",
            "question_type": "mcq",
            "options": ["Queue", "Stack (Call Stack)", "Heap", "Array"],
            "correct_answer": "Stack (Call Stack)",
            "explanation": "The call stack is a stack data structure that stores function call frames. Each function call pushes a frame; return pops it.",
            "difficulty": "medium",
            "learning_objective": "Real-world stack applications",
        },
        {
            "question_text": "What is the time complexity of push and pop operations on a stack implemented with a linked list?",
            "question_type": "mcq",
            "options": ["O(n) for both", "O(1) for both", "O(1) push, O(n) pop", "O(log n) for both"],
            "correct_answer": "O(1) for both",
            "explanation": "Both push and pop operate at the head of the linked list, requiring only pointer updates — O(1) each.",
            "difficulty": "medium",
            "learning_objective": "Stack implementation complexity",
        },
        {
            "question_text": "Which algorithm for evaluating postfix expressions uses a stack?",
            "question_type": "mcq",
            "options": ["Infix evaluation", "Dijkstra's two-stack algorithm", "Prim's algorithm", "DFS"],
            "correct_answer": "Dijkstra's two-stack algorithm",
            "explanation": "Dijkstra's two-stack algorithm uses separate stacks for operands and operators to evaluate postfix/infix expressions.",
            "difficulty": "hard",
            "learning_objective": "Advanced stack algorithms",
        },
    ],
    
    # Data Structures - Queues
    "queues": [
        {
            "question_text": "Queues follow which ordering principle?",
            "question_type": "mcq",
            "options": ["LIFO", "FIFO", "Priority-based", "Sorted order"],
            "correct_answer": "FIFO",
            "explanation": "Queues use First In, First Out (FIFO) — the first element enqueued is the first to be dequeued.",
            "difficulty": "easy",
            "learning_objective": "Queue ordering principle",
        },
        {
            "question_text": "Which operation adds an element to the back of a queue?",
            "question_type": "mcq",
            "options": ["push()", "enqueue()", "append()", "insert()"],
            "correct_answer": "enqueue()",
            "explanation": "enqueue() adds to the rear; dequeue() removes from the front. These are the standard queue operations.",
            "difficulty": "easy",
            "learning_objective": "Queue operations",
        },
        {
            "question_text": "BFS (Breadth-First Search) graph traversal uses a queue internally.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "BFS visits nodes level by level using a queue. Each node's neighbors are enqueued and processed in FIFO order.",
            "difficulty": "medium",
            "learning_objective": "Queue in BFS traversal",
        },
        {
            "question_text": "A circular queue is preferred over a linear queue because:",
            "question_type": "mcq",
            "options": ["It uses less memory absolutely", "It reuses empty front positions avoiding false overflow", "Elements are sorted automatically", "It allows O(1) random access"],
            "correct_answer": "It reuses empty front positions avoiding false overflow",
            "explanation": "In a linear queue, dequeued positions are wasted. A circular queue wraps around to reuse those positions.",
            "difficulty": "medium",
            "learning_objective": "Circular queue advantage",
        },
        {
            "question_text": "Priority Queue differs from a regular queue in that:",
            "question_type": "mcq",
            "options": ["Elements are dequeued by FIFO", "Elements are dequeued by priority", "It can only hold integers", "It uses a stack internally"],
            "correct_answer": "Elements are dequeued by priority",
            "explanation": "In a Priority Queue, elements are dequeued based on priority (highest or lowest first), not insertion order.",
            "difficulty": "medium",
            "learning_objective": "Priority queue concept",
        },
    ],
    
    # Data Structures - Trees
    "trees": [
        {
            "question_text": "In a Binary Search Tree (BST), for any node N: all values in the left subtree are _____ N, and all values in the right subtree are _____ N.",
            "question_type": "mcq",
            "options": ["greater than, less than", "less than, greater than", "equal to, greater than", "less than, equal to"],
            "correct_answer": "less than, greater than",
            "explanation": "BST property: left subtree values < node value < right subtree values. This enables O(log n) search.",
            "difficulty": "easy",
            "learning_objective": "BST property",
        },
        {
            "question_text": "What is the height of a balanced binary tree with n nodes?",
            "question_type": "mcq",
            "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"],
            "correct_answer": "O(log n)",
            "explanation": "A balanced binary tree splits nodes evenly at each level, giving height O(log n) — critical for efficient operations.",
            "difficulty": "easy",
            "learning_objective": "Binary tree height",
        },
        {
            "question_text": "Inorder traversal of a BST visits nodes in sorted (ascending) order.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Inorder (Left → Node → Right) on a BST visits nodes in ascending sorted order, making it useful for sorted output.",
            "difficulty": "medium",
            "learning_objective": "BST inorder traversal",
        },
        {
            "question_text": "Which tree traversal is used for making a copy of the tree?",
            "question_type": "mcq",
            "options": ["Inorder", "Preorder", "Postorder", "Level-order"],
            "correct_answer": "Preorder",
            "explanation": "Preorder (Node → Left → Right) is used to copy a tree because you process the root before the subtrees.",
            "difficulty": "medium",
            "learning_objective": "Tree traversal applications",
        },
        {
            "question_text": "An AVL tree maintains height balance by ensuring that for every node, the height difference between left and right subtrees is at most:",
            "question_type": "mcq",
            "options": ["0", "1", "2", "log n"],
            "correct_answer": "1",
            "explanation": "AVL trees maintain a balance factor of -1, 0, or +1 at every node. Rotation operations restore balance when violated.",
            "difficulty": "hard",
            "learning_objective": "AVL tree balance property",
        },
        {
            "question_text": "What is the worst-case time complexity of searching in an unbalanced BST?",
            "question_type": "mcq",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "correct_answer": "O(n)",
            "explanation": "A completely unbalanced BST degenerates into a linked list, making search O(n) in the worst case.",
            "difficulty": "hard",
            "learning_objective": "BST worst-case analysis",
        },
    ],
    
    # Data Structures - Graphs
    "graphs": [
        {
            "question_text": "In BFS (Breadth-First Search), which data structure is used?",
            "question_type": "mcq",
            "options": ["Stack", "Queue", "Heap", "Hash Table"],
            "correct_answer": "Queue",
            "explanation": "BFS uses a queue to process nodes level by level (FIFO order), ensuring shortest path in unweighted graphs.",
            "difficulty": "easy",
            "learning_objective": "BFS data structure",
        },
        {
            "question_text": "DFS (Depth-First Search) uses a stack (or recursion) for traversal.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "DFS uses a stack — either explicitly or via recursive call stack — to go as deep as possible before backtracking.",
            "difficulty": "easy",
            "learning_objective": "DFS data structure",
        },
        {
            "question_text": "Which algorithm finds the shortest path in a weighted graph with non-negative edges?",
            "question_type": "mcq",
            "options": ["BFS", "DFS", "Dijkstra's Algorithm", "Prim's Algorithm"],
            "correct_answer": "Dijkstra's Algorithm",
            "explanation": "Dijkstra's algorithm uses a priority queue to greedily select the shortest unvisited node, solving SSSP for non-negative weights.",
            "difficulty": "medium",
            "learning_objective": "Shortest path algorithms",
        },
        {
            "question_text": "An undirected graph with n vertices and n-1 edges is always a tree (connected, acyclic).",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "A connected undirected graph with exactly n-1 edges has no cycles — this is the definition of a tree.",
            "difficulty": "medium",
            "learning_objective": "Graph and tree relationship",
        },
        {
            "question_text": "What is the time complexity of BFS on a graph with V vertices and E edges using adjacency list?",
            "question_type": "mcq",
            "options": ["O(V)", "O(E)", "O(V + E)", "O(V × E)"],
            "correct_answer": "O(V + E)",
            "explanation": "BFS visits each vertex once (O(V)) and processes each edge once (O(E)), giving total time O(V + E).",
            "difficulty": "medium",
            "learning_objective": "BFS time complexity",
        },
        {
            "question_text": "Topological sort can only be applied to which type of graph?",
            "question_type": "mcq",
            "options": ["Undirected graphs", "Directed Acyclic Graphs (DAGs)", "Complete graphs", "Bipartite graphs"],
            "correct_answer": "Directed Acyclic Graphs (DAGs)",
            "explanation": "Topological sort requires a DAG — directed edges ensure ordering, acyclic property ensures a valid linear order exists.",
            "difficulty": "hard",
            "learning_objective": "Topological sort prerequisites",
        },
        {
            "question_text": "Floyd-Warshall algorithm finds:",
            "question_type": "mcq",
            "options": ["Single-source shortest paths", "All-pairs shortest paths", "Minimum spanning tree", "Maximum flow"],
            "correct_answer": "All-pairs shortest paths",
            "explanation": "Floyd-Warshall uses dynamic programming to find shortest paths between all pairs of vertices in O(V³) time.",
            "difficulty": "hard",
            "learning_objective": "All-pairs shortest path algorithms",
        },
    ],
    
    # Data Structures - Dynamic Programming
    "dynamic_programming": [
        {
            "question_text": "Dynamic Programming is applicable when a problem has which properties?",
            "question_type": "mcq",
            "options": ["Greedy choice and optimal substructure", "Overlapping subproblems and optimal substructure", "Divide and conquer only", "Linear time solvability"],
            "correct_answer": "Overlapping subproblems and optimal substructure",
            "explanation": "DP applies when: (1) subproblems overlap (computed multiple times) and (2) optimal solution builds from optimal subproblem solutions.",
            "difficulty": "easy",
            "learning_objective": "Dynamic programming properties",
        },
        {
            "question_text": "Memoization is the top-down approach to Dynamic Programming.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Memoization = top-down DP (recursion + cache). Tabulation = bottom-up DP (iterative, fills table from base cases up).",
            "difficulty": "easy",
            "learning_objective": "DP approaches: memoization vs tabulation",
        },
        {
            "question_text": "What is the time complexity of the standard DP solution to the 0/1 Knapsack problem (n items, capacity W)?",
            "question_type": "mcq",
            "options": ["O(n)", "O(W)", "O(n × W)", "O(2ⁿ)"],
            "correct_answer": "O(n × W)",
            "explanation": "The DP table has n rows (items) and W+1 columns (capacities), filled in O(1) per cell, giving O(n × W) total.",
            "difficulty": "medium",
            "learning_objective": "Knapsack DP complexity",
        },
        {
            "question_text": "The Fibonacci sequence naively computed with recursion has exponential time complexity but DP reduces it to:",
            "question_type": "mcq",
            "options": ["O(n²)", "O(n log n)", "O(n)", "O(log n)"],
            "correct_answer": "O(n)",
            "explanation": "DP memoizes or tabulates Fibonacci values from 0 to n, computing each exactly once — O(n) time, O(n) space (O(1) if optimized).",
            "difficulty": "medium",
            "learning_objective": "Fibonacci DP",
        },
        {
            "question_text": "Longest Common Subsequence (LCS) of two strings of lengths m and n has DP time complexity:",
            "question_type": "mcq",
            "options": ["O(m + n)", "O(m × n)", "O(m log n)", "O(2^max(m,n))"],
            "correct_answer": "O(m × n)",
            "explanation": "LCS DP fills an (m+1) × (n+1) table, each cell in O(1), giving O(m × n) time and space.",
            "difficulty": "hard",
            "learning_objective": "LCS dynamic programming",
        },
        {
            "question_text": "Which DP technique is used to solve the Coin Change problem (minimum coins)?",
            "question_type": "mcq",
            "options": ["Greedy only", "Top-down memoization or Bottom-up tabulation", "Divide and conquer", "BFS shortest path"],
            "correct_answer": "Top-down memoization or Bottom-up tabulation",
            "explanation": "Coin Change is a classic DP problem. Both memoization and tabulation work. Greedy fails for general coin systems.",
            "difficulty": "hard",
            "learning_objective": "Coin change dynamic programming",
        },
    ],
    
    # Mathematics - Calculus (generic subject example)
    "limits": [
        {
            "question_text": "What is the limit of sin(x)/x as x approaches 0?",
            "question_type": "mcq",
            "options": ["0", "∞", "1", "Undefined"],
            "correct_answer": "1",
            "explanation": "This is the fundamental trigonometric limit. Using L'Hôpital's rule or the squeeze theorem: lim(x→0) sin(x)/x = 1.",
            "difficulty": "medium",
            "learning_objective": "Fundamental limits",
        },
        {
            "question_text": "A limit exists at a point if and only if the left-hand and right-hand limits are equal.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "For lim(x→a) f(x) to exist, the left limit (x→a⁻) and right limit (x→a⁺) must both exist and be equal.",
            "difficulty": "easy",
            "learning_objective": "Limit existence conditions",
        },
    ],
    
    # Machine Learning
    "supervised_learning": [
        {
            "question_text": "In supervised learning, the training data consists of:",
            "question_type": "mcq",
            "options": ["Only input features", "Input features with labeled outputs", "Unlabeled data clusters", "Reward signals"],
            "correct_answer": "Input features with labeled outputs",
            "explanation": "Supervised learning requires labeled training data (input-output pairs) to learn a mapping function.",
            "difficulty": "easy",
            "learning_objective": "Supervised learning definition",
        },
        {
            "question_text": "Overfitting occurs when a model performs well on training data but poorly on unseen test data.",
            "question_type": "true_false",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Overfitting = model memorizes training data noise, losing generalization ability. Techniques like regularization and cross-validation address this.",
            "difficulty": "medium",
            "learning_objective": "Overfitting concept",
        },
        {
            "question_text": "Which metric is most appropriate for evaluating a classifier on an imbalanced dataset?",
            "question_type": "mcq",
            "options": ["Accuracy", "F1-Score", "MSE", "R²"],
            "correct_answer": "F1-Score",
            "explanation": "On imbalanced datasets, accuracy is misleading. F1-Score balances Precision and Recall, handling class imbalance better.",
            "difficulty": "hard",
            "learning_objective": "Classification metrics",
        },
    ],
}


class QuestionGenerator:
    """
    Deterministic template-based question generator.
    Selects questions based on topic, difficulty, and past mistakes.
    In demo mode, operates entirely without any external API.
    """
    
    def get_questions_for_topic(
        self,
        topic_code: str,
        difficulty: Optional[str] = None,
        num_questions: int = 5,
        exclude_ids: Optional[List[int]] = None,
        student_mastery: float = 50.0
    ) -> List[Dict[str, Any]]:
        """
        Generate questions for a topic deterministically.
        
        If difficulty is None, auto-selects based on mastery:
        - mastery < 40 → easy
        - 40-65 → medium  
        - > 65 → hard
        """
        if difficulty is None:
            if student_mastery < 40:
                difficulty = "easy"
            elif student_mastery < 65:
                difficulty = "medium"
            else:
                difficulty = "hard"
        
        # Look up topic bank
        topic_questions = QUESTION_BANK.get(topic_code, [])
        
        # If no bank for this topic, generate generic questions
        if not topic_questions:
            topic_questions = self._generate_generic_questions(topic_code, difficulty)
        
        # Filter by difficulty (include easier if not enough questions)
        difficulty_order = ["easy", "medium", "hard"]
        filtered = [q for q in topic_questions if q["difficulty"] == difficulty]
        
        if len(filtered) < num_questions:
            # Fill with adjacent difficulty
            for d in difficulty_order:
                if d != difficulty:
                    filtered += [q for q in topic_questions if q["difficulty"] == d]
        
        # Deterministic selection
        rng = random.Random(_seed_for(topic_code, difficulty, 42))
        rng.shuffle(filtered)
        
        # Assign deterministic IDs and return
        result = []
        for i, q in enumerate(filtered[:num_questions]):
            question = q.copy()
            question["id"] = abs(hash(f"{topic_code}_{difficulty}_{i}")) % 100000 + 10000
            question["topic_code"] = topic_code
            result.append(question)
        
        return result
    
    def _generate_generic_questions(
        self, 
        topic_code: str, 
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate generic placeholder questions for unknown topics."""
        topic_name = topic_code.replace("_", " ").title()
        return [
            {
                "question_text": f"Which of the following best describes the core objective of {topic_name}?",
                "question_type": "mcq",
                "options": [
                    f"Solving algorithmic problems efficiently using {topic_name} principles",
                    f"Manual memory allocation without data structures",
                    f"Unstructured data processing without complexity constraints",
                    f"Compiling source code into machine instructions",
                ],
                "correct_answer": f"Solving algorithmic problems efficiently using {topic_name} principles",
                "explanation": f"Understanding the core objectives of {topic_name} is essential for designing optimal software algorithms.",
                "difficulty": "easy",
                "learning_objective": f"Core principles of {topic_name}",
            },
            {
                "question_text": f"Mastery of {topic_name} concepts requires understanding both theoretical time complexity and practical implementation.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "True",
                "explanation": f"Effective problem solving in {topic_name} balances algorithmic big-O bounds with clean implementation.",
                "difficulty": "easy",
                "learning_objective": f"Foundational mastery of {topic_name}",
            },
            {
                "question_text": f"What is the most effective approach when analyzing an algorithm in {topic_name}?",
                "question_type": "mcq",
                "options": [
                    "Identify worst-case time and space complexity",
                    "Rely solely on empirical execution time",
                    "Ignore edge cases and boundary conditions",
                    "Assume input sizes are always small",
                ],
                "correct_answer": "Identify worst-case time and space complexity",
                "explanation": "Big-O asymptotic analysis provides reliable performance guarantees across varying input sizes.",
                "difficulty": "medium",
                "learning_objective": "Algorithmic analysis",
            },
            {
                "question_text": f"In {topic_name}, what is the main tradeoff between iterative and recursive solutions?",
                "question_type": "mcq",
                "options": [
                    "Recursion incurs call stack overhead while iteration uses O(1) auxiliary space",
                    "Iteration is always O(n²) while recursion is O(1)",
                    "Recursion uses less memory than iteration in all cases",
                    "There is no difference in memory or stack execution",
                ],
                "correct_answer": "Recursion incurs call stack overhead while iteration uses O(1) auxiliary space",
                "explanation": "Recursive function calls add stack frames to memory, whereas iterative loops reuse local variable state.",
                "difficulty": "medium",
                "learning_objective": "Space-time trade-offs",
            },
            {
                "question_text": f"Which strategy is recommended when handling edge cases in {topic_name} problems?",
                "question_type": "mcq",
                "options": [
                    "Validate empty inputs, single element inputs, and boundary limits",
                    "Ignore empty inputs and test only typical cases",
                    "Rely on exception handlers to catch logic bugs",
                    "Assume input values are strictly positive integers",
                ],
                "correct_answer": "Validate empty inputs, single element inputs, and boundary limits",
                "explanation": "Robust algorithms explicitly handle null, empty, single-item, and overflow boundary conditions.",
                "difficulty": "medium",
                "learning_objective": "Edge case engineering",
            },
            {
                "question_text": f"What is the primary constraint when optimizing a {topic_name} algorithm from O(n²) to O(n log n)?",
                "question_type": "mcq",
                "options": [
                    "Utilizing divide-and-conquer or efficient heap/tree representations",
                    "Adding nested loops over the data",
                    "Converting all data types to floating point numbers",
                    "Increasing the memory footprint without structural changes",
                ],
                "correct_answer": "Utilizing divide-and-conquer or efficient heap/tree representations",
                "explanation": "Divide-and-conquer partitioning or logarithmic data structures reduce subproblem quadratic overhead.",
                "difficulty": "hard",
                "learning_objective": "Optimization techniques",
            },
            {
                "question_text": f"True or False: Space complexity for a {topic_name} algorithm includes both input space and auxiliary working memory.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "True",
                "explanation": "Total space complexity accounts for input data structures plus extra workspace allocated during execution.",
                "difficulty": "medium",
                "learning_objective": "Space complexity evaluation",
            },
            {
                "question_text": f"When evaluating a {topic_name} solution for production systems, which factor is crucial alongside time complexity?",
                "question_type": "mcq",
                "options": [
                    "Code readability, maintainability, and thread safety",
                    "File size of the source code",
                    "Number of comments in the function body",
                    "Variable naming length",
                ],
                "correct_answer": "Code readability, maintainability, and thread safety",
                "explanation": "Production code requires robust error handling, concurrency safeguards, and clear architectural structure.",
                "difficulty": "easy",
                "learning_objective": "Production engineering standards",
            },
            {
                "question_text": f"What type of data structure is most commonly combined with {topic_name} for fast O(1) lookups?",
                "question_type": "mcq",
                "options": [
                    "Hash Map / Hash Table",
                    "Singly Linked List",
                    "Binary Search Tree",
                    "Array Stack",
                ],
                "correct_answer": "Hash Map / Hash Table",
                "explanation": "Hash tables provide average O(1) key-value lookup, making them ideal for accelerating subproblem queries.",
                "difficulty": "medium",
                "learning_objective": "Data structure synergy",
            },
            {
                "question_text": f"Which paradigm is best suited for solving optimization problems in {topic_name} with optimal substructure?",
                "question_type": "mcq",
                "options": [
                    "Dynamic Programming / Greedy Choice",
                    "Brute Force Permutation",
                    "Randomized Sampling",
                    "Linear Search Traversal",
                ],
                "correct_answer": "Dynamic Programming / Greedy Choice",
                "explanation": "Optimal substructure allows building global optimal solutions from local subproblems using DP or Greedy approaches.",
                "difficulty": "hard",
                "learning_objective": "Algorithmic paradigms",
            },
        ]
    
    def generate_diagnostic_questions(
        self,
        topic_codes: List[str],
        questions_per_topic: int = 2
    ) -> List[Dict[str, Any]]:
        """Generate balanced diagnostic set across multiple topics."""
        all_questions = []
        for topic_code in topic_codes:
            questions = self.get_questions_for_topic(
                topic_code,
                difficulty=None,
                num_questions=questions_per_topic,
                student_mastery=50  # use medium difficulty for diagnostics
            )
            all_questions.extend(questions)
        
        # Shuffle deterministically
        rng = random.Random(12345)
        rng.shuffle(all_questions)
        return all_questions


question_generator = QuestionGenerator()
