"""
Unit tests for Water Jug Problem Solver (BFS & DFS).
================================================================================
Student Register Number : 113025148034
================================================================================
"""

import os
import sys
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.models import State, TransitionStep, SearchResult, CSPAllocationResult
from src.solver import (
    WaterJugProblem,
    export_solution_csv,
    export_solution_json,
    export_solution_pdf,
)
from src.csp_solver import SmartCityWaterCSP



class TestWaterJugSolver(unittest.TestCase):
    """Test suite covering State-Space Search models, transitions, and algorithms."""

    def test_solvability_analysis(self) -> None:
        """Verify Diophantine solvability checks via Bezout's Identity."""
        # Solvable cases
        prob1 = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        solvable, _ = prob1.is_solvable()
        self.assertTrue(solvable, "Expected (4, 3, 2) to be solvable")

        prob2 = WaterJugProblem(cap_a=5, cap_b=3, target=4)
        solvable, _ = prob2.is_solvable()
        self.assertTrue(solvable, "Expected (5, 3, 4) to be solvable")

        # Unsolvable: target exceeds maximum container capacity
        prob3 = WaterJugProblem(cap_a=3, cap_b=2, target=5)
        solvable, reason = prob3.is_solvable()
        self.assertFalse(solvable, "Target exceeding capacity must be unsolvable")
        self.assertIn("exceeds maximum capacity", reason)

        # Unsolvable: target not divisible by GCD(cap_a, cap_b)
        prob4 = WaterJugProblem(cap_a=6, cap_b=4, target=5)
        solvable, reason = prob4.is_solvable()
        self.assertFalse(solvable, "Target not divisible by GCD must be unsolvable")
        self.assertIn("not a multiple of GCD", reason)

    def test_invalid_constructor_parameters(self) -> None:
        """Ensure invalid capacities and negative target volumes raise ValueError."""
        with self.assertRaises(ValueError):
            WaterJugProblem(cap_a=0, cap_b=3, target=2)

        with self.assertRaises(ValueError):
            WaterJugProblem(cap_a=4, cap_b=-1, target=2)

        with self.assertRaises(ValueError):
            WaterJugProblem(cap_a=4, cap_b=3, target=-5)

    def test_trivial_goal_target_zero(self) -> None:
        """Initial state (0, 0) is already goal when target is 0."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=0)
        bfs_res = problem.solve_bfs()
        self.assertTrue(bfs_res.is_solved)
        self.assertEqual(len(bfs_res.path), 1)
        self.assertEqual(bfs_res.path[0].state, (0, 0))

        dfs_res = problem.solve_dfs()
        self.assertTrue(dfs_res.is_solved)
        self.assertEqual(len(dfs_res.path), 1)

    def test_bfs_optimality_4_3_2(self) -> None:
        """Verify BFS finds the optimal shortest path for (4L, 3L, Target 2L)."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        result = problem.solve_bfs()

        self.assertTrue(result.is_solved, "BFS should discover a solution")
        # Optimal cost for (4, 3, 2) is 4 actions
        total_actions = len(result.path) - 1
        self.assertEqual(total_actions, 4, f"Optimal BFS solution should be 4 actions, got {total_actions}")

        # Final state must contain 2L in either jug
        final_state = result.path[-1].state
        self.assertTrue(final_state[0] == 2 or final_state[1] == 2, f"Final state {final_state} must contain target 2L")

    def test_dfs_solution_discovery_4_3_2(self) -> None:
        """Verify DFS discovers a valid solution path for (4L, 3L, Target 2L)."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        result = problem.solve_dfs()

        self.assertTrue(result.is_solved, "DFS should discover a solution")
        final_state = result.path[-1].state
        self.assertTrue(final_state[0] == 2 or final_state[1] == 2, f"Final state {final_state} must contain target 2L")

    def test_bfs_vs_dfs_5_3_4(self) -> None:
        """Verify BFS finds optimal 6 actions for (5, 3, 4), while DFS is also valid."""
        problem = WaterJugProblem(cap_a=5, cap_b=3, target=4)

        bfs_res = problem.solve_bfs()
        dfs_res = problem.solve_dfs()

        self.assertTrue(bfs_res.is_solved)
        self.assertTrue(dfs_res.is_solved)

        # BFS shortest path is 6 actions
        bfs_actions = len(bfs_res.path) - 1
        self.assertEqual(bfs_actions, 6)

        # DFS may find equal or longer path
        dfs_actions = len(dfs_res.path) - 1
        self.assertGreaterEqual(dfs_actions, bfs_actions)

    def test_path_transition_validity(self) -> None:
        """Verify all step transitions in the solution path follow valid environment rules."""
        problem = WaterJugProblem(cap_a=5, cap_b=3, target=4)
        result = problem.solve_bfs()

        self.assertTrue(result.is_solved)
        path = result.path
        self.assertEqual(path[0].state, (0, 0))

        for i in range(len(path) - 1):
            curr_state = path[i].state
            next_step = path[i + 1]

            # Check that next state is a valid successor of curr_state
            valid_successors = [s[1] for s in problem.get_successors(curr_state)]
            self.assertIn(
                next_step.state,
                valid_successors,
                f"Transition from {curr_state} to {next_step.state} is invalid."
            )

    def test_state_space_graph_generation(self) -> None:
        """Verify complete state-space graph computes reachable states and valid transitions."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()
        graph = problem.get_state_space_graph(solution_path=bfs_res.path)

        self.assertGreater(len(graph.nodes), 0)
        self.assertGreater(len(graph.edges), 0)

        # Check initial state node exists
        init_nodes = [n for n in graph.nodes if n.is_initial]
        self.assertEqual(len(init_nodes), 1)
        self.assertEqual(init_nodes[0].state, (0, 0))

        # Check goal node exists
        goal_nodes = [n for n in graph.nodes if n.is_goal]
        self.assertGreater(len(goal_nodes), 0)
        for g_node in goal_nodes:
            self.assertTrue(g_node.state[0] == 2 or g_node.state[1] == 2)

        # Check solution transitions are tagged
        sol_edges = [e for e in graph.edges if e.is_solution]
        self.assertEqual(len(sol_edges), len(bfs_res.path) - 1)

    def test_search_tree_generation(self) -> None:
        """Verify search tree generation for BFS and DFS traversal."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()

        bfs_tree = problem.get_search_tree(algorithm="bfs", solution_path=bfs_res.path)
        self.assertGreater(len(bfs_tree.nodes), 0)
        self.assertGreater(len(bfs_tree.edges), 0)
        self.assertTrue(any(n.is_initial for n in bfs_tree.nodes))
        self.assertTrue(any(n.is_goal for n in bfs_tree.nodes))

        dfs_res = problem.solve_dfs()
        dfs_tree = problem.get_search_tree(algorithm="dfs", solution_path=dfs_res.path)
        self.assertGreater(len(dfs_tree.nodes), 0)
        self.assertTrue(any(n.is_initial for n in dfs_tree.nodes))

    def test_dot_graph_export(self) -> None:
        """Verify valid Graphviz DOT language syntax generation."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()
        graph = problem.get_state_space_graph(solution_path=bfs_res.path)

        dot_str = problem.generate_dot_graph(graph, rankdir="LR", solution_only=False)
        self.assertIn("digraph WaterJugGraph {", dot_str)
        self.assertIn('rankdir="LR";', dot_str)
        self.assertIn('"s_0_0"', dot_str)
        self.assertIn("->", dot_str)

        # Test solution-only mode
        dot_sol = problem.generate_dot_graph(graph, solution_only=True)
        self.assertIn("digraph WaterJugGraph {", dot_sol)
        # All included nodes in solution_only must be part of solution
        self.assertIn("[Start]", dot_sol)

    def test_visjs_html_generation(self) -> None:
        """Verify interactive Vis.js HTML generation with JSON payloads and controls."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()
        graph = problem.get_state_space_graph(solution_path=bfs_res.path)

        html = problem.generate_visjs_html(graph)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("vis-network", html)
        self.assertIn("togglePhysics", html)
        self.assertIn("toggleLayout", html)
        self.assertIn("network", html)

    def test_csp_water_allocation_standard(self) -> None:
        """Verify Smart City CSP solver under standard municipal reservoir capacity."""
        csp = SmartCityWaterCSP(reservoir_capacity=150)
        res = csp.solve()

        self.assertTrue(res.is_solved)
        self.assertEqual(res.total_reservoir, 150)
        self.assertLessEqual(res.total_allocated, 150)
        self.assertGreater(len(res.allocations), 0)

        # Hospital (P1) must receive at least minimum critical threshold (30kL)
        hospital = next(a for a in res.allocations if "Hospital" in a.zone_name)
        self.assertGreaterEqual(hospital.allocated, hospital.min_critical)

    def test_csp_water_allocation_drought(self) -> None:
        """Verify Smart City CSP detects severe shortage when capacity is below critical lifeline."""
        csp = SmartCityWaterCSP(reservoir_capacity=15)
        res = csp.solve()

        # Capacity 15 is below hospital critical 30 -> cannot be solved
        self.assertFalse(res.is_solved)
        self.assertIn("Drought", res.status_message)

    def test_export_solution_csv(self) -> None:
        """Verify CSV export formats all steps and column headers accurately."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()

        csv_text = export_solution_csv(problem, bfs_res)
        self.assertIn("Step,Action,Jug_A_Liters,Jug_B_Liters", csv_text)
        self.assertIn("Initial State", csv_text)
        self.assertIn("Fill Jug B", csv_text)

    def test_export_solution_json(self) -> None:
        """Verify JSON export contains valid technical schema, metadata, and arrays."""
        import json
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()
        dfs_res = problem.solve_dfs()
        csp_res = SmartCityWaterCSP(reservoir_capacity=150).solve()

        json_str = export_solution_json(
            problem,
            bfs_result=bfs_res,
            dfs_result=dfs_res,
            student_reg_no="113025148034",
            seed=148034,
            csp_result=csp_res
        )
        parsed = json.loads(json_str)
        self.assertEqual(parsed["metadata"]["student_register_number"], "113025148034")
        self.assertTrue(parsed["problem_configuration"]["is_solvable"])
        self.assertIn("bfs", parsed["search_algorithms"])
        self.assertIn("dfs", parsed["search_algorithms"])
        self.assertIn("smart_city_water_csp", parsed)

    def test_export_solution_pdf(self) -> None:
        """Verify PDF export generates valid binary PDF document."""
        problem = WaterJugProblem(cap_a=4, cap_b=3, target=2)
        bfs_res = problem.solve_bfs()
        csp_res = SmartCityWaterCSP(reservoir_capacity=150).solve()

        pdf_bytes = export_solution_pdf(
            problem,
            bfs_result=bfs_res,
            student_reg_no="113025148034",
            seed=148034,
            csp_result=csp_res
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 100)
        # Check standard PDF file header
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()


