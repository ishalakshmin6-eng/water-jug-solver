"""
Core State-Space Search Solver for the Water Jug Problem.
"""

from collections import deque
import csv
import datetime
import io
import json
import math
import time
from typing import List, Tuple, Set, Optional, Dict

try:
    from .models import (
        State,
        TransitionStep,
        SearchResult,
        GraphNode,
        GraphEdge,
        StateSpaceGraph,
        CSPAllocationResult,
    )
except ImportError:
    from models import (
        State,
        TransitionStep,
        SearchResult,
        GraphNode,
        GraphEdge,
        StateSpaceGraph,
        CSPAllocationResult,
    )




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

    def get_state_space_graph(
        self, solution_path: Optional[List[TransitionStep]] = None
    ) -> StateSpaceGraph:
        """
        Construct the complete reachable state-space graph starting from (0, 0).

        :param solution_path: Optional solution path from search algorithm to highlight.
        :return: StateSpaceGraph containing all reachable nodes and directed edges.
        """
        solution_states: Set[State] = set()
        solution_transitions: Set[Tuple[State, State]] = set()

        if solution_path:
            solution_states = {step.state for step in solution_path}
            for i in range(len(solution_path) - 1):
                solution_transitions.add((solution_path[i].state, solution_path[i + 1].state))

        queue: deque[State] = deque([self.initial_state])
        visited_states: Set[State] = {self.initial_state}
        edges: List[GraphEdge] = []
        nodes: List[GraphNode] = []

        visited_edge_signatures: Set[Tuple[State, State, str]] = set()

        while queue:
            curr_state = queue.popleft()
            curr_id = f"s_{curr_state[0]}_{curr_state[1]}"

            for action_name, next_state, desc in self.get_successors(curr_state):
                next_id = f"s_{next_state[0]}_{next_state[1]}"
                edge_sig = (curr_state, next_state, action_name)

                if edge_sig not in visited_edge_signatures:
                    visited_edge_signatures.add(edge_sig)
                    is_sol_edge = (curr_state, next_state) in solution_transitions
                    edges.append(
                        GraphEdge(
                            source_id=curr_id,
                            target_id=next_id,
                            action=action_name,
                            description=desc,
                            is_solution=is_sol_edge,
                        )
                    )

                if next_state not in visited_states:
                    visited_states.add(next_state)
                    queue.append(next_state)

        # Build node metadata
        for state in sorted(visited_states):
            node_id = f"s_{state[0]}_{state[1]}"
            is_init = state == self.initial_state
            is_goal = self.is_goal(state)
            is_sol = state in solution_states
            nodes.append(
                GraphNode(
                    id=node_id,
                    state=state,
                    label=f"({state[0]}, {state[1]})",
                    is_initial=is_init,
                    is_goal=is_goal,
                    is_solution=is_sol,
                    depth=0,
                )
            )

        return StateSpaceGraph(nodes=nodes, edges=edges)

    def get_search_tree(
        self, algorithm: str = "bfs", solution_path: Optional[List[TransitionStep]] = None
    ) -> StateSpaceGraph:
        """
        Generate the search exploration tree generated during BFS or DFS.

        :param algorithm: 'bfs' or 'dfs'.
        :param solution_path: Optional solution path to highlight in the tree.
        :return: StateSpaceGraph representing the search tree.
        """
        solution_states_seq: List[State] = [step.state for step in solution_path] if solution_path else []

        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []

        root_id = "node_0"
        is_root_goal = self.is_goal(self.initial_state)
        is_root_sol = bool(solution_states_seq and solution_states_seq[0] == self.initial_state)

        nodes.append(
            GraphNode(
                id=root_id,
                state=self.initial_state,
                label=f"({self.initial_state[0]}, {self.initial_state[1]})",
                is_initial=True,
                is_goal=is_root_goal,
                is_solution=is_root_sol,
                depth=0,
            )
        )

        counter = 0
        node_tree_map: Dict[str, State] = {root_id: self.initial_state}
        parent_map: Dict[str, Tuple[Optional[str], Optional[str]]] = {root_id: (None, None)}

        if algorithm.lower() == "bfs":
            frontier = deque([(self.initial_state, root_id, 0)])
            visited = {self.initial_state}

            while frontier:
                curr_state, curr_node_id, depth = frontier.popleft()
                if self.is_goal(curr_state) and depth > 0:
                    continue

                for action_name, next_state, desc in self.get_successors(curr_state):
                    if next_state not in visited:
                        visited.add(next_state)
                        counter += 1
                        child_id = f"node_{counter}"
                        node_tree_map[child_id] = next_state
                        parent_map[child_id] = (curr_node_id, action_name)
                        is_goal = self.is_goal(next_state)

                        nodes.append(
                            GraphNode(
                                id=child_id,
                                state=next_state,
                                label=f"({next_state[0]}, {next_state[1]})",
                                is_initial=False,
                                is_goal=is_goal,
                                is_solution=False,
                                depth=depth + 1,
                            )
                        )
                        edges.append(
                            GraphEdge(
                                source_id=curr_node_id,
                                target_id=child_id,
                                action=action_name,
                                description=desc,
                                is_solution=False,
                            )
                        )
                        frontier.append((next_state, child_id, depth + 1))
        else:
            # DFS tree
            stack = [(self.initial_state, root_id, 0)]
            visited = {self.initial_state}

            while stack:
                curr_state, curr_node_id, depth = stack.pop()
                if self.is_goal(curr_state) and depth > 0:
                    continue

                for action_name, next_state, desc in self.get_successors(curr_state):
                    if next_state not in visited:
                        visited.add(next_state)
                        counter += 1
                        child_id = f"node_{counter}"
                        node_tree_map[child_id] = next_state
                        parent_map[child_id] = (curr_node_id, action_name)
                        is_goal = self.is_goal(next_state)

                        nodes.append(
                            GraphNode(
                                id=child_id,
                                state=next_state,
                                label=f"({next_state[0]}, {next_state[1]})",
                                is_initial=False,
                                is_goal=is_goal,
                                is_solution=False,
                                depth=depth + 1,
                            )
                        )
                        edges.append(
                            GraphEdge(
                                source_id=curr_node_id,
                                target_id=child_id,
                                action=action_name,
                                description=desc,
                                is_solution=False,
                            )
                        )
                        stack.append((next_state, child_id, depth + 1))

        # Highlight solution branch if provided
        if solution_states_seq:
            goal_node_id = None
            for n in nodes:
                if n.state == solution_states_seq[-1] and n.is_goal:
                    goal_node_id = n.id
                    break

            if goal_node_id:
                sol_node_ids = set()
                sol_edge_pairs = set()
                curr_id = goal_node_id
                while curr_id:
                    sol_node_ids.add(curr_id)
                    p_id, _ = parent_map.get(curr_id, (None, None))
                    if p_id:
                        sol_edge_pairs.add((p_id, curr_id))
                    curr_id = p_id

                nodes = [
                    GraphNode(
                        id=n.id,
                        state=n.state,
                        label=n.label,
                        is_initial=n.is_initial,
                        is_goal=n.is_goal,
                        is_solution=n.id in sol_node_ids,
                        depth=n.depth,
                    )
                    for n in nodes
                ]
                edges = [
                    GraphEdge(
                        source_id=e.source_id,
                        target_id=e.target_id,
                        action=e.action,
                        description=e.description,
                        is_solution=(e.source_id, e.target_id) in sol_edge_pairs,
                    )
                    for e in edges
                ]

        return StateSpaceGraph(nodes=nodes, edges=edges)

    def generate_dot_graph(
        self,
        graph: StateSpaceGraph,
        title: str = "Water Jug State-Space Graph",
        rankdir: str = "TB",
        solution_only: bool = False,
    ) -> str:
        """
        Generate Graphviz DOT representation of state-space graph or search tree.

        :param graph: StateSpaceGraph to render.
        :param title: Graph title.
        :param rankdir: 'TB' (top-to-bottom) or 'LR' (left-to-right).
        :param solution_only: If True, only render the nodes and edges on the solution path.
        :return: Valid Graphviz DOT string.
        """
        lines = [
            'digraph WaterJugGraph {',
            f'    rankdir="{rankdir}";',
            '    bgcolor="transparent";',
            '    compound=true;',
            '    nodesep=0.45;',
            '    ranksep=0.65;',
            '    node [fontname="Helvetica, Arial, sans-serif", fontsize=10, style="filled,rounded", shape=box, height=0.55, width=1.1, margin="0.1,0.08"];',
            '    edge [fontname="Helvetica, Arial, sans-serif", fontsize=8, arrowsize=0.7];',
            '',
        ]

        valid_nodes = [n for n in graph.nodes if (not solution_only or n.is_solution)]
        valid_node_ids = {n.id for n in valid_nodes}

        lines.append('    // Nodes')
        for node in valid_nodes:
            a, b = node.state
            status_tag = ""
            if node.is_initial:
                status_tag = " [Start]"
            elif node.is_goal:
                status_tag = " [Goal 🎯]"
            elif node.is_solution:
                status_tag = " [Sol]"

            label_text = f"({a}, {b}){status_tag}\\n[{a}L / {b}L]"

            if node.is_initial:
                lines.append(
                    f'    "{node.id}" [label="{label_text}", fillcolor="#dbeafe", color="#0284c7", penwidth=2.5, fontcolor="#0c4a6e"];'
                )
            elif node.is_goal:
                lines.append(
                    f'    "{node.id}" [label="{label_text}", fillcolor="#d1fae5", color="#059669", penwidth=3.0, peripheries=2, fontcolor="#064e3b"];'
                )
            elif node.is_solution:
                lines.append(
                    f'    "{node.id}" [label="{label_text}", fillcolor="#e0f2fe", color="#0284c7", penwidth=2.5, fontcolor="#0369a1"];'
                )
            else:
                lines.append(
                    f'    "{node.id}" [label="{label_text}", fillcolor="#f8fafc", color="#cbd5e1", penwidth=1.2, fontcolor="#334155"];'
                )

        lines.append('')
        lines.append('    // Edges')
        for edge in graph.edges:
            if edge.source_id not in valid_node_ids or edge.target_id not in valid_node_ids:
                continue

            if edge.is_solution:
                lines.append(
                    f'    "{edge.source_id}" -> "{edge.target_id}" [label=" {edge.action} ", color="#0284c7", penwidth=2.8, fontcolor="#0369a1", weight=2];'
                )
            elif not solution_only:
                lines.append(
                    f'    "{edge.source_id}" -> "{edge.target_id}" [label=" {edge.action} ", color="#cbd5e1", penwidth=1.0, fontcolor="#64748b", weight=1];'
                )

        lines.append('}')
        return '\n'.join(lines)

    def generate_visjs_html(
        self,
        graph: StateSpaceGraph,
        height: int = 580,
    ) -> str:
        """
        Generate interactive Vis.js Network visualization HTML.

        Features:
          - Physics spring simulation with freeze/unfreeze toggle
          - Hierarchical tree layout vs force-directed organic layout toggle
          - Pan, zoom, node drag, and interactive click inspector
          - Solution path highlighter
        """
        vis_nodes = []
        for node in graph.nodes:
            a, b = node.state
            pct_a = int((a / self.cap_a) * 100) if self.cap_a > 0 else 0
            pct_b = int((b / self.cap_b) * 100) if self.cap_b > 0 else 0

            # Classification
            role = "Intermediate Reachable State"
            if node.is_initial:
                role = "Initial Root State (0, 0)"
            elif node.is_goal:
                role = f"🎯 Goal State (Target {self.target}L)"
            elif node.is_solution:
                role = "Solution Path Transition"

            # Colors
            if node.is_initial:
                bg = "#dbeafe"
                border = "#0284c7"
                text_col = "#0c4a6e"
                bw = 3
            elif node.is_goal:
                bg = "#d1fae5"
                border = "#059669"
                text_col = "#064e3b"
                bw = 3
            elif node.is_solution:
                bg = "#e0f2fe"
                border = "#0284c7"
                text_col = "#0369a1"
                bw = 2.5
            else:
                bg = "#f8fafc"
                border = "#cbd5e1"
                text_col = "#334155"
                bw = 1.5

            vis_nodes.append({
                "id": node.id,
                "label": f"({a}, {b})\n[{a}L / {b}L]",
                "title": f"State ({a}, {b}) | {role}\nJug A: {a}/{self.cap_a}L ({pct_a}%)\nJug B: {b}/{self.cap_b}L ({pct_b}%)",
                "shape": "box",
                "margin": 10,
                "borderWidth": bw,
                "color": {
                    "background": bg,
                    "border": border,
                    "highlight": {"background": "#fed7aa", "border": "#ea580c"},
                    "hover": {"background": "#e2e8f0", "border": border},
                },
                "font": {"color": text_col, "face": "Outfit, sans-serif", "size": 12, "bold": node.is_solution or node.is_goal},
                "shadow": True,
                "level": node.depth if node.depth > 0 else None,
                "stateA": a,
                "stateB": b,
                "capA": self.cap_a,
                "capB": self.cap_b,
                "target": self.target,
                "role": role,
                "isInitial": node.is_initial,
                "isGoal": node.is_goal,
                "isSolution": node.is_solution,
            })

        vis_edges = []
        for edge in graph.edges:
            vis_edges.append({
                "from": edge.source_id,
                "to": edge.target_id,
                "label": edge.action,
                "title": edge.description,
                "arrows": "to",
                "color": {
                    "color": "#0284c7" if edge.is_solution else "#94a3b8",
                    "highlight": "#ea580c",
                    "hover": "#0284c7",
                },
                "width": 3 if edge.is_solution else 1.2,
                "isSolution": edge.is_solution,
                "font": {
                    "size": 10,
                    "face": "Outfit, sans-serif",
                    "color": "#0369a1" if edge.is_solution else "#64748b",
                    "background": "rgba(255, 255, 255, 0.85)",
                    "align": "middle",
                },
                "smooth": {"type": "curvedCW", "roundness": 0.15},
            })

        nodes_json = json.dumps(vis_nodes)
        edges_json = json.dumps(vis_edges)

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700&display=swap">
    <script type="text/javascript" src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
            background: #f8fafc;
            color: #1e293b;
        }}
        .graph-wrapper {{
            display: flex;
            flex-direction: column;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            overflow: hidden;
            background: #ffffff;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        .toolbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px;
            padding: 10px 16px;
            background: #f1f5f9;
            border-bottom: 1px solid #e2e8f0;
        }}
        .toolbar-group {{
            display: flex;
            gap: 6px;
            align-items: center;
        }}
        .btn {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            padding: 5px 12px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #334155;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn:hover {{
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
        }}
        .btn.active {{
            background: #0284c7;
            color: #ffffff;
            border-color: #0284c7;
        }}
        select.dropdown {{
            padding: 5px 10px;
            border-radius: 6px;
            border: 1px solid #cbd5e1;
            font-size: 0.82rem;
            background: #ffffff;
            color: #334155;
            font-weight: 600;
        }}
        #network {{
            width: 100%;
            height: {height}px;
            background: #fafafa;
        }}
        .inspector-card {{
            padding: 12px 16px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 0.88rem;
        }}
        .fill-meter {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .meter-bar {{
            width: 100px;
            height: 12px;
            background: #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            position: relative;
        }}
        .meter-fill {{
            height: 100%;
            border-radius: 6px;
            transition: width 0.3s ease;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .badge-init {{ background: #dbeafe; color: #0369a1; }}
        .badge-goal {{ background: #d1fae5; color: #047857; }}
        .badge-sol  {{ background: #fed7aa; color: #c2410c; }}
        .badge-reg  {{ background: #e2e8f0; color: #475569; }}
    </style>
</head>
<body>
    <div class="graph-wrapper">
        <div class="toolbar">
            <div class="toolbar-group">
                <button class="btn" id="btnLayout" onclick="toggleLayout()">📐 Layout: Organic</button>
                <button class="btn" id="btnPhysics" onclick="togglePhysics()">⏸️ Physics: Active</button>
                <button class="btn" onclick="fitGraph()">🎯 Fit Screen</button>
                <button class="btn" id="btnFilterSol" onclick="toggleFilterSol()">✨ Highlight Solution</button>
            </div>
            <div class="toolbar-group">
                <span style="font-size: 0.82rem; font-weight: 600; color: #64748b;">Jump to Node:</span>
                <select id="nodeSelect" class="dropdown" onchange="jumpToNode(this.value)">
                    <option value="">-- Choose State --</option>
                </select>
            </div>
        </div>
        <div id="network"></div>
        <div class="inspector-card" id="inspectorCard">
            <div>
                <strong>Selected Node:</strong> <span id="inspState">Click any state above to inspect details</span>
                <span id="inspBadge" class="badge" style="display: none; margin-left: 8px;"></span>
            </div>
            <div id="inspGauges" style="display: none;" class="toolbar-group">
                <div class="fill-meter">
                    <span>Jug A:</span>
                    <div class="meter-bar"><div id="gaugeA" class="meter-fill" style="background: #0284c7; width: 0%;"></div></div>
                    <span id="valA">0L</span>
                </div>
                <div class="fill-meter">
                    <span>Jug B:</span>
                    <div class="meter-bar"><div id="gaugeB" class="meter-fill" style="background: #0d9488; width: 0%;"></div></div>
                    <span id="valB">0L</span>
                </div>
            </div>
        </div>
    </div>

    <script type="text/javascript">
        const rawNodes = {nodes_json};
        const rawEdges = {edges_json};

        let nodesDataset = new vis.DataSet(rawNodes);
        let edgesDataset = new vis.DataSet(rawEdges);

        const container = document.getElementById('network');
        const data = {{ nodes: nodesDataset, edges: edgesDataset }};

        let isHierarchical = false;
        let isPhysicsActive = true;
        let isSolFiltered = false;

        const options = {{
            nodes: {{
                shape: 'box',
                shadow: true,
                borderWidth: 2,
                margin: 10
            }},
            edges: {{
                arrows: {{ to: {{ enabled: true, scaleFactor: 0.8 }} }},
                smooth: {{ type: 'curvedCW', roundness: 0.15 }}
            }},
            physics: {{
                enabled: true,
                solver: 'forceAtlas2Based',
                forceAtlas2Based: {{
                    gravitationalConstant: -38,
                    centralGravity: 0.01,
                    springLength: 100,
                    springConstant: 0.08,
                    damping: 0.4
                }},
                stabilization: {{ iterations: 120 }}
            }},
            interaction: {{
                hover: true,
                dragNodes: true,
                zoomView: true,
                navigationButtons: false
            }}
        }};

        let network = new vis.Network(container, data, options);

        // Populate dropdown
        const selectEl = document.getElementById('nodeSelect');
        rawNodes.forEach(n => {{
            let opt = document.createElement('option');
            opt.value = n.id;
            opt.textContent = `State (${{n.stateA}}, ${{n.stateB}})${{n.isInitial ? ' [Start]' : ''}}${{n.isGoal ? ' [Goal]' : ''}}`;
            selectEl.appendChild(opt);
        }});

        function updateInspector(nodeData) {{
            if (!nodeData) return;
            document.getElementById('inspState').textContent = `State (${{nodeData.stateA}}L, ${{nodeData.stateB}}L)`;
            const badge = document.getElementById('inspBadge');
            badge.style.display = 'inline-block';
            badge.textContent = nodeData.role;
            if (nodeData.isGoal) badge.className = 'badge badge-goal';
            else if (nodeData.isInitial) badge.className = 'badge badge-init';
            else if (nodeData.isSolution) badge.className = 'badge badge-sol';
            else badge.className = 'badge badge-reg';

            document.getElementById('inspGauges').style.display = 'flex';
            const pctA = Math.round((nodeData.stateA / nodeData.capA) * 100);
            const pctB = Math.round((nodeData.stateB / nodeData.capB) * 100);

            document.getElementById('gaugeA').style.width = pctA + '%';
            document.getElementById('valA').textContent = `${{nodeData.stateA}} / ${{nodeData.capA}}L (${{pctA}}%)`;

            document.getElementById('gaugeB').style.width = pctB + '%';
            document.getElementById('valB').textContent = `${{nodeData.stateB}} / ${{nodeData.capB}}L (${{pctB}}%)`;
        }}

        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const nodeData = rawNodes.find(n => n.id === nodeId);
                updateInspector(nodeData);
                selectEl.value = nodeId;
            }}
        }});

        function jumpToNode(nodeId) {{
            if (!nodeId) return;
            network.focus(nodeId, {{
                scale: 1.2,
                animation: {{ duration: 600, easingFunction: 'easeInOutQuad' }}
            }});
            network.selectNodes([nodeId]);
            const nodeData = rawNodes.find(n => n.id === nodeId);
            updateInspector(nodeData);
        }}

        function togglePhysics() {{
            isPhysicsActive = !isPhysicsActive;
            network.setOptions({{ physics: {{ enabled: isPhysicsActive }} }});
            const btn = document.getElementById('btnPhysics');
            btn.textContent = isPhysicsActive ? '⏸️ Physics: Active' : '▶️ Physics: Frozen';
            btn.classList.toggle('active', !isPhysicsActive);
        }}

        function toggleLayout() {{
            isHierarchical = !isHierarchical;
            const btn = document.getElementById('btnLayout');
            if (isHierarchical) {{
                btn.textContent = '📐 Layout: Tree (Hierarchical)';
                btn.classList.add('active');
                network.setOptions({{
                    layout: {{
                        hierarchical: {{
                            direction: 'UD',
                            sortMethod: 'directed',
                            levelSeparation: 110,
                            nodeSpacing: 140
                        }}
                    }},
                    physics: {{ enabled: false }}
                }});
            }} else {{
                btn.textContent = '📐 Layout: Organic';
                btn.classList.remove('active');
                network.setOptions({{
                    layout: {{ hierarchical: false }},
                    physics: {{ enabled: true }}
                }});
            }}
            network.fit();
        }}

        function fitGraph() {{
            network.fit({{ animation: {{ duration: 500, easingFunction: 'easeInOutQuad' }} }});
        }}

        function toggleFilterSol() {{
            isSolFiltered = !isSolFiltered;
            const btn = document.getElementById('btnFilterSol');
            btn.classList.toggle('active', isSolFiltered);

            if (isSolFiltered) {{
                // Dim non-solution nodes
                const updatedNodes = rawNodes.map(n => {{
                    if (!n.isSolution) {{
                        return {{
                            id: n.id,
                            color: {{ background: '#f1f5f9', border: '#e2e8f0' }},
                            font: {{ color: '#94a3b8' }},
                            opacity: 0.35
                        }};
                    }} else {{
                        return {{
                            id: n.id,
                            color: {{ background: '#dbeafe', border: '#0284c7' }},
                            font: {{ color: '#0369a1', bold: true }}
                        }};
                    }}
                }});
                const updatedEdges = rawEdges.map(e => {{
                    return {{
                        id: e.id,
                        hidden: !e.isSolution,
                        color: {{ color: e.isSolution ? '#0284c7' : '#e2e8f0' }}
                    }};
                }});
                nodesDataset.update(updatedNodes);
                edgesDataset.update(updatedEdges);
            }} else {{
                // Restore all
                nodesDataset.clear();
                nodesDataset.add(rawNodes);
                edgesDataset.clear();
                edgesDataset.add(rawEdges);
            }}
        }}

        // Initial selection to root node if present
        if (rawNodes.length > 0) {{
            updateInspector(rawNodes[0]);
        }}
    </script>
</body>
</html>
"""
        return html_template


# ==============================================================================
# Multi-Format Export Engine (CSV, JSON, PDF)
# ==============================================================================
def export_solution_csv(problem: WaterJugProblem, result: SearchResult) -> str:
    """Export step-by-step state transitions to standard CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Step",
        "Action",
        "Jug_A_Liters",
        "Jug_B_Liters",
        "Jug_A_Capacity",
        "Jug_B_Capacity",
        "Target_Volume",
        "Operation_Description"
    ])
    for step in result.path:
        writer.writerow([
            step.step_number,
            step.action_name,
            step.state[0],
            step.state[1],
            problem.cap_a,
            problem.cap_b,
            problem.target,
            step.description
        ])
    return output.getvalue()


def export_solution_json(
    problem: WaterJugProblem,
    bfs_result: Optional[SearchResult] = None,
    dfs_result: Optional[SearchResult] = None,
    student_reg_no: str = "113025148034",
    seed: int = 148034,
    csp_result: Optional[CSPAllocationResult] = None,
) -> str:
    """Export complete problem execution trace, benchmarks, and CSP metrics to structured JSON."""
    solvable, reason = problem.is_solvable()
    payload: Dict = {
        "metadata": {
            "project": "Water Jug Problem Solver & Smart City Water Grid",
            "student_register_number": student_reg_no,
            "deterministic_seed": seed,
            "timestamp": datetime.datetime.now().isoformat(),
        },
        "problem_configuration": {
            "capacity_a": problem.cap_a,
            "capacity_b": problem.cap_b,
            "target_volume": problem.target,
            "is_solvable": solvable,
            "solvability_analysis": reason,
        },
        "search_algorithms": {}
    }

    for res, key in [(bfs_result, "bfs"), (dfs_result, "dfs")]:
        if res:
            payload["search_algorithms"][key] = {
                "algorithm_name": res.algorithm_name,
                "is_solved": res.is_solved,
                "solution_steps_count": len(res.path) - 1 if res.is_solved else 0,
                "nodes_explored": res.nodes_explored,
                "max_frontier_size": res.max_frontier_size,
                "execution_time_ms": res.execution_time_ms,
                "path": [
                    {
                        "step": s.step_number,
                        "action": s.action_name,
                        "state_a": s.state[0],
                        "state_b": s.state[1],
                        "description": s.description
                    }
                    for s in res.path
                ]
            }

    if csp_result:
        payload["smart_city_water_csp"] = {
            "is_solved": csp_result.is_solved,
            "total_reservoir": csp_result.total_reservoir,
            "total_allocated": csp_result.total_allocated,
            "total_demand": csp_result.total_demand,
            "unmet_demand": csp_result.unmet_demand,
            "nodes_explored": csp_result.nodes_explored,
            "backtracks_count": csp_result.backtracks_count,
            "execution_time_ms": csp_result.execution_time_ms,
            "status_message": csp_result.status_message,
            "allocations": [
                {
                    "zone_name": a.zone_name,
                    "priority_label": a.priority_label,
                    "allocated": a.allocated,
                    "target_demand": a.target_demand,
                    "min_critical": a.min_critical,
                    "satisfaction_pct": a.satisfaction_pct,
                    "status": a.status,
                }
                for a in csp_result.allocations
            ]
        }

    return json.dumps(payload, indent=2)


def export_solution_pdf(
    problem: WaterJugProblem,
    bfs_result: Optional[SearchResult] = None,
    dfs_result: Optional[SearchResult] = None,
    student_reg_no: str = "113025148034",
    seed: int = 148034,
    csp_result: Optional[CSPAllocationResult] = None,
) -> bytes:
    """Export formatted academic project report as PDF using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#475569'),
            spaceAfter=12
        )
        section_style = ParagraphStyle(
            'ReportSection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=16,
            textColor=colors.HexColor('#0284c7'),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#1e293b')
        )

        elements = []

        # Title & Metadata
        elements.append(Paragraph("Water Jug Problem Solver & Smart City Water Grid Analysis", title_style))
        elements.append(Paragraph(
            f"<b>Student Register No:</b> {student_reg_no} | "
            f"<b>Deterministic Seed:</b> {seed} | "
            f"<b>Generated:</b> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
            subtitle_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=10))

        # Problem Configuration
        solvable, reason = problem.is_solvable()
        elements.append(Paragraph("1. Problem Configuration & Bézout's Solvability", section_style))
        config_data = [
            ["Parameter", "Configured Value", "Mathematical Analysis"],
            ["Jug A Capacity", f"{problem.cap_a} Liters", "Capacity bound $C_A$"],
            ["Jug B Capacity", f"{problem.cap_b} Liters", "Capacity bound $C_B$"],
            ["Target Volume", f"{problem.target} Liters", f"GCD({problem.cap_a}, {problem.cap_b}) = {math.gcd(problem.cap_a, problem.cap_b)}"],
            ["Solvability Status", "SOLVABLE ✅" if solvable else "UNSOLVABLE ❌", reason],
        ]
        t_config = Table(config_data, colWidths=[130, 120, 280])
        t_config.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        elements.append(t_config)
        elements.append(Spacer(1, 10))

        # Algorithm Comparison Table
        if bfs_result or dfs_result:
            elements.append(Paragraph("2. State-Space Search Performance Comparison", section_style))
            comp_headers = ["Metric", "BFS (Breadth-First)", "DFS (Depth-First)"]
            bfs_steps = f"{len(bfs_result.path) - 1} actions" if (bfs_result and bfs_result.is_solved) else "N/A"
            dfs_steps = f"{len(dfs_result.path) - 1} actions" if (dfs_result and dfs_result.is_solved) else "N/A"

            comp_rows = [
                comp_headers,
                ["Status", "SOLVED ✅" if (bfs_result and bfs_result.is_solved) else "FAILED", "SOLVED ✅" if (dfs_result and dfs_result.is_solved) else "FAILED"],
                ["Solution Steps", bfs_steps, dfs_steps],
                ["Optimality", "Optimal (Shortest)", "Non-Optimal"],
                ["Nodes Explored", str(bfs_result.nodes_explored if bfs_result else "N/A"), str(dfs_result.nodes_explored if dfs_result else "N/A")],
                ["Max Frontier", str(bfs_result.max_frontier_size if bfs_result else "N/A"), str(dfs_result.max_frontier_size if dfs_result else "N/A")],
                ["Runtime", f"{bfs_result.execution_time_ms:.3f} ms" if bfs_result else "N/A", f"{dfs_result.execution_time_ms:.3f} ms" if dfs_result else "N/A"],
            ]
            t_comp = Table(comp_rows, colWidths=[150, 190, 190])
            t_comp.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_comp)
            elements.append(Spacer(1, 10))

        # Primary Solution Steps Table
        target_res = bfs_result if (bfs_result and bfs_result.is_solved) else dfs_result
        if target_res and target_res.is_solved:
            elements.append(Paragraph(f"3. Step-by-Step Transition Ledger ({target_res.algorithm_name})", section_style))
            step_table_data = [["Step", "Action", "State (A, B)", "Operation Description"]]
            for s in target_res.path:
                step_table_data.append([
                    str(s.step_number),
                    s.action_name,
                    f"({s.state[0]}L, {s.state[1]}L)",
                    s.description
                ])
            t_steps = Table(step_table_data, colWidths=[40, 120, 90, 280])
            t_steps.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(t_steps)
            elements.append(Spacer(1, 10))

        # Smart City CSP Allocation Section (if present)
        if csp_result:
            elements.append(Paragraph("4. Smart City Municipal Water Allocation (CSP)", section_style))
            elements.append(Paragraph(
                f"<b>Reservoir Capacity:</b> {csp_result.total_reservoir}kL | "
                f"<b>Allocated:</b> {csp_result.total_allocated}kL | "
                f"<b>Demand:</b> {csp_result.total_demand}kL | "
                f"<b>Status:</b> {csp_result.status_message}",
                body_style
            ))
            elements.append(Spacer(1, 4))
            csp_rows = [["Sector / Zone", "Priority", "Allocated / Target", "Satisfaction", "Status"]]
            for a in csp_result.allocations:
                csp_rows.append([
                    a.zone_name,
                    a.priority_label,
                    f"{a.allocated} / {a.target_demand} kL",
                    f"{a.satisfaction_pct}%",
                    a.status
                ])
            t_csp = Table(csp_rows, colWidths=[150, 90, 110, 80, 100])
            t_csp.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d9488')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
            ]))
            elements.append(t_csp)

        doc.build(elements)
        return buffer.getvalue()
    except Exception as e:
        # Fallback to plain bytes text header if rendering fails
        fallback_text = (
            f"Water Jug Problem Report\nStudent Reg: {student_reg_no}\nSeed: {seed}\n"
            f"Capacities: ({problem.cap_a}L, {problem.cap_b}L) -> Target {problem.target}L\n"
            f"Error generating PDF: {e}"
        )
        return fallback_text.encode("utf-8")


