"""
LearnLens AI - LLM Service
Abstraction layer for LLM API calls.
Falls back to rule-based responses if no API key is set.
"""
import os
from typing import Optional, Dict, Any


DEMO_EXPLANATIONS: Dict[str, Dict[str, str]] = {
    "arrays": {
        "explain": """**Arrays** are contiguous memory structures that store elements of the same type.

**Key Properties:**
- Fixed size (static arrays) or dynamic (dynamic arrays/vectors)
- O(1) random access by index
- O(n) insertion/deletion in the middle
- Elements stored in consecutive memory locations

**Common Operations:**
- Traverse: O(n)
- Search (unsorted): O(n), Search (sorted, binary): O(log n)
- Insert at end: O(1) amortized, Insert at middle: O(n)

**When to use Arrays:**
- When you need fast random access
- When size is known in advance
- For cache-friendly operations (sequential access)""",
        "example": """**Array Example: Two-Sum Problem**

```python
def two_sum(nums, target):
    seen = {}  # value → index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# Example:
nums = [2, 7, 11, 15]
target = 9
print(two_sum(nums, target))  # Output: [0, 1]
# Because nums[0] + nums[1] = 2 + 7 = 9
```

**Explanation:** Using a hash map turns the O(n²) brute force into O(n) time.""",
        "summarize": """**Quick Revision: Arrays**

✅ **Core Concept:** Contiguous memory, 0-indexed
✅ **Time Complexities:** Access O(1) | Search O(n) | Insert/Delete O(n)
✅ **Key Algorithms:** Binary Search, Two-pointer, Sliding Window, Kadane's
✅ **Common Patterns:** Sorting, Prefix sums, Hashing for lookups
⚠️ **Watch out for:** Off-by-one errors, index out of bounds"""
    },
    "graphs": {
        "explain": """**Graphs** are data structures consisting of vertices (nodes) and edges (connections).

**Types:**
- Directed vs Undirected
- Weighted vs Unweighted
- Cyclic vs Acyclic (DAG)

**Representations:**
- Adjacency Matrix: O(V²) space, O(1) edge check
- Adjacency List: O(V+E) space, O(degree) edge check

**Key Traversals:**
- **BFS** (Queue): Shortest path in unweighted graphs, level-order
- **DFS** (Stack/Recursion): Cycle detection, topological sort, SCC

**Key Algorithms:**
- Dijkstra's: Single-source shortest path (non-negative weights)
- Bellman-Ford: SSSP with negative weights
- Floyd-Warshall: All-pairs shortest path
- Kruskal's/Prim's: Minimum Spanning Tree""",
        "example": """**BFS vs DFS: When to Use Which**

```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

def dfs(graph, start, visited=None):
    if visited is None: visited = set()
    visited.add(start)
    order = [start]
    for neighbor in graph[start]:
        if neighbor not in visited:
            order.extend(dfs(graph, neighbor, visited))
    return order
```

**Use BFS for:** Shortest path, finding connected components, social network distance
**Use DFS for:** Cycle detection, topological sort, maze solving""",
        "summarize": """**Quick Revision: Graphs**

✅ **Core Concept:** V vertices, E edges — directed/undirected/weighted
✅ **BFS:** Queue, O(V+E), shortest path unweighted
✅ **DFS:** Stack/Recursion, O(V+E), cycle detection
✅ **Dijkstra:** Priority Queue, O((V+E)log V), shortest path weighted
✅ **Common Applications:** Navigation, social networks, dependency resolution
⚠️ **Watch out for:** Cycles in DFS (need visited set), disconnected graphs"""
    },
    "dynamic_programming": {
        "explain": """**Dynamic Programming (DP)** solves complex problems by breaking them into simpler overlapping subproblems and storing results.

**Two Key Properties Required:**
1. **Optimal Substructure:** Optimal solution contains optimal sub-solutions
2. **Overlapping Subproblems:** Same subproblems are solved repeatedly

**Two Approaches:**
- **Top-Down (Memoization):** Recursion + cache
- **Bottom-Up (Tabulation):** Fill table iteratively from base cases

**Classic DP Problems:**
- Fibonacci (foundation)
- 0/1 Knapsack (capacity optimization)
- LCS (string comparison)
- Edit Distance (string edit)
- Coin Change (minimum coins)
- Matrix Chain Multiplication""",
        "example": """**Classic Example: Fibonacci with DP**

```python
# ❌ Naive (O(2^n)):
def fib_naive(n):
    if n <= 1: return n
    return fib_naive(n-1) + fib_naive(n-2)

# ✅ Memoization (O(n)):
def fib_memo(n, memo={}):
    if n <= 1: return n
    if n in memo: return memo[n]
    memo[n] = fib_memo(n-1) + fib_memo(n-2)
    return memo[n]

# ✅ Tabulation (O(n), cleaner):
def fib_dp(n):
    if n <= 1: return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]

# ✅✅ Space-optimized (O(1)):
def fib_opt(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
```""",
        "summarize": """**Quick Revision: Dynamic Programming**

✅ **Core Concept:** Overlapping subproblems + optimal substructure
✅ **Memoization:** Top-down, recursive + cache dictionary
✅ **Tabulation:** Bottom-up, iterative table filling
✅ **State Design:** Identify what changes between subproblems
✅ **Classic Problems:** Knapsack, LCS, Coin Change, Paths in Grid
⚠️ **Watch out for:** Identifying correct state transitions and base cases"""
    }
}

DEFAULT_EXPLANATION = """**Concept Overview**

This topic covers fundamental concepts that build your problem-solving foundation.

**Learning Approach:**
1. Understand the core definition and motivation
2. Study concrete examples and trace through them manually
3. Identify the time and space complexity
4. Practice with progressively harder problems
5. Connect to related topics

**Tips for Mastery:**
- Draw diagrams to visualize abstract concepts
- Implement from scratch before using library functions
- Solve at least 5-10 varied problems per concept
- Review mistakes carefully — they reveal misconceptions"""


class LLMService:
    """
    LLM abstraction that works in both API and demo modes.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.demo_mode = not bool(self.api_key) or os.getenv("DEMO_MODE", "true").lower() == "true"
    
    def get_explanation(
        self,
        topic_code: str,
        topic_name: str,
        action: str,
        mastery_score: float,
        context: Optional[str] = None
    ) -> str:
        """Get AI explanation for a concept."""
        
        if self.demo_mode:
            return self._get_demo_explanation(topic_code, topic_name, action, mastery_score)
        
        # Real LLM call (only if API key is configured)
        try:
            return self._call_openai(topic_code, topic_name, action, mastery_score, context)
        except Exception as e:
            return self._get_demo_explanation(topic_code, topic_name, action, mastery_score)
    
    def _get_demo_explanation(
        self,
        topic_code: str,
        topic_name: str,
        action: str,
        mastery_score: float
    ) -> str:
        """Return rich pre-written explanations for demo mode."""
        topic_bank = DEMO_EXPLANATIONS.get(topic_code, {})
        base_text = topic_bank.get(action, DEFAULT_EXPLANATION)
        
        # Add personalized context header
        mastery_context = ""
        if mastery_score < 40:
            mastery_context = f"📊 **Your Current Level:** You are at {mastery_score:.0f}% mastery in {topic_name} — we'll start from the fundamentals.\n\n"
        elif mastery_score < 60:
            mastery_context = f"📊 **Your Current Level:** You are developing in {topic_name} ({mastery_score:.0f}% mastery). Let's focus on the gaps.\n\n"
        elif mastery_score < 80:
            mastery_context = f"📊 **Your Current Level:** You are proficient in {topic_name} ({mastery_score:.0f}%). Let's push toward mastery.\n\n"
        else:
            mastery_context = f"📊 **Your Current Level:** You have strong mastery in {topic_name} ({mastery_score:.0f}%). Here's a quick refresher.\n\n"
        
        return mastery_context + base_text
    
    def _call_openai(
        self,
        topic_code: str,
        topic_name: str,
        action: str,
        mastery_score: float,
        context: Optional[str]
    ) -> str:
        """Call OpenAI API (only used when API key is configured)."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            action_prompts = {
                "explain": f"Explain {topic_name} clearly with key concepts, properties, and use cases.",
                "example": f"Give a concrete code example demonstrating {topic_name} with explanation.",
                "hint": f"Give a helpful hint for solving a {topic_name} problem without giving away the answer.",
                "practice": f"Create a practice problem for {topic_name} at appropriate difficulty.",
                "summarize": f"Create a concise revision summary for {topic_name} with key points.",
            }
            
            system_prompt = f"""You are LearnLens AI, an adaptive learning assistant.
The student's current mastery in {topic_name} is {mastery_score:.0f}%.
Personalize your response based on this mastery level.
Be concise, use markdown formatting, and include code examples where relevant."""
            
            user_prompt = action_prompts.get(action, f"Help with {topic_name}")
            if context:
                user_prompt += f"\n\nAdditional context: {context}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=800,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return self._get_demo_explanation(topic_code, topic_name, action, mastery_score)
    
    def get_hint_for_question(
        self,
        question_text: str,
        topic_name: str,
        correct_answer: str,
        student_answer: Optional[str] = None
    ) -> str:
        """Generate a hint without revealing the answer."""
        if student_answer:
            return f"""💡 **Hint for this question:**

Your answer was not quite right. Here's a nudge in the right direction:

- Re-read the question carefully and identify key terms
- Think about the fundamental definition related to **{topic_name}**
- Consider edge cases or special properties
- Remember: the answer relates to a core concept, not an exception

Try reasoning through the options systematically rather than guessing."""
        else:
            return f"""💡 **Hint:**

For this {topic_name} question:
- Identify the core concept being tested
- Recall the definition and key properties
- Think about examples you've seen
- Eliminate obviously wrong answers first"""


llm_service = LLMService()
