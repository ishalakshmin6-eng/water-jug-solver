"""
Core State-Space Search Solver for the Water Jug Problem.
"""

from collections import deque
import math
import time
from typing import List, Tuple, Set, Optional

try:
    from .models import State, TransitionStep, SearchResult
except ImportError:
    from models import State, TransitionStep, SearchResult


class WaterJugProblem:
    """
    Formal State-Space formulation of the Two-Jug Water Jug Problem.

    Mathematical Representation:
      - State Space S: {(a, b) | 0 <= a <= cap_a, 0 <= b <= cap_b}
      - Initial State s_0: (0, 0)
      - Goal Test G(s): s[0] == target or s[1] == target
      - Actions A(s): Fill(A), Fill(B), Empty(A), Empty(B), Pour(A->B), Pour(B->A)
      - Transition Function T: S x A -> S
      - Step Cost c(s, a, s'): 1 (unit step cost)
    """

    def __init__(self, cap_a: int, cap_b: int, target: int) -> None:
        """
        Initialize the Water Jug environment.

        :param cap_a: Maximum capacity of Jug A (strictly positive integer).
        :param cap_b: Maximum capacity of Jug B (strictly positive integer).
        :param target: Target water volume to measure in either jug.
        """
        if cap_a <= 0 or cap_b <= 0:
            raise ValueError(f"Jug capacities must be positive integers. Received cap_a={cap_a}, cap_b={cap_b}")
        if target < 0:
            raise ValueError(f"Target volume cannot be negative. Received target={target}")

        self.cap_a: int = cap_a
        self.cap_b: int = cap_b
        self.target: int = target
        self.initial_state: State = (0, 0)

    def is_solvable(self) -> Tuple[bool, str]:
        """
        Check solvability using Bezout's Identity and Diophantine equations.

        A target volume T can be measured if and only if:
          1. T <= max(cap_a, cap_b)
          2. T % gcd(cap_a, cap_b) == 0
        """
        if self.target > max(self.cap_a, self.cap_b):
            return False, (
                f"Target volume ({self.target}L) exceeds maximum capacity of both jugs "
                f"(max({self.cap_a}L, {self.cap_b}L) = {max(self.cap_a, self.cap_b)}L)."
            )

        gcd_val = math.gcd(self.cap_a, self.cap_b)
        if self.target % gcd_val != 0:
            return False, (
                f"Target volume ({self.target}L) is not a multiple of GCD({self.cap_a}, {self.cap_b}) = {gcd_val}. "
                f"By Bezout's Identity, any linear combination a*x + b*y must be a multiple of gcd(a, b)."
            )

        return True, f"Solvable: Target ({self.target}L) <= max capacity and is divisible by GCD({self.cap_a}, {self.cap_b}) = {gcd_val}."

    def is_goal(self, state: State) -> bool:
        """Evaluate whether the given state satisfies the goal condition."""
        return state[0] == self.target or state[1] == self.target

    def get_successors(self, state: State) -> List[Tuple[str, State, str]]:
        """
        Generate all valid successor states from the current state.

        Returns a list of tuples: (action_name, next_state, description)
        Valid Operators:
          1. Fill Jug A
          2. Fill Jug B
          3. Empty Jug A
          4. Empty Jug B
          5. Pour Jug A -> Jug B
          6. Pour Jug B -> Jug A
        """
        a, b = state
        successors: List[Tuple[str, State, str]] = []

        # 1. Fill Jug A
        if a < self.cap_a:
            successors.append((
                "Fill Jug A",
                (self.cap_a, b),
                f"Fill Jug A to full capacity ({self.cap_a}L)"
            ))

        # 2. Fill Jug B
        if b < self.cap_b:
            successors.append((
                "Fill Jug B",
                (a, self.cap_b),
                f"Fill Jug B to full capacity ({self.cap_b}L)"
            ))

        # 3. Empty Jug A
        if a > 0:
            successors.append((
                "Empty Jug A",
                (0, b),
                "Empty all water from Jug A"
            ))

        # 4. Empty Jug B
        if b > 0:
            successors.append((
                "Empty Jug B",
                (a, 0),
                "Empty all water from Jug B"
            ))

        # 5. Pour Jug A into Jug B
        if a > 0 and b < self.cap_b:
            transfer = min(a, self.cap_b - b)
            successors.append((
                "Pour Jug A -> Jug B",
                (a - transfer, b + transfer),
                f"Pour {transfer}L from Jug A into Jug B"
            ))

        # 6. Pour Jug B into Jug A
        if b > 0 and a < self.cap_a:
            transfer = min(b, self.cap_a - a)
            successors.append((
                "Pour Jug B -> Jug A",
                (a + transfer, b - transfer),
                f"Pour {transfer}L from Jug B into Jug A"
            ))

        return successors

    def solve_bfs(self) -> SearchResult:
        """
        Breadth-First Search (BFS) Solver.

        BFS expands nodes shallowest-first using a FIFO queue.
        Properties:
          - Completeness: Guaranteed to find a solution if one exists in finite graph.
          - Optimality: Guaranteed to return the shortest path (minimum operations)
            since all action costs are uniform (c = 1).
        """
        start_time = time.perf_counter()

        # Check trivial initial state
        if self.is_goal(self.initial_state):
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            initial_step = TransitionStep(0, "Initial State", self.initial_state, "Starting configuration")
            return SearchResult("Breadth-First Search (BFS)", True, [initial_step], 1, 1, elapsed_ms)

        # Frontier queue stores tuples: (current_state, path_so_far)
        frontier: deque[Tuple[State, List[Tuple[str, State, str]]]] = deque()
        frontier.append((self.initial_state, [("Initial State", self.initial_state, "Starting configuration")]))

        visited: Set[State] = {self.initial_state}
        nodes_explored = 0
        max_frontier_size = 1

        while frontier:
            max_frontier_size = max(max_frontier_size, len(frontier))
            current_state, path = frontier.popleft()
            nodes_explored += 1

            for action_name, next_state, desc in self.get_successors(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    new_path = path + [(action_name, next_state, desc)]

                    # Early goal check for BFS optimization
                    if self.is_goal(next_state):
                        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                        formatted_path = [
                            TransitionStep(idx, step[0], step[1], step[2])
                            for idx, step in enumerate(new_path)
                        ]
                        return SearchResult(
                            "Breadth-First Search (BFS)",
                            True,
                            formatted_path,
                            nodes_explored,
                            max_frontier_size,
                            elapsed_ms
                        )

                    frontier.append((next_state, new_path))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SearchResult("Breadth-First Search (BFS)", False, [], nodes_explored, max_frontier_size, elapsed_ms)

    def solve_dfs(self) -> SearchResult:
        """
        Depth-First Search (DFS) Solver.

        DFS expands nodes deepest-first using a LIFO stack.
        Properties:
          - Completeness: Complete in finite state spaces with graph search (visited set).
          - Optimality: Non-optimal. It returns the first path encountered, which may
            involve unnecessary circular or alternating operations.
        """
        start_time = time.perf_counter()

        # Check trivial initial state
        if self.is_goal(self.initial_state):
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            initial_step = TransitionStep(0, "Initial State", self.initial_state, "Starting configuration")
            return SearchResult("Depth-First Search (DFS)", True, [initial_step], 1, 1, elapsed_ms)

        # Frontier stack stores tuples: (current_state, path_so_far)
        stack: List[Tuple[State, List[Tuple[str, State, str]]]] = [
            (self.initial_state, [("Initial State", self.initial_state, "Starting configuration")])
        ]

        visited: Set[State] = {self.initial_state}
        nodes_explored = 0
        max_frontier_size = 1

        while stack:
            max_frontier_size = max(max_frontier_size, len(stack))
            current_state, path = stack.pop()
            nodes_explored += 1

            if self.is_goal(current_state):
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                formatted_path = [
                    TransitionStep(idx, step[0], step[1], step[2])
                    for idx, step in enumerate(path)
                ]
                return SearchResult(
                    "Depth-First Search (DFS)",
                    True,
                    formatted_path,
                    nodes_explored,
                    max_frontier_size,
                    elapsed_ms
                )

            # Explore successors
            for action_name, next_state, desc in self.get_successors(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    stack.append((next_state, path + [(action_name, next_state, desc)]))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SearchResult("Depth-First Search (DFS)", False, [], nodes_explored, max_frontier_size, elapsed_ms)
