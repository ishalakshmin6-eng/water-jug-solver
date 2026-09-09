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

from src.models import State, TransitionStep, SearchResult
from src.solver import WaterJugProblem


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


if __name__ == "__main__":
    unittest.main()
