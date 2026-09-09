"""
Data models and type definitions for the Water Jug Problem Solver.
"""

from typing import Tuple, List, NamedTuple

# State represents the current water volume in (Jug A, Jug B)
State = Tuple[int, int]


class TransitionStep(NamedTuple):
    """Represents a single state transition along a solution path."""
    step_number: int
    action_name: str
    state: State
    description: str


class SearchResult(NamedTuple):
    """Contains outcome, statistics, and execution trace for a search algorithm."""
    algorithm_name: str
    is_solved: bool
    path: List[TransitionStep]
    nodes_explored: int
    max_frontier_size: int
    execution_time_ms: float
