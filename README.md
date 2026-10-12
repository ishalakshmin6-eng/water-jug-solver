# Water Jug Problem Solver & Smart City Water Grid - AI State-Space Search & CSP

[![Streamlit App](https://img.shields.io/badge/Web%20App-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Python Standard Library](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)]()

A modular, production-ready implementation of the **Water Jug Problem** and a **Smart City Water Allocation System** using classical **State-Space Search** paradigms and **Constraint Satisfaction Problems (CSP)** in Artificial Intelligence.

### 🌟 Key Deliverables:
1. **Interactive Streamlit Web Dashboard**: Modern glassmorphic interface with animated water jug beakers, step-by-step transition cards with volume deltas, side-by-side BFS vs DFS comparative matrix, and full dynamic replay.
2. **Interactive State-Space Graph & Search Tree Visualizer**:
   - **Vis.js Physics Network**: Drag-and-drop nodes, zoom/pan, spring physics controls, live node inspection gauges, and solution-path filter.
   - **Graphviz Hierarchical Diagram**: Structured DAG/Tree layout (TB / LR) with Graphviz `.dot` export.
3. **Smart City Water Allocation System (CSP)**: Multi-sector municipal water distribution solver using Backtracking Search, Forward Checking, and Minimum Remaining Values (MRV) heuristic.
4. **Multi-Format Export Engine**: One-click downloads for **CSV**, **JSON**, and publication-ready **Academic PDF** reports via ReportLab.
5. **Terminal CLI & Modular Engine**: Command-line interface supporting BFS, DFS, DOT/CSV/JSON/PDF exports, and municipal CSP allocation.
6. **Automated Unit Tests**: Standard `unittest` suite with **16 passing unit tests** covering all search algorithms, Diophantine solvability proofs, graph topology, CSP constraints, and export engines.

---

## 📌 Student & Course Metadata
* **Student Register Number**: `113025148034`
* **Deterministic Random Seed**: `148034` (`int("113025148034"[-6:])`)
* **Course**: Artificial Intelligence & Search Algorithms

---

## 📁 Repository Structure

```text
water-jug-solver/
├── src/                  # Python source code
│   ├── __init__.py       # Package definition and public exports
│   ├── app.py            # Modern Streamlit Web Application (7 Comprehensive Tabs)
│   ├── models.py         # Data models (State, TransitionStep, Graph, CSP models)
│   ├── solver.py         # WaterJugProblem class, BFS/DFS, Graphviz DOT & exports
│   ├── csp_solver.py     # Smart City Water Allocation CSP engine (Backtracking + MRV)
│   └── main.py           # CLI runner with multi-format export and CSP reporting
├── tests/                # Automated unit tests using Python's unittest
│   ├── __init__.py       # Test package definition
│   └── test_solver.py    # 16 Unit tests covering BFS, DFS, Graphs, CSP, and Exports
├── docs/                 # Project documentation and visual artifacts
│   ├── report.md         # Comprehensive academic report
│   └── screenshots/      # Directory placeholder for output screenshots
│       └── .gitkeep
├── README.md             # Project documentation and execution instructions
├── requirements.txt      # Python dependencies (Streamlit, Graphviz, ReportLab)
├── .gitignore            # Standard Python environment and artifact ignores
└── LICENSE               # Standard MIT License
```

---

## 🌐 Launching the Streamlit Web Application

To run the interactive web interface locally:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the Streamlit Web Application
python -m streamlit run src/app.py
```
Then open `http://localhost:8501` in your browser.

### Web UI Tabs:
1. **📋 Step-by-Step Transition Cards**: Visual transition cards featuring action icons (💧 Fill, 🫗 Pour, 🗑️ Empty), volume delta badges ($\Delta = \pm x\text{L}$), before/after state badges, and complete tabular ledger.
2. **🎬 Dynamic Step Replay**: Interactive step slider with animated glass beaker graphics showing real-time water levels.
3. **⚖️ Comparative Analysis (BFS vs DFS)**: Side-by-side metric matrix comparing solution cost, optimality guarantee, nodes explored, max frontier memory, and execution runtime.
4. **🕸️ State-Space Graph & Search Tree**: Interactive Vis.js Physics Network (drag/zoom/inspect) and structured Graphviz DAG/tree with `.dot` download button.
5. **🏙️ Smart City Water Allocation (CSP)**: Multi-zone municipal grid allocation dashboard with district demand sliders, priority fulfillment metrics, and satisfaction progress meters.
6. **📥 Multi-Format Reports & Export**: Direct one-click downloads for **CSV**, **JSON**, and formatted **Academic PDF** reports.
7. **📖 AI Search & CSP Formal Theory**: Formal mathematical specifications and proofs.

---

## 💻 CLI Terminal Execution

You can also run the solver directly in your command line:

```bash
# 1. Default benchmark (4L, 3L -> 2L using BFS)
python src/main.py

# 2. Run comparative analysis (BFS vs DFS)
python src/main.py --cap_a 5 --cap_b 3 --target 4 --algorithm both

# 3. Run Smart City Water Allocation CSP alongside search
python src/main.py --cap_a 4 --cap_b 3 --target 2 --smart_city_csp --reservoir_cap 150

# 4. Multi-format exports (DOT, CSV, JSON, PDF)
python src/main.py --cap_a 4 --cap_b 3 --target 2 --export_dot graph.dot --export_csv steps.csv --export_json report.json --export_pdf report.pdf

# 5. Mathematical unsolvability test
python src/main.py --cap_a 6 --cap_b 4 --target 5

# 6. CLI options help
python src/main.py --help
```

---

## 🧪 Running Automated Unit Tests

Run the complete test suite using Python's standard `unittest` framework:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*(All 16 unit tests execute and pass in ~0.24 seconds).*

---

## 🧠 Theoretical Formulation & Transition Model

### 1. Water Jug Search 5-Tuple
The search problem is formally defined as:
$$\mathcal{P} = \langle \mathcal{S}, s_0, \mathcal{A}(s), \mathcal{T}(s, a), \mathcal{G}(s) \rangle$$

- **State Space ($\mathcal{S}$)**: Ordered pairs $(a, b) \in \mathbb{Z}^2$ where $0 \le a \le C_A$ and $0 \le b \le C_B$.
- **Initial State ($s_0$)**: $(0, 0)$
- **Goal Condition ($\mathcal{G}(s)$)**: $a = T \lor b = T$
- **Transition Operators ($\mathcal{A}(s) \to \mathcal{T}(s, a)$)**:
  1. `Fill Jug A`: $(C_A, b)$
  2. `Fill Jug B`: $(a, C_B)$
  3. `Empty Jug A`: $(0, b)$
  4. `Empty Jug B`: $(a, 0)$
  5. `Pour Jug A -> Jug B`: $(a - \Delta, b + \Delta)$, where $\Delta = \min(a, C_B - b)$
  6. `Pour Jug B -> Jug A`: $(a + \Delta, b - \Delta)$, where $\Delta = \min(b, C_A - a)$

### 2. Mathematical Solvability (Bézout's Identity)
A configuration $\langle C_A, C_B, T \rangle$ is mathematically solvable if and only if:
1. $T \le \max(C_A, C_B)$
2. $T \equiv 0 \pmod{\gcd(C_A, C_B)}$

### 3. Smart City Water Allocation CSP Formulation
- **Variables ($\mathcal{X}$)**: $\{ Z_{\text{Hospital}}, Z_{\text{Residential}}, Z_{\text{Commercial}}, Z_{\text{Industrial}}, Z_{\text{Agricultural}} \}$
- **Domains ($\mathcal{D}_i$)**: $[0, \text{TargetDemand}_i]$
- **Constraints ($\mathcal{C}$)**:
  1. $\sum \text{Alloc}(Z_i) \le \text{Reservoir Capacity}$
  2. $\text{Alloc}(Z_{\text{Hospital}}) \ge \text{MinCritical}(Z_{\text{Hospital}})$ (Hard Lifeline)
  3. Priority Ordering: Higher priority zones satisfied before discretionary low-priority quotas.

---

## 📚 Academic References
1. **Russell, S., & Norvig, P.** (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. (Chapter 3: Solving Problems by Searching; Chapter 6: Constraint Satisfaction Problems).
2. **Korf, R. E.** (1985). *Depth-first iterative-deepening: An optimal admissible tree search*. Artificial Intelligence, 27(1), 97–109.
3. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
4. **Bézout, É.** (1779). *Théorie générale des équations algébriques*. Ph.-D. Pierres, Paris.
