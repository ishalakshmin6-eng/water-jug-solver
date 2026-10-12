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


class GraphNode(NamedTuple):
    """Represents a node in the state-space graph or search tree."""
    id: str
    state: State
    label: str
    is_initial: bool
    is_goal: bool
    is_solution: bool
    depth: int = 0


class GraphEdge(NamedTuple):
    """Represents a directed transition between two states."""
    source_id: str
    target_id: str
    action: str
    description: str
    is_solution: bool


class StateSpaceGraph(NamedTuple):
    """Encapsulates full state-space graph or search tree structure."""
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class ZoneDemand(NamedTuple):
    """Represents municipal district demand in Smart City Water Allocation CSP."""
    name: str
    priority_level: int  # 1 (Critical) to 5 (Eco)
    priority_label: str
    min_critical: int
    target_demand: int
    description: str


class ZoneAllocation(NamedTuple):
    """Resulting allocation for a specific municipal zone."""
    zone_name: str
    priority_label: str
    allocated: int
    target_demand: int
    min_critical: int
    satisfaction_pct: float
    status: str


class CSPAllocationResult(NamedTuple):
    """Outcome and constraint metrics for Smart City Water Allocation CSP."""
    is_solved: bool
    total_reservoir: int
    total_allocated: int
    total_demand: int
    unmet_demand: int
    allocations: List[ZoneAllocation]
    nodes_explored: int
    backtracks_count: int
    execution_time_ms: float
    status_message: str


