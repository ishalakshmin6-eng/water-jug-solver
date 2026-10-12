import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import random
import time
from typing import Optional

# Ensure project root and src directory are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from src.models import (
        State,
        TransitionStep,
        SearchResult,
        GraphNode,
        GraphEdge,
        StateSpaceGraph,
        ZoneDemand,
        ZoneAllocation,
        CSPAllocationResult,
    )
    from src.solver import (
        WaterJugProblem,
        export_solution_csv,
        export_solution_json,
        export_solution_pdf,
    )
    from src.csp_solver import SmartCityWaterCSP
except ImportError:
    from models import (
        State,
        TransitionStep,
        SearchResult,
        GraphNode,
        GraphEdge,
        StateSpaceGraph,
        ZoneDemand,
        ZoneAllocation,
        CSPAllocationResult,
    )
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
# Page Configuration & Styling
# ==============================================================================
st.set_page_config(
    page_title=f"Water Jug Solver & Smart City Grid | {STUDENT_REG_NO}",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics, glassmorphism, and animated jugs
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #0369a1 45%, #0d9488 100%);
        padding: 26px 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -5px rgba(2, 132, 199, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .student-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(10px);
        padding: 6px 16px;
        border-radius: 24px;
        font-weight: 700;
        font-size: 0.92rem;
        letter-spacing: 0.5px;
        border: 1px solid rgba(255, 255, 255, 0.35);
    }
    
    .step-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 3px 8px -2px rgba(0, 0, 0, 0.05);
        transition: all 0.25s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
    }
    
    .step-card:hover {
        border-color: #0284c7;
        box-shadow: 0 8px 18px -4px rgba(2, 132, 199, 0.15);
        transform: translateY(-2px);
    }
    
    .action-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        background: #f0f9ff;
        border: 1px solid #bae6fd;
    }
    
    .state-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f1f5f9;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.88rem;
        color: #1e293b;
        border: 1px solid #cbd5e1;
    }
    
    .delta-badge {
        background: #e0f2fe;
        color: #0369a1;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 10px;
    }

    .jug-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin: 10px;
    }
    
    .jug-glass {
        width: 140px;
        height: 220px;
        border: 4px solid #334155;
        border-top: none;
        border-radius: 0 0 20px 20px;
        position: relative;
        background: rgba(241, 245, 249, 0.7);
        overflow: hidden;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.06);
    }
    
    .jug-water {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, #38bdf8 0%, #0284c7 100%);
        transition: height 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }

    .csp-zone-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Helper Functions
# ==============================================================================
def get_action_icon(action_name: str) -> str:
    """Return an expressive emoji icon based on the state transition action."""
    if "Fill" in action_name:
        return "💧"
    elif "Pour" in action_name:
        return "🫗"
    elif "Empty" in action_name:
        return "🗑️"
    elif "Initial" in action_name:
        return "🚩"
    return "🔄"


def render_jug_visual(name: str, current: int, capacity: int, color_grad: str = "#0284c7") -> str:
    """Generate HTML snippet for an animated water jug beaker."""
    pct = int((current / capacity) * 100) if capacity > 0 else 0
    pct = max(0, min(100, pct))
    return f"""
    <div class="jug-container">
        <div style="font-weight: 700; font-size: 1.15rem; color: #1e293b; margin-bottom: 8px;">{name}</div>
        <div class="jug-glass">
            <div class="jug-water" style="height: {pct}%; background: linear-gradient(180deg, #38bdf8 0%, {color_grad} 100%);">
                {current}L ({pct}%)
            </div>
        </div>
        <div style="margin-top: 10px; font-weight: 600; color: #475569; font-size: 0.92rem;">
            {current} / {capacity} Liters ({pct}% Full)
        </div>
    </div>
    """


# ==============================================================================
# Header Banner
# ==============================================================================
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div>
            <h1 style="margin: 0; font-size: 2.2rem; font-weight: 800; color: white;">💧 Water Jug Solver & Smart City Grid</h1>
            <p style="margin: 6px 0 0 0; opacity: 0.92; font-size: 1.05rem;">
                Classical State-Space Search (BFS & DFS) + Municipal Water Allocation via Constraint Satisfaction (CSP)
            </p>
        </div>
        <div style="text-align: right;">
            <div class="student-badge">🎓 Student Reg No: {STUDENT_REG_NO}</div>
            <div style="font-size: 0.82rem; margin-top: 6px; opacity: 0.88;">Deterministic Seed: <code>{DETERMINISTIC_SEED}</code></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# Sidebar - Inputs and Configuration
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Problem Configuration")
    st.markdown("Set jug capacities and target volume:")

    col_a, col_b = st.columns(2)
    with col_a:
        cap_a = st.number_input("Jug A (L)", min_value=1, max_value=60, value=4, step=1)
    with col_b:
        cap_b = st.number_input("Jug B (L)", min_value=1, max_value=60, value=3, step=1)

    target = st.number_input("Target Volume (L)", min_value=1, max_value=60, value=2, step=1)

    st.markdown("---")
    st.header("🧠 Search Strategy")
    algo_selection = st.radio(
        "Select Search Strategy",
        [
            "Breadth-First Search (BFS) [Optimal]",
            "Depth-First Search (DFS)",
            "Both (Comparative Analysis)"
        ],
        index=2
    )

    st.markdown("---")
    st.subheader("📌 Benchmark Presets")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("Classic (4, 3 → 2)", use_container_width=True):
            st.session_state["cap_a"] = 4
            st.session_state["cap_b"] = 3
            st.session_state["target"] = 2
            st.rerun()
    with col_p2:
        if st.button("Puzzle (5, 3 → 4)", use_container_width=True):
            st.session_state["cap_a"] = 5
            st.session_state["cap_b"] = 3
            st.session_state["target"] = 4
            st.rerun()

    solve_button = st.button("🚀 Run Solver & Analysis", type="primary", use_container_width=True)
    st.markdown("---")
    st.caption(f"**University AI Project** | Register Number: `{STUDENT_REG_NO}`")


# ==============================================================================
# Core Execution & Mathematical Solvability Verification
# ==============================================================================
try:
    problem = WaterJugProblem(cap_a=int(cap_a), cap_b=int(cap_b), target=int(target))
    is_solvable, reason = problem.is_solvable()
except ValueError as err:
    st.error(f"Input Error: {err}")
    st.stop()

# Solvability Alert Banner
if not is_solvable:
    st.error(f"⚠️ **Mathematically Unsolvable**: {reason}")
    st.info("By **Bézout's Identity**, any measurable amount must be a multiple of $\\gcd(C_A, C_B)$ and cannot exceed $\\max(C_A, C_B)$.")
else:
    st.success(f"✅ **Mathematically Solvable**: {reason}")

# Run search solvers
run_bfs = "Breadth-First" in algo_selection or "Both" in algo_selection
run_dfs = "Depth-First" in algo_selection or "Both" in algo_selection

bfs_result = problem.solve_bfs() if (run_bfs and is_solvable) else None
dfs_result = problem.solve_dfs() if (run_dfs and is_solvable) else None
primary_res = bfs_result if (bfs_result and bfs_result.is_solved) else dfs_result

# Initialize CSP default run
default_csp = SmartCityWaterCSP(reservoir_capacity=150)
csp_result_cached = default_csp.solve()


# ==============================================================================
# Navigation Tabs (7 Comprehensive Tabs)
# ==============================================================================
tab_steps, tab_replay, tab_compare, tab_graph, tab_csp, tab_exports, tab_theory = st.tabs([
    "📋 Step-by-Step Transition Cards",
    "🎬 Dynamic Step Replay",
    "⚖️ Comparative Analysis (BFS vs DFS)",
    "🕸️ State-Space Graph & Search Tree",
    "🏙️ Smart City Water Allocation (CSP)",
    "📥 Multi-Format Reports & Export",
    "📖 AI Search & CSP Formal Theory"
])


# ------------------------------------------------------------------------------
# TAB 1: Step-by-Step Transition Cards
# ------------------------------------------------------------------------------
with tab_steps:
    if primary_res and primary_res.is_solved:
        st.subheader(f"Step-by-Step Solution Path: {primary_res.algorithm_name}")
        st.markdown(f"Discovered goal state in **{len(primary_res.path) - 1} transitions** with **{primary_res.nodes_explored} nodes explored**.")

        # KPI Summary row
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("Total Steps", f"{len(primary_res.path) - 1} actions")
        with s2:
            st.metric("Optimality", "Optimal (Shortest)" if "BFS" in primary_res.algorithm_name else "Non-Optimal")
        with s3:
            st.metric("Nodes Explored", f"{primary_res.nodes_explored}")
        with s4:
            st.metric("Runtime", f"{primary_res.execution_time_ms:.3f} ms")

        # Step cards
        st.markdown("#### Transition Sequence Cards")
        for i, step in enumerate(primary_res.path):
            prev = primary_res.path[i - 1] if i > 0 else None
            icon = get_action_icon(step.action_name)

            delta_a = f"{step.state[0] - prev.state[0]:+d}L" if prev else "+0L"
            delta_b = f"{step.state[1] - prev.state[1]:+d}L" if prev else "+0L"

            st.markdown(f"""
            <div class="step-card">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div class="action-icon">{icon}</div>
                    <div>
                        <div style="font-weight: 700; font-size: 1.05rem; color: #0f172a;">
                            Step {step.step_number}: {step.action_name}
                        </div>
                        <div style="font-size: 0.88rem; color: #64748b; margin-top: 2px;">
                            {step.description}
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <div class="state-badge">
                        <span>Jug A: <strong>{step.state[0]}/{problem.cap_a}L</strong></span>
                        <span class="delta-badge">{delta_a}</span>
                    </div>
                    <div class="state-badge">
                        <span>Jug B: <strong>{step.state[1]}/{problem.cap_b}L</strong></span>
                        <span class="delta-badge">{delta_b}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Full Dataframe View
        with st.expander("📊 View Complete Raw Transition Dataframe", expanded=False):
            table_data = [
                {
                    "Step": s.step_number,
                    "Action": s.action_name,
                    "State (A, B)": f"({s.state[0]}L, {s.state[1]}L)",
                    "Jug A Fill": f"{s.state[0]} / {problem.cap_a} L",
                    "Jug B Fill": f"{s.state[1]} / {problem.cap_b} L",
                    "Description": s.description
                }
                for s in primary_res.path
            ]
            st.dataframe(table_data, use_container_width=True, hide_index=True)
    else:
        st.info("Run search to view transition steps.")


# ------------------------------------------------------------------------------
# TAB 2: Dynamic Step Replay
# ------------------------------------------------------------------------------
with tab_replay:
    if primary_res and primary_res.is_solved:
        st.subheader("🎬 Dynamic Step Replay & Interactive Beakers")
        st.markdown("Use the slider below to step through each action and observe the water levels change dynamically:")

        max_step = len(primary_res.path) - 1
        selected_step = st.slider("Select Step Number", min_value=0, max_value=max_step, value=0, step=1)
        curr_step_obj = primary_res.path[selected_step]

        st.markdown(f"### Step {curr_step_obj.step_number}: **{curr_step_obj.action_name}**")
        st.info(f"💡 {curr_step_obj.description}")

        jug_col1, jug_col2 = st.columns(2)
        with jug_col1:
            st.markdown(
                render_jug_visual("Jug A", curr_step_obj.state[0], problem.cap_a, "#0284c7"),
                unsafe_allow_html=True
            )
        with jug_col2:
            st.markdown(
                render_jug_visual("Jug B", curr_step_obj.state[1], problem.cap_b, "#0d9488"),
                unsafe_allow_html=True
            )

        if curr_step_obj.state[0] == problem.target or curr_step_obj.state[1] == problem.target:
            st.balloons()
            st.success(f"🎯 Target volume of {problem.target}L reached in state ({curr_step_obj.state[0]}L, {curr_step_obj.state[1]}L)!")
    else:
        st.info("Run search to replay steps.")


# ------------------------------------------------------------------------------
# TAB 3: Comparative Analysis (BFS vs DFS)
# ------------------------------------------------------------------------------
with tab_compare:
    st.subheader("⚖️ Comparative Evaluation: BFS vs. DFS")
    st.markdown(
        "Side-by-side empirical performance comparison evaluating **optimality**, "
        "**exploration breadth**, **frontier memory consumption**, and **execution time**."
    )

    if bfs_result and dfs_result:
        comp_data = [
            {
                "Evaluation Dimension": "Problem Solved Status",
                "BFS (Breadth-First)": "SOLVED ✅" if bfs_result.is_solved else "FAILED ❌",
                "DFS (Depth-First)": "SOLVED ✅" if dfs_result.is_solved else "FAILED ❌",
            },
            {
                "Evaluation Dimension": "Solution Cost (Transitions)",
                "BFS (Breadth-First)": f"{len(bfs_result.path) - 1} actions",
                "DFS (Depth-First)": f"{len(dfs_result.path) - 1} actions",
            },
            {
                "Evaluation Dimension": "Path Optimality Guarantee",
                "BFS (Breadth-First)": "Guaranteed Optimal (Shortest Path)",
                "DFS (Depth-First)": "Non-Optimal (First Found)",
            },
            {
                "Evaluation Dimension": "Nodes Explored",
                "BFS (Breadth-First)": f"{bfs_result.nodes_explored} states",
                "DFS (Depth-First)": f"{dfs_result.nodes_explored} states",
            },
            {
                "Evaluation Dimension": "Max Frontier Size (Memory)",
                "BFS (Breadth-First)": f"{bfs_result.max_frontier_size} queue items",
                "DFS (Depth-First)": f"{dfs_result.max_frontier_size} stack items",
            },
            {
                "Evaluation Dimension": "Execution Runtime",
                "BFS (Breadth-First)": f"{bfs_result.execution_time_ms:.4f} ms",
                "DFS (Depth-First)": f"{dfs_result.execution_time_ms:.4f} ms",
            }
        ]
        st.dataframe(comp_data, use_container_width=True, hide_index=True)

        # Comparative visual columns
        st.markdown("#### Empirical Efficiency Summary")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "Solution Actions (Cost)",
                f"BFS: {len(bfs_result.path) - 1}",
                delta=f"-{len(dfs_result.path) - len(bfs_result.path)} steps vs DFS" if len(dfs_result.path) >= len(bfs_result.path) else "Same",
                delta_color="normal"
            )
        with c2:
            st.metric(
                "Exploration Footprint",
                f"BFS: {bfs_result.nodes_explored} nodes",
                delta=f"{bfs_result.nodes_explored - dfs_result.nodes_explored} nodes vs DFS",
                delta_color="off"
            )
        with c3:
            st.metric(
                "Execution Runtime",
                f"BFS: {bfs_result.execution_time_ms:.3f} ms",
                delta=f"{bfs_result.execution_time_ms - dfs_result.execution_time_ms:+.3f} ms vs DFS",
                delta_color="off"
            )
    else:
        st.info("Select **'Both (Comparative Analysis)'** in the sidebar to enable full side-by-side evaluation.")


# ------------------------------------------------------------------------------
# TAB 4: State-Space Graph & Search Tree
# ------------------------------------------------------------------------------
with tab_graph:
    st.subheader("🕸️ State-Space Graph & Search Tree Visualizer")
    st.markdown(
        "Interactive graphical representation of the Water Jug state space. "
        "Switch between the **Interactive Physics Network (Vis.js)** and the **Structured Graphviz Diagram (DOT)**."
    )

    active_path = primary_res.path if primary_res else []

    cfg_col1, cfg_col2, cfg_col3 = st.columns([1.2, 1.2, 1.0])
    with cfg_col1:
        viz_engine = st.radio(
            "Visualization Engine",
            [
                "🌟 Interactive Physics Network (Vis.js)",
                "📊 Structured Graphviz Diagram (DOT)"
            ],
            index=0,
            key="graph_engine_select_main"
        )
    with cfg_col2:
        graph_scope = st.selectbox(
            "Graph Scope & Topology",
            [
                "Full Reachable State-Space Graph",
                "Search Exploration Tree (BFS/DFS Traversal)",
                "Solution Path Only"
            ],
            index=0,
            key="graph_scope_select_main"
        )

    layout_dir = "Top to Bottom (TB)"
    with cfg_col3:
        if "Structured Graphviz" in viz_engine:
            layout_dir = st.selectbox(
                "Layout Flow Direction",
                ["Top to Bottom (TB)", "Left to Right (LR)"],
                index=0,
                key="graph_layout_dir_main"
            )
        else:
            if bfs_result and dfs_result:
                highlight_algo = st.selectbox(
                    "Highlight Solution Algorithm",
                    ["BFS (Optimal)", "DFS"],
                    index=0,
                    key="graph_highlight_algo_main"
                )
                active_path = bfs_result.path if "BFS" in highlight_algo else dfs_result.path

    if "Exploration Tree" in graph_scope:
        chosen_algo = "dfs" if (run_dfs and not run_bfs) else "bfs"
        graph_data = problem.get_search_tree(algorithm=chosen_algo, solution_path=active_path)
        graph_title = f"Search Tree ({chosen_algo.upper()} Traversal)"
    else:
        graph_data = problem.get_state_space_graph(solution_path=active_path)
        graph_title = "Reachable State-Space Graph"

    is_sol_only = "Solution Path Only" in graph_scope

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total Graph Nodes", f"{len(graph_data.nodes)} states")
    with kpi2:
        st.metric("Directed Transitions", f"{len(graph_data.edges)} edges")
    with kpi3:
        st.metric("Solution Path Length", f"{len(active_path) - 1} steps" if active_path else "0")
    with kpi4:
        st.metric("Target Reachable", "YES 🎯" if any(n.is_goal for n in graph_data.nodes) else "NO ❌")

    st.markdown("""
    <div style="display: flex; gap: 16px; flex-wrap: wrap; align-items: center; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 16px; margin: 10px 0 16px 0; font-size: 0.85rem;">
        <div style="font-weight: 700; color: #475569;">Color Legend:</div>
        <div><span style="display:inline-block;width:12px;height:12px;background:#dbeafe;border:2px solid #0284c7;border-radius:3px;margin-right:4px;"></span> <strong>Start (0, 0)</strong></div>
        <div><span style="display:inline-block;width:12px;height:12px;background:#d1fae5;border:2px solid #059669;border-radius:3px;margin-right:4px;"></span> <strong>Goal (🎯)</strong></div>
        <div><span style="display:inline-block;width:12px;height:12px;background:#e0f2fe;border:2px solid #0284c7;border-radius:3px;margin-right:4px;"></span> <strong>Solution Path</strong></div>
        <div><span style="display:inline-block;width:12px;height:12px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:3px;margin-right:4px;"></span> <strong>Reachable State</strong></div>
    </div>
    """, unsafe_allow_html=True)

    if "Interactive Physics" in viz_engine:
        vis_html = problem.generate_visjs_html(graph_data, height=560)
        components.html(vis_html, height=680, scrolling=False)
        st.caption("💡 **Interactive Controls:** Drag nodes to reposition them, scroll to zoom, hover for metadata, or click any node to view real-time jug fill meters.")
    else:
        rankdir_code = "LR" if "Left to Right" in layout_dir else "TB"
        dot_code = problem.generate_dot_graph(
            graph_data,
            title=graph_title,
            rankdir=rankdir_code,
            solution_only=is_sol_only
        )
        st.graphviz_chart(dot_code, use_container_width=True)

        d_col1, _ = st.columns([1, 3])
        with d_col1:
            st.download_button(
                label="📥 Export Graph (.dot)",
                data=dot_code,
                file_name=f"water_jug_{problem.cap_a}L_{problem.cap_b}L_{problem.target}L.dot",
                mime="text/vnd.graphviz",
                use_container_width=True
            )


# ------------------------------------------------------------------------------
# TAB 5: Smart City Water Allocation (CSP)
# ------------------------------------------------------------------------------
with tab_csp:
    st.subheader("🏙️ Smart City Water Allocation System (CSP)")
    st.markdown(
        "Real-world application extending the Water Jug Problem to municipal water grids. "
        "Formulated as a **Constraint Satisfaction Problem (CSP)** with Backtracking Search, "
        "Forward Checking, and Priority Tier Satisfaction."
    )

    csp_col1, csp_col2 = st.columns([1, 2])

    with csp_col1:
        st.markdown("#### 🎛️ Reservoir & Zone Controls")
        reservoir_input = st.slider("Total Reservoir Capacity (kL)", min_value=20, max_value=300, value=150, step=10)

        st.markdown("**Zone Target Demands (kL):**")
        hosp_target = st.slider("🏥 Hospital & Trauma (P1)", 20, 60, 40, 5)
        res_target = st.slider("🏘️ Residential (P2)", 20, 100, 60, 5)
        comm_target = st.slider("🏢 Commercial & Tech (P3)", 10, 60, 35, 5)
        ind_target = st.slider("🏭 Industrial (P4)", 10, 50, 30, 5)
        agri_target = st.slider("🌾 Agricultural Belt (P5)", 5, 40, 25, 5)

        custom_zones = [
            ZoneDemand("Hospital & Trauma Center", 1, "Critical (P1)", 30, hosp_target, "Emergency surgical units and ICU lifeline"),
            ZoneDemand("Residential Metropolitan", 2, "High (P2)", 35, res_target, "Domestic drinking, sanitation, and municipal feed"),
            ZoneDemand("Commercial & Tech Parks", 3, "Medium (P3)", 15, comm_target, "IT offices, retail centers, data cooling"),
            ZoneDemand("Industrial Manufacturing", 4, "Low (P4)", 10, ind_target, "Fabrication and heavy assembly plants"),
            ZoneDemand("Agricultural & Green Belt", 5, "Eco (P5)", 5, agri_target, "Urban green spaces and farming belts"),
        ]

        run_csp_btn = st.button("⚡ Solve Water Allocation CSP", type="primary", use_container_width=True)

    with csp_col2:
        # Solve CSP
        csp_solver_instance = SmartCityWaterCSP(reservoir_capacity=reservoir_input, zones=custom_zones)
        csp_res = csp_solver_instance.solve()

        # Metrics row
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        with m_c1:
            st.metric("Total Reservoir", f"{csp_res.total_reservoir} kL")
        with m_c2:
            st.metric("Total Demand", f"{csp_res.total_demand} kL")
        with m_c3:
            st.metric("Total Allocated", f"{csp_res.total_allocated} kL")
        with m_c4:
            st.metric("Status", "SATISFIED ✅" if csp_res.is_solved else "DEFICIT ⚠️")

        st.info(f"💡 **CSP Engine Status:** {csp_res.status_message} (Solved in {csp_res.execution_time_ms:.3f} ms with {csp_res.nodes_explored} search nodes)")

        # Sector progress bars
        st.markdown("#### District Allocation Breakdown")
        for alloc in csp_res.allocations:
            pct_val = min(100.0, alloc.satisfaction_pct) / 100.0
            st.markdown(f"""
            <div class="csp-zone-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <div>
                        <strong style="font-size: 1.05rem; color: #0f172a;">{alloc.zone_name}</strong>
                        <span style="font-size: 0.8rem; background: #e2e8f0; padding: 2px 8px; border-radius: 10px; margin-left: 8px;">{alloc.priority_label}</span>
                    </div>
                    <div style="font-weight: 700; color: #0284c7;">
                        {alloc.allocated} / {alloc.target_demand} kL ({alloc.satisfaction_pct}%)
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.progress(pct_val)


# ------------------------------------------------------------------------------
# TAB 6: Multi-Format Reports & Export
# ------------------------------------------------------------------------------
with tab_exports:
    st.subheader("📥 Export Solution & Academic Documentation")
    st.markdown("Download full research reports, data tables, and structured payloads in standard formats:")

    if primary_res and primary_res.is_solved:
        # Generate export contents
        csv_data = export_solution_csv(problem, primary_res)
        json_data = export_solution_json(
            problem,
            bfs_result=bfs_result,
            dfs_result=dfs_result,
            student_reg_no=STUDENT_REG_NO,
            seed=DETERMINISTIC_SEED,
            csp_result=csp_res
        )
        pdf_bytes = export_solution_pdf(
            problem,
            bfs_result=bfs_result,
            dfs_result=dfs_result,
            student_reg_no=STUDENT_REG_NO,
            seed=DETERMINISTIC_SEED,
            csp_result=csp_res
        )

        e_col1, e_col2, e_col3 = st.columns(3)

        with e_col1:
            st.markdown("### 📊 CSV Data Ledger")
            st.markdown("Tabular spreadsheet export of step numbers, actions, state vectors $(A, B)$, and fill percentages.")
            st.download_button(
                label="📥 Download Solution CSV",
                data=csv_data,
                file_name=f"water_jug_{problem.cap_a}L_{problem.cap_b}L_{problem.target}L.csv",
                mime="text/csv",
                use_container_width=True
            )

        with e_col2:
            st.markdown("### ⚙️ JSON Data Payload")
            st.markdown("Complete machine-readable technical schema with student metadata, problem configurations, and CSP metrics.")
            st.download_button(
                label="📥 Download Structured JSON",
                data=json_data,
                file_name=f"water_jug_report_{STUDENT_REG_NO}.json",
                mime="application/json",
                use_container_width=True
            )

        with e_col3:
            st.markdown("### 📄 Academic PDF Report")
            st.markdown("Publication-formatted document featuring problem verification, algorithm comparison table, and step ledger.")
            st.download_button(
                label="📥 Download Academic PDF",
                data=pdf_bytes,
                file_name=f"water_jug_report_{STUDENT_REG_NO}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        st.markdown("---")
        st.markdown("#### JSON Payload Preview")
        st.json(json_data[:1200] + "\n  ...\n}")
    else:
        st.warning("Please solve a valid problem configuration to enable report exports.")


# ------------------------------------------------------------------------------
# TAB 7: AI Search & CSP Formal Theory
# ------------------------------------------------------------------------------
with tab_theory:
    st.subheader("📖 Formal Problem Formulation & Theoretical Foundations")
    st.markdown(r"""
    ### 1. Water Jug Search Problem 5-Tuple
    The state-space search problem is formally defined by $\mathcal{P} = \langle \mathcal{S}, s_0, \mathcal{A}(s), \mathcal{T}(s, a), \mathcal{G}(s) \rangle$:

    1. **State Space ($\mathcal{S}$)**:
       $$\mathcal{S} = \{ (a, b) \in \mathbb{Z}^2 \mid 0 \le a \le C_A, 0 \le b \le C_B \}$$
    2. **Initial State ($s_0$)**: $s_0 = (0, 0)$
    3. **Goal Test ($\mathcal{G}(s)$)**: $a = T \lor b = T$
    4. **Action Set ($\mathcal{A}(s)$)**:
       - $\text{Fill}(A): (C_A, b)$, $\text{Fill}(B): (a, C_B)$
       - $\text{Empty}(A): (0, b)$, $\text{Empty}(B): (a, 0)$
       - $\text{Pour}(A \to B): (a - \Delta, b + \Delta)$, where $\Delta = \min(a, C_B - b)$
       - $\text{Pour}(B \to A): (a + \Delta, b - \Delta)$, where $\Delta = \min(b, C_A - a)$
    5. **Number-Theoretic Solvability (Bézout's Identity)**:
       A target volume $T$ can be measured if and only if:
       $$T \le \max(C_A, C_B) \quad \text{and} \quad T \equiv 0 \pmod{\gcd(C_A, C_B)}$$

    ---

    ### 2. Smart City Municipal Water Grid CSP Formulation
    The resource allocation extension is formally defined as a Constraint Satisfaction Problem $\langle \mathcal{X}, \mathcal{D}, \mathcal{C} \rangle$:

    1. **Variables ($\mathcal{X}$)**:
       $$\mathcal{X} = \{ Z_{\text{hospital}}, Z_{\text{residential}}, Z_{\text{commercial}}, Z_{\text{industrial}}, Z_{\text{agricultural}} \}$$
    2. **Domains ($\mathcal{D}_i$)**:
       $$\mathcal{D}_i \subseteq [0, \text{TargetDemand}_i]$$
    3. **Constraints ($\mathcal{C}$)**:
       - **Total Reservoir Bound**: $\sum_{i=1}^n \text{Alloc}(Z_i) \le \text{Reservoir Capacity}$
       - **Hospital Lifeline (Hard)**: $\text{Alloc}(Z_{\text{hospital}}) \ge \text{MinCritical}(Z_{\text{hospital}})$
       - **Priority Tier Hierarchy**: Priority $k$ satisfied before Priority $k+1$ discretionary quota.
    """)

    st.markdown(f"""
    ---
    **Academic Identity & Verification**:
    - **Student Register Number**: `{STUDENT_REG_NO}`
    - **Deterministic Random Seed**: `{DETERMINISTIC_SEED}`
    - **Course Module**: *Artificial Intelligence & Search Algorithms*
    """)
