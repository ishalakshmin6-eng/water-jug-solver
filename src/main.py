"""
Water Jug Problem Solver - State Space Search
================================================================================
Student Register Number : 113025148034
Course Module           : Artificial Intelligence & State-Space Search
Deterministic Seed      : 148034 (int("113025148034"[-6:]))
================================================================================

Main entry point and CLI runner for the Water Jug Problem Solver.
"""

import argparse
import os
import random
import sys

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Ensure proper path resolution whether executed as module or script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from src.models import State, TransitionStep, SearchResult, CSPAllocationResult
    from src.solver import (
        WaterJugProblem,
        export_solution_csv,
        export_solution_json,
        export_solution_pdf,
    )
    from src.csp_solver import SmartCityWaterCSP
except ImportError:
    from models import State, TransitionStep, SearchResult, CSPAllocationResult
    from solver import (
        WaterJugProblem,
        export_solution_csv,
        export_solution_json,
        export_solution_pdf,
    )
    from csp_solver import SmartCityWaterCSP


# ==============================================================================
# Student Identification & Deterministic Seeding Ground Rules
# ==============================================================================
STUDENT_REG_NO: str = "113025148034"
DETERMINISTIC_SEED: int = int(STUDENT_REG_NO[-6:])  # Extracts 148034

random.seed(DETERMINISTIC_SEED)


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
    parser.add_argument(
        "--export_dot",
        type=str,
        default=None,
        help="Optional output filepath to export the state-space graph as a Graphviz DOT file."
    )
    parser.add_argument(
        "--export_csv",
        type=str,
        default=None,
        help="Optional output filepath to export solution path as CSV (e.g., solution.csv)."
    )
    parser.add_argument(
        "--export_json",
        type=str,
        default=None,
        help="Optional output filepath to export problem and search metrics as JSON (e.g., report.json)."
    )
    parser.add_argument(
        "--export_pdf",
        type=str,
        default=None,
        help="Optional output filepath to export comprehensive report as PDF (e.g., report.pdf)."
    )
    parser.add_argument(
        "--smart_city_csp",
        action="store_true",
        help="Run Smart City Water Allocation CSP alongside the water jug solver."
    )
    parser.add_argument(
        "--reservoir_cap",
        type=int,
        default=150,
        help="Total municipal reservoir volume in kL for Smart City CSP (default: 150 kL)."
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
    active_result: SearchResult = None
    bfs_res: Optional[SearchResult] = None
    dfs_res: Optional[SearchResult] = None

    if args.algorithm == "bfs":
        bfs_res = problem.solve_bfs()
        render_search_result(problem, bfs_res)
        active_result = bfs_res

    elif args.algorithm == "dfs":
        dfs_res = problem.solve_dfs()
        render_search_result(problem, dfs_res)
        active_result = dfs_res

    elif args.algorithm == "both":
        bfs_res = problem.solve_bfs()
        dfs_res = problem.solve_dfs()
        render_search_result(problem, bfs_res)
        render_search_result(problem, dfs_res)
        render_comparison_summary(bfs_res, dfs_res)
        active_result = bfs_res

    # Smart City CSP Allocation Run if requested
    csp_result: Optional[CSPAllocationResult] = None
    if args.smart_city_csp:
        csp_solver = SmartCityWaterCSP(reservoir_capacity=args.reservoir_cap)
        csp_result = csp_solver.solve()
        print("\n" + csp_solver.format_terminal_report(csp_result))

    # Export Graphviz DOT file if requested
    if args.export_dot:
        sol_path = active_result.path if (active_result and active_result.is_solved) else None
        graph = problem.get_state_space_graph(solution_path=sol_path)
        dot_content = problem.generate_dot_graph(graph, title="Water Jug State-Space Graph")
        try:
            with open(args.export_dot, "w", encoding="utf-8") as f:
                f.write(dot_content)
            print(f"\n[+] STATE-SPACE GRAPH EXPORTED: {os.path.abspath(args.export_dot)}")
        except OSError as err:
            print(f"\n[ERROR] Failed to write DOT file '{args.export_dot}': {err}", file=sys.stderr)

    # Export CSV file if requested
    if args.export_csv and active_result and active_result.is_solved:
        csv_content = export_solution_csv(problem, active_result)
        try:
            with open(args.export_csv, "w", encoding="utf-8", newline="") as f:
                f.write(csv_content)
            print(f"[+] CSV TRANSITION LEDGER EXPORTED: {os.path.abspath(args.export_csv)}")
        except OSError as err:
            print(f"[ERROR] Failed to write CSV file '{args.export_csv}': {err}", file=sys.stderr)

    # Export JSON file if requested
    if args.export_json:
        json_content = export_solution_json(
            problem,
            bfs_result=bfs_res,
            dfs_result=dfs_res,
            student_reg_no=STUDENT_REG_NO,
            seed=DETERMINISTIC_SEED,
            csp_result=csp_result
        )
        try:
            with open(args.export_json, "w", encoding="utf-8") as f:
                f.write(json_content)
            print(f"[+] STRUCTURED JSON REPORT EXPORTED: {os.path.abspath(args.export_json)}")
        except OSError as err:
            print(f"[ERROR] Failed to write JSON file '{args.export_json}': {err}", file=sys.stderr)

    # Export PDF report if requested
    if args.export_pdf:
        pdf_bytes = export_solution_pdf(
            problem,
            bfs_result=bfs_res,
            dfs_result=dfs_res,
            student_reg_no=STUDENT_REG_NO,
            seed=DETERMINISTIC_SEED,
            csp_result=csp_result
        )
        try:
            with open(args.export_pdf, "wb") as f:
                f.write(pdf_bytes)
            print(f"[+] ACADEMIC PDF REPORT EXPORTED: {os.path.abspath(args.export_pdf)}")
        except OSError as err:
            print(f"[ERROR] Failed to write PDF file '{args.export_pdf}': {err}", file=sys.stderr)


if __name__ == "__main__":

    main()

