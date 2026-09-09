# Water Jug Problem Solver - State Space Search

[![Streamlit App](https://img.shields.io/badge/Web%20App-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Python Standard Library](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests: Passing](https://img.shields.io/badge/Tests-7%20Passed-brightgreen.svg)]()

A modular, production-ready implementation of the **Water Jug Problem** using classical **State-Space Search** paradigms in Artificial Intelligence. This project models the problem domain formally and provides:
1. **Interactive Streamlit Web Application**: An animated localhost web dashboard with interactive jug visualization, step sliders, and side-by-side algorithm comparison.
2. **Terminal CLI & Modular Engine**: Command-line solver with both **Breadth-First Search (BFS)** for guaranteed path optimality and **Depth-First Search (DFS)**.
3. **Automated Unit Tests**: Standard `unittest` suite covering algorithms and Diophantine solvability proofs.

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
│   ├── __init__.py       # Package definition
│   ├── app.py            # Interactive Streamlit Web Application
│   ├── models.py         # State, TransitionStep, SearchResult data types
│   ├── solver.py         # WaterJugProblem class, transition rules, BFS & DFS
│   └── main.py           # CLI runner and terminal reporting
├── tests/                # Automated unit tests using Python's unittest
│   ├── __init__.py       # Test package definition
│   └── test_solver.py    # Test cases for BFS/DFS optimality, validity, and edge cases
├── docs/                 # Project documentation and visual artifacts
│   ├── report.md         # Comprehensive academic report
│   └── screenshots/      # Directory placeholder for output screenshots
│       └── .gitkeep
├── README.md             # Project documentation and execution instructions
├── requirements.txt      # Python dependencies (Streamlit)
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
streamlit run src/app.py
```
Then open `http://localhost:8501` in your browser.

### Web UI Features:
- **Interactive Sidebar**: Input custom Jug A, Jug B, and Target capacities, or pick quick presets.
- **Algorithm Selector**: Switch between BFS, DFS, or side-by-side Comparative Analysis.
- **Full State Transition Table**: Displays step numbers, actions taken, state vectors $(A, B)$, fill fractions, and descriptions.
- **Dynamic Step Replay & Visualizer**: Animated beaker graphics showing real-time water levels for each step.
- **Student ID Banner**: Displays Register Number `113025148034` prominently in the header.

---

## 💻 CLI Terminal Execution

You can also run the solver directly in your command line:

```bash
# Default benchmark (4L, 3L -> 2L using BFS)
python src/main.py

# Run comparative analysis (BFS vs DFS)
python src/main.py --cap_a 5 --cap_b 3 --target 4 --algorithm both

# Mathematical unsolvability test
python src/main.py --cap_a 6 --cap_b 4 --target 5

# CLI options help
python src/main.py --help
```

---

## 🧪 Running Automated Unit Tests

Run the complete test suite using Python's standard `unittest` framework:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 🧠 Theoretical Formulation & Transition Model

The search problem is formally defined as:
$$\mathcal{P} = \langle \mathcal{S}, s_0, \mathcal{A}(s), \mathcal{T}(s, a), \mathcal{G}(s) \rangle$$

### 1. State Space ($\mathcal{S}$)
A state is an ordered 2-tuple $(J_A, J_B)$ denoting the water in Jug A and Jug B:
$$\mathcal{S} = \{ (a, b) \in \mathbb{Z}^2 \mid 0 \le a \le C_A \text{ and } 0 \le b \le C_B \}$$

### 2. Transition Operators ($\mathcal{A}(s) \to \mathcal{T}(s, a)$)

| # | Action Name | Precondition | State Transition $(a, b) \to (a', b')$ | Description |
|---|-------------|--------------|----------------------------------------|-------------|
| 1 | `Fill Jug A` | $a < C_A$ | $(C_A, b)$ | Fill Jug A to maximum capacity |
| 2 | `Fill Jug B` | $b < C_B$ | $(a, C_B)$ | Fill Jug B to maximum capacity |
| 3 | `Empty Jug A` | $a > 0$ | $(0, b)$ | Empty all water from Jug A |
| 4 | `Empty Jug B` | $b > 0$ | $(a, 0)$ | Empty all water from Jug B |
| 5 | `Pour Jug A -> Jug B` | $a > 0 \land b < C_B$ | $(a - \Delta, b + \Delta)$, where $\Delta = \min(a, C_B - b)$ | Pour water from A to B until B is full or A is empty |
| 6 | `Pour Jug B -> Jug A` | $b > 0 \land a < C_A$ | $(a + \Delta, b - \Delta)$, where $\Delta = \min(b, C_A - a)$ | Pour water from B to A until A is full or B is empty |

### 3. Mathematical Solvability (Bézout's Identity)
A configuration $\langle C_A, C_B, T \rangle$ is mathematically solvable if and only if:
1. $T \le \max(C_A, C_B)$
2. $T \equiv 0 \pmod{\gcd(C_A, C_B)}$

---

## 📚 Academic References
1. **Russell, S., & Norvig, P.** (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. (Chapter 3: Solving Problems by Searching).
2. **Korf, R. E.** (1985). *Depth-first iterative-deepening: An optimal admissible tree search*. Artificial Intelligence, 27(1), 97–109.
3. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. (Chapter 22: Elementary Graph Algorithms).
4. **Bézout, É.** (1779). *Théorie générale des équations algébriques*. Ph.-D. Pierres, Paris.
