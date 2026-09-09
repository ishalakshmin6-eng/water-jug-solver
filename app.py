"""
Water Jug Problem Solver - State Space Search
================================================================================
Student Register Number : 113025148034
Course Module           : Artificial Intelligence & State-Space Search
Deterministic Seed      : 148034 (int("113025148034"[-6:]))
================================================================================

This module models and solves the classic Water Jug Problem using State-Space Search.
It implements:
  - Formal State-Space representation: State = (jug_a: int, jug_b: int)
  - Canonical state-transition operators: Fill, Empty, and Pour
  - Breadth-First Search (BFS) for optimal/shortest path discovery
  - Depth-First Search (DFS) for depth-oriented state exploration
  - Number-theoretic solvability verification (Bezout's Identity / GCD)
  - Zero external dependencies (Python Standard Library only)
"""

import argparse
from collections import deque
import math
import random
import sys
import time
from typing import List, Tuple, Set, Optional, Dict, NamedTuple

# ==============================================================================
# Student Identification & Deterministic Seeding Ground Rules
# ==============================================================================
STUDENT_REG_NO: str = "113025148034"
DETERMINISTIC_SEED: int = int(STUDENT_REG_NO[-6:])  # Extracts 148034

random.seed(DETERMINISTIC_SEED)


# ==============================================================================
# Domain Types and Data Structures
# ==============================================================================
# State represents the current volume in (Jug A, Jug B)
State = Tuple[int, int]


class TransitionStep(NamedTuple):
    """Represents a single state transition along a solution path."""
    step_number: int
    action_name: str
    state: State
    description: str


class SearchResult(NamedTuple):
    """Contains outcome, statistics, and trace for an executed search algorithm."""
    algorithm_name: str
    is_solved: bool
    path: List[TransitionStep]
    nodes_explored: int
    max_frontier_size: int
    execution_time_ms: float


# ==============================================================================
# Water Jug Problem Formulation
# ==============================================================================
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
        # path_so_far contains tuples: (action_name, state, description)
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

            # Explore successors (in deterministic order)
            for action_name, next_state, desc in self.get_successors(current_state):
                if next_state not in visited:
                    visited.add(next_state)
                    stack.append((next_state, path + [(action_name, next_state, desc)]))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SearchResult("Depth-First Search (DFS)", False, [], nodes_explored, max_frontier_size, elapsed_ms)


# ==============================================================================
# CLI Presentation & Terminal Formatting
# ==============================================================================
def render_header() -> None:
    """Print project banner with student registration and seed metadata."""
    print("=" * 82)
    print("   WATER JUG PROBLEM SOLVER - STATE SPACE SEARCH")
    print("   University Project | Artificial Intelligence & Search Algorithms")
    print("=" * 82)
    print(f" * Student Register Number : {STUDENT_REG_NO}")
    print(f" * Deterministic Seed      : {DETERMINISTIC_SEED} (seed = int(reg_no[-6:]))")
    print(f" * Random Module Status    : Seeded & Deterministic")
    print("=" * 82)


def render_problem_info(problem: WaterJugProblem, solvable: bool, reason: str) -> None:
    """Display problem configuration and mathematical verification."""
    print("\n[1] PROBLEM CONFIGURATION & MATHEMATICAL VERIFICATION")
    print("-" * 82)
    print(f" * Jug A Capacity : {problem.cap_a} Liters")
    print(f" * Jug B Capacity : {problem.cap_b} Liters")
    print(f" * Target Volume  : {problem.target} Liters (in either Jug A or Jug B)")
    print(f" * Initial State  : Jug A = 0L, Jug B = 0L -> (0, 0)")
    print(f" * Solvability    : {'YES (Solvable)' if solvable else 'NO (Unsolvable)'}")
    print(f" * Analysis       : {reason}")
    print("-" * 82)


def render_search_result(problem: WaterJugProblem, result: SearchResult) -> None:
    """Format and print detailed step-by-step search execution trace and metrics."""
    print(f"\n[>] ALGORITHM: {result.algorithm_name}")
    print("=" * 82)

    if not result.is_solved:
        print(" [!] No sequence of actions can lead to the target volume.")
        print(f"  * Nodes Explored: {result.nodes_explored}")
        print(f"  * Execution Time: {result.execution_time_ms:.3f} ms")
        print("=" * 82)
        return

    total_steps = len(result.path) - 1
    print(f" [+] Solution Discovered! Total Transitions: {total_steps} step(s)")
    print("-" * 82)
    header_fmt = "{:<6} | {:<22} | {:<16} | {:<32}"
    row_fmt    = "{:<6} | {:<22} | {:<16} | {:<32}"

    print(header_fmt.format("Step", "Action", "State (A, B)", "Operation Detail"))
    print("-" * 82)

    for step in result.path:
        state_str = f"({step.state[0]}L, {step.state[1]}L)"
        jug_visual = f"[{step.state[0]}/{problem.cap_a}L, {step.state[1]}/{problem.cap_b}L]"
        formatted_state = f"{state_str:<9} {jug_visual}"
        print(row_fmt.format(step.step_number, step.action_name, formatted_state, step.description))

    print("-" * 82)
    print(" PERMISSION & PERFORMANCE METRICS:")
    print(f"  * Optimal / Shortest Path : {'YES (Guaranteed by BFS)' if 'BFS' in result.algorithm_name else 'Not Guaranteed (DFS Path)'}")
    print(f"  * Path Length (Cost)      : {total_steps} actions")
    print(f"  * Nodes Explored          : {result.nodes_explored}")
    print(f"  * Max Frontier Size       : {result.max_frontier_size}")
    print(f"  * Execution Time          : {result.execution_time_ms:.4f} ms")
    print("=" * 82)


def render_comparison_summary(bfs_result: SearchResult, dfs_result: SearchResult) -> None:
    """Print side-by-side comparison between BFS and DFS metrics."""
    print("\n[2] COMPARATIVE ANALYSIS: BFS vs DFS")
    print("=" * 82)
    print(f"{'Metric':<28} | {'BFS (Breadth-First)':<24} | {'DFS (Depth-First)':<24}")
    print("-" * 82)

    bfs_steps = len(bfs_result.path) - 1 if bfs_result.is_solved else "N/A"
    dfs_steps = len(dfs_result.path) - 1 if dfs_result.is_solved else "N/A"

    print(f"{'Status':<28} | {('SOLVED' if bfs_result.is_solved else 'FAILED'):<24} | {('SOLVED' if dfs_result.is_solved else 'FAILED'):<24}")
    print(f"{'Solution Steps (Cost)':<28} | {str(bfs_steps):<24} | {str(dfs_steps):<24}")
    print(f"{'Path Optimality':<28} | {'Optimal (Shortest)':<24} | {'Non-Optimal (First Found)':<24}")
    print(f"{'Nodes Explored':<28} | {str(bfs_result.nodes_explored):<24} | {str(dfs_result.nodes_explored):<24}")
    print(f"{'Max Frontier Size':<28} | {str(bfs_result.max_frontier_size):<24} | {str(dfs_result.max_frontier_size):<24}")
    print(f"{'Execution Time (ms)':<28} | {f'{bfs_result.execution_time_ms:.4f} ms':<24} | {f'{dfs_result.execution_time_ms:.4f} ms':<24}")
    print("=" * 82)


# ==============================================================================
# CLI Entrypoint
# ==============================================================================
def parse_arguments() -> argparse.Namespace:
    """Configure and parse command-line arguments using argparse."""
    parser = argparse.ArgumentParser(
        description="Water Jug Problem Solver using State-Space Search (BFS / DFS)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"Student Register Number: {STUDENT_REG_NO} | Deterministic Seed: {DETERMINISTIC_SEED}"
    )

    parser.add_argument(
        "--cap_a",
        type=int,
        default=4,
        help="Capacity of Jug A in liters."
    )
    parser.add_argument(
        "--cap_b",
        type=int,
        default=3,
        help="Capacity of Jug B in liters."
    )
    parser.add_argument(
        "--target",
        type=int,
        default=2,
        help="Target volume of water in liters to be measured."
    )
    parser.add_argument(
        "--algorithm",
        type=str,
        choices=["bfs", "dfs", "both"],
        default="bfs",
        help="Search algorithm to execute: 'bfs' (optimal path), 'dfs', or 'both' for comparative analysis."
    )

    return parser.parse_args()


def main() -> None:
    """Main execution flow for Water Jug Solver."""
    render_header()
    args = parse_arguments()

    try:
        problem = WaterJugProblem(cap_a=args.cap_a, cap_b=args.cap_b, target=args.target)
    except ValueError as err:
        print(f"\n[ERROR] Invalid parameters: {err}", file=sys.stderr)
        sys.exit(1)

    is_solvable, reason = problem.is_solvable()
    render_problem_info(problem, is_solvable, reason)

    if not is_solvable:
        print("\n[!] Halting search: Problem is mathematically unsolvable under given capacities.\n")
        sys.exit(0)

    # Execute search based on CLI selection
    if args.algorithm == "bfs":
        bfs_res = problem.solve_bfs()
        render_search_result(problem, bfs_res)

    elif args.algorithm == "dfs":
        dfs_res = problem.solve_dfs()
        render_search_result(problem, dfs_res)

    elif args.algorithm == "both":
        bfs_res = problem.solve_bfs()
        dfs_res = problem.solve_dfs()
        render_search_result(problem, bfs_res)
        render_search_result(problem, dfs_res)
        render_comparison_summary(bfs_res, dfs_res)


if __name__ == "__main__":
    main()
