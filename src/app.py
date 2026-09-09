import streamlit as st
import os
import sys
import random
import time

# Ensure project root and src directory are in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

try:
    from src.models import State, TransitionStep, SearchResult
    from src.solver import WaterJugProblem
except ImportError:
    from models import State, TransitionStep, SearchResult
    from solver import WaterJugProblem

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
    page_title=f"Water Jug Solver | Reg: {STUDENT_REG_NO}",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for rich aesthetics and animated water jugs
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 50%, #0d9488 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(14, 165, 233, 0.3);
    }
    
    .student-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.5px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .stat-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
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
        background: rgba(241, 245, 249, 0.6);
        overflow: hidden;
        box-shadow: inset 0 0 15px rgba(0,0,0,0.05);
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
        text-shadow: 0 1px 2px rgba(0,0,0,0.4);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Helper Functions
# ==============================================================================
def render_jug_visual(name: str, current: int, capacity: int, color_grad: str = "#0284c7") -> str:
    """Generate HTML snippet for an animated water jug."""
    pct = int((current / capacity) * 100) if capacity > 0 else 0
    pct = max(0, min(100, pct))
    return f"""
    <div class="jug-container">
        <div style="font-weight: 700; font-size: 1.1rem; color: #1e293b; margin-bottom: 6px;">{name}</div>
        <div class="jug-glass">
            <div class="jug-water" style="height: {pct}%; background: linear-gradient(180deg, #38bdf8 0%, {color_grad} 100%);">
                {current}L ({pct}%)
            </div>
        </div>
        <div style="margin-top: 8px; font-weight: 600; color: #64748b; font-size: 0.9rem;">
            {current} / {capacity} Liters
        </div>
    </div>
    """


# ==============================================================================
# Header Banner
# ==============================================================================
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <h1 style="margin: 0; font-size: 2.1rem; font-weight: 700; color: white;">💧 Water Jug Problem Solver</h1>
            <p style="margin: 4px 0 0 0; opacity: 0.9; font-size: 1.05rem;">State-Space Search with Breadth-First & Depth-First Algorithms</p>
        </div>
        <div style="text-align: right;">
            <div class="student-badge">🎓 Student Reg No: {STUDENT_REG_NO}</div>
            <div style="font-size: 0.8rem; margin-top: 6px; opacity: 0.85;">Deterministic Seed: <code>{DETERMINISTIC_SEED}</code></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# Sidebar - Inputs and Configuration
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Problem Configuration")
    
    st.markdown("Configure the jug capacities and desired target volume below:")
    
    col_a, col_b = st.columns(2)
    with col_a:
        cap_a = st.number_input("Jug A Capacity (L)", min_value=1, max_value=50, value=4, step=1)
    with col_b:
        cap_b = st.number_input("Jug B Capacity (L)", min_value=1, max_value=50, value=3, step=1)
        
    target = st.number_input("Target Volume (L)", min_value=1, max_value=50, value=2, step=1)
    
    st.markdown("---")
    st.header("🧠 Search Strategy")
    algo_selection = st.radio(
        "Select Algorithm",
        [
            "Breadth-First Search (BFS) [Optimal]",
            "Depth-First Search (DFS)",
            "Both (Comparative Analysis)"
        ],
        index=0
    )
    
    st.markdown("---")
    # Quick preset benchmarks
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

    solve_button = st.button("🚀 Solve Problem", type="primary", use_container_width=True)

    st.markdown("---")
    st.caption(f"**University Project** | Register Number: `{STUDENT_REG_NO}`")


# ==============================================================================
# Core Execution & Presentation Logic
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
    st.info("According to **Bézout's Identity**, any reachable amount must be a multiple of the greatest common divisor $\\gcd(C_A, C_B)$ and cannot exceed $\\max(C_A, C_B)$.")
else:
    st.success(f"✅ **Mathematically Solvable**: {reason}")

# Main Solver Action
if solve_button or "last_solved" in st.session_state:
    st.session_state["last_solved"] = True

    if not is_solvable:
        st.warning("Cannot run search on an unsolvable configuration.")
        st.stop()

    # Determine algorithms to run
    run_bfs = "Breadth-First" in algo_selection or "Both" in algo_selection
    run_dfs = "Depth-First" in algo_selection or "Both" in algo_selection

    bfs_result = problem.solve_bfs() if run_bfs else None
    dfs_result = problem.solve_dfs() if run_dfs else None

    # Tab views for comprehensive insights
    tab_solution, tab_visualizer, tab_theory = st.tabs([
        "📋 Step-by-Step Transition Table",
        "🎬 Interactive Step Visualizer",
        "📖 Search Theory & Formulation"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: Step-by-Step Transition Table
    # --------------------------------------------------------------------------
    with tab_solution:
        if run_bfs and not run_dfs:
            res = bfs_result
        elif run_dfs and not run_bfs:
            res = dfs_result
        else:
            res = bfs_result  # Default to BFS for single view, then show comparison

        st.subheader(f"Search Results: {res.algorithm_name}")

        # Metrics cards
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.metric("Status", "Solved ✅" if res.is_solved else "Failed ❌")
        with m2:
            st.metric("Total Steps", f"{len(res.path) - 1} actions")
        with m3:
            st.metric("Optimality", "Optimal (Shortest)" if "BFS" in res.algorithm_name else "Non-Optimal")
        with m4:
            st.metric("Nodes Explored", f"{res.nodes_explored}")
        with m5:
            st.metric("Execution Time", f"{res.execution_time_ms:.3f} ms")

        # Table display
        if res.is_solved:
            st.markdown("#### State Transitions Leading to Target Volume")
            table_data = []
            for step in res.path:
                table_data.append({
                    "Step": step.step_number,
                    "Action": step.action_name,
                    "State (A, B)": f"({step.state[0]}L, {step.state[1]}L)",
                    "Jug A Fill": f"{step.state[0]} / {problem.cap_a} L",
                    "Jug B Fill": f"{step.state[1]} / {problem.cap_b} L",
                    "Operation Details": step.description
                })
            st.dataframe(table_data, use_container_width=True, hide_index=True)

        # If both selected, also show comparison
        if run_bfs and run_dfs:
            st.markdown("---")
            st.subheader("⚖️ Comparative Evaluation: BFS vs. DFS")
            
            comp_data = [
                {
                    "Metric": "Status",
                    "BFS (Breadth-First)": "SOLVED ✅" if bfs_result.is_solved else "FAILED ❌",
                    "DFS (Depth-First)": "SOLVED ✅" if dfs_result.is_solved else "FAILED ❌",
                },
                {
                    "Metric": "Solution Steps (Transitions)",
                    "BFS (Breadth-First)": f"{len(bfs_result.path) - 1} actions",
                    "DFS (Depth-First)": f"{len(dfs_result.path) - 1} actions",
                },
                {
                    "Metric": "Path Optimality",
                    "BFS (Breadth-First)": "Optimal (Shortest Path)",
                    "DFS (Depth-First)": "Non-Optimal (First Encountered)",
                },
                {
                    "Metric": "Nodes Explored",
                    "BFS (Breadth-First)": f"{bfs_result.nodes_explored}",
                    "DFS (Depth-First)": f"{dfs_result.nodes_explored}",
                },
                {
                    "Metric": "Max Frontier Size",
                    "BFS (Breadth-First)": f"{bfs_result.max_frontier_size}",
                    "DFS (Depth-First)": f"{dfs_result.max_frontier_size}",
                },
                {
                    "Metric": "Execution Time",
                    "BFS (Breadth-First)": f"{bfs_result.execution_time_ms:.4f} ms",
                    "DFS (Depth-First)": f"{dfs_result.execution_time_ms:.4f} ms",
                }
            ]
            st.dataframe(comp_data, use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # TAB 2: Interactive Step Visualizer
    # --------------------------------------------------------------------------
    with tab_visualizer:
        active_res = bfs_result if bfs_result is not None else dfs_result
        if active_res and active_res.is_solved:
            st.subheader("🎬 Dynamic Step Replay")
            st.markdown("Use the slider below to step through each action and observe the water levels change dynamically:")
            
            max_step = len(active_res.path) - 1
            selected_step = st.slider("Select Step Number", min_value=0, max_value=max_step, value=0, step=1)
            
            curr_step_obj = active_res.path[selected_step]
            
            st.markdown(f"### Step {curr_step_obj.step_number}: **{curr_step_obj.action_name}**")
            st.info(f"💡 {curr_step_obj.description}")
            
            # Render Jugs side-by-side
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
                st.success(f"🎯 Target volume of {problem.target}L reached!")

    # --------------------------------------------------------------------------
    # TAB 3: Theoretical Formulation & Bézout's Identity
    # --------------------------------------------------------------------------
    with tab_theory:
        st.subheader("🧠 State-Space Search Formalization")
        st.markdown(r"""
        The problem is formally defined by the AI search 5-tuple $\langle \mathcal{S}, s_0, \mathcal{A}(s), \mathcal{T}(s, a), \mathcal{G}(s) \rangle$:

        1. **State Space ($\mathcal{S}$)**:
           $$\mathcal{S} = \{ (a, b) \in \mathbb{Z}^2 \mid 0 \le a \le C_A, 0 \le b \le C_B \}$$
        2. **Initial State ($s_0$)**: $s_0 = (0, 0)$
        3. **Goal Test ($\mathcal{G}(s)$)**: $a = T \lor b = T$
        4. **Actions ($\mathcal{A}(s)$)**:
           - $\text{Fill}(A)$, $\text{Fill}(B)$
           - $\text{Empty}(A)$, $\text{Empty}(B)$
           - $\text{Pour}(A \to B)$, $\text{Pour}(B \to A)$
        5. **Mathematical Solvability**:
           A target $T$ can be measured if and only if $T \le \max(C_A, C_B)$ and $T \equiv 0 \pmod{\gcd(C_A, C_B)}$.
        """)
        st.markdown(f"""
        ---
        **Student Information**:
        - Student Register Number: `{STUDENT_REG_NO}`
        - Deterministic Seed: `{DETERMINISTIC_SEED}`
        - Course: *Artificial Intelligence & Search Algorithms*
        """)
else:
    st.info("👈 Set your parameters in the left sidebar and click **'🚀 Solve Problem'** to begin.")
