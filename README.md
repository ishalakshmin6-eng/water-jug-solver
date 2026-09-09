# Water Jug Problem Solver - State Space Search

[![Python Standard Library](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dependencies: Zero](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-brightgreen.svg)]()
[![Tests: Passing](https://img.shields.io/badge/Tests-7%20Passed-brightgreen.svg)]()

A modular, production-ready implementation of the **Water Jug Problem** using classical **State-Space Search** paradigms in Artificial Intelligence. This project models the problem domain formally and provides implementations of both **Breadth-First Search (BFS)** for guaranteed path optimality and **Depth-First Search (DFS)** for deep exploratory search.

---

## 📌 Student & Course Metadata
* **Student Register Number**: `113025148034`
* **Deterministic Random Seed**: `148034` (`int("113025148034"[-6:])`)
* **Framework / Dependencies**: Python Standard Library only (`argparse`, `collections`, `random`, `math`, `time`, `typing`, `unittest`)

---

## 📁 Repository Structure

The project strictly adheres to the following production directory structure:

```text
water-jug-solver/
├── src/                  # Python source code (models, solver, CLI entrypoint)
│   ├── __init__.py       # Package definition
│   ├── models.py         # State, TransitionStep, SearchResult data types
│   ├── solver.py         # WaterJugProblem class, transition rules, BFS & DFS
│   └── main.py           # Main CLI entry point and terminal reporting
├── tests/                # Automated unit tests using Python's unittest
│   ├── __init__.py       # Test package definition
│   └── test_solver.py    # Test cases for BFS/DFS optimality, validity, and edge cases
├── docs/                 # Project documentation and visual artifacts
│   ├── report.md         # Comprehensive academic report
│   └── screenshots/      # Directory placeholder for output screenshots
│       └── .gitkeep
├── README.md             # Project documentation and execution instructions
├── requirements.txt      # Python dependencies (Standard library only)
├── .gitignore            # Standard Python environment and artifact ignores
└── LICENSE               # Standard MIT License
```

---

## 🧠 Theoretical Formulation & Transition Model

The search problem is formally defined as:
$$\mathcal{P} = \langle \mathcal{S}, s_0, \mathcal{A}(s), \mathcal{T}(s, a), \mathcal{G}(s) \rangle$$

### 1. State Space ($\mathcal{S}$)
A state is an ordered 2-tuple $(J_A, J_B)$ denoting the water in Jug A and Jug B:
$$\mathcal{S} = \{ (a, b) \in \mathbb{Z}^2 \mid 0 \le a \le C_A \text{ and } 0 \le b \le C_B \}$$

### 2. Initial State ($s_0$) & Goal Condition ($\mathcal{G}(s)$)
* Initial state: $s_0 = (0, 0)$
* Goal state: $\mathcal{G}(s) \iff (s_A = T) \lor (s_B = T)$

### 3. State Transition Operators ($\mathcal{A}(s) \to \mathcal{T}(s, a)$)

| # | Action Name | Precondition | State Transition $(a, b) \to (a', b')$ | Description |
|---|-------------|--------------|----------------------------------------|-------------|
| 1 | `Fill Jug A` | $a < C_A$ | $(C_A, b)$ | Fill Jug A to maximum capacity |
| 2 | `Fill Jug B` | $b < C_B$ | $(a, C_B)$ | Fill Jug B to maximum capacity |
| 3 | `Empty Jug A` | $a > 0$ | $(0, b)$ | Empty all water from Jug A onto the ground |
| 4 | `Empty Jug B` | $b > 0$ | $(a, 0)$ | Empty all water from Jug B onto the ground |
| 5 | `Pour Jug A -> Jug B` | $a > 0 \land b < C_B$ | $(a - \Delta, b + \Delta)$, where $\Delta = \min(a, C_B - b)$ | Pour water from A to B until B is full or A is empty |
| 6 | `Pour Jug B -> Jug A` | $b > 0 \land a < C_A$ | $(a + \Delta, b - \Delta)$, where $\Delta = \min(b, C_A - a)$ | Pour water from B to A until A is full or B is empty |

### 4. Mathematical Solvability (Bézout's Identity)
A configuration $\langle C_A, C_B, T \rangle$ is mathematically solvable if and only if:
1. $T \le \max(C_A, C_B)$
2. $T \equiv 0 \pmod{\gcd(C_A, C_B)}$

By **Bézout's Identity**, any reachable water volume represents a linear combination $C_A \cdot x + C_B \cdot y = T$. If $T$ is not divisible by $\gcd(C_A, C_B)$, no valid sequence of operations exists.

---

## 🔍 Search Algorithms

| Characteristic | Breadth-First Search (BFS) | Depth-First Search (DFS) |
|---|---|---|
| **Frontier Structure** | FIFO Queue (`collections.deque`) | LIFO Stack (`list`) |
| **Path Optimality** | **Guaranteed Optimal** (Shortest path in unit-cost search) | **Non-Optimal** (First path discovered) |
| **Completeness** | Complete in finite graphs | Complete in finite graphs (with visited set) |
| **Time Complexity** | $\mathcal{O}(b^d)$ | $\mathcal{O}(b^m)$ |
| **Space Complexity** | $\mathcal{O}(b^d)$ | $\mathcal{O}(b \cdot m)$ |

---

## 🚀 Execution Guide

### Prerequisites
* Python **3.8+** installed.
* Zero external pip packages needed (standard library only).

### 1. Running the Default Benchmark ($C_A = 4\text{L}, C_B = 3\text{L}, T = 2\text{L}$)
Run directly as a script:
```bash
python src/main.py
```
Or execute as a Python module:
```bash
python -m src.main
```

### 2. Command-Line Options
Custom capacities and target values can be passed via CLI flags:

```bash
# Custom capacities with Breadth-First Search
python src/main.py --cap_a 5 --cap_b 3 --target 4 --algorithm bfs

# Comparative analysis comparing BFS vs DFS side-by-side
python src/main.py --cap_a 5 --cap_b 3 --target 4 --algorithm both

# Mathematical unsolvability demonstration
python src/main.py --cap_a 6 --cap_b 4 --target 5

# Display help documentation
python src/main.py --help
```

### 3. Running Automated Unit Tests
Execute the test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📊 Sample Execution Output

```text
==================================================================================
   WATER JUG PROBLEM SOLVER - STATE SPACE SEARCH
   University Project | Artificial Intelligence & Search Algorithms
==================================================================================
 * Student Register Number : 113025148034
 * Deterministic Seed      : 148034 (seed = int(reg_no[-6:]))
 * Random Module Status    : Seeded & Deterministic
==================================================================================

[1] PROBLEM CONFIGURATION & MATHEMATICAL VERIFICATION
----------------------------------------------------------------------------------
 * Jug A Capacity : 4 Liters
 * Jug B Capacity : 3 Liters
 * Target Volume  : 2 Liters (in either Jug A or Jug B)
 * Initial State  : Jug A = 0L, Jug B = 0L -> (0, 0)
 * Solvability    : YES (Solvable)
 * Analysis       : Solvable: Target (2L) <= max capacity and is divisible by GCD(4, 3) = 1.
----------------------------------------------------------------------------------

[>] ALGORITHM: Breadth-First Search (BFS)
==================================================================================
 [+] Solution Discovered! Total Transitions: 4 step(s)
----------------------------------------------------------------------------------
Step   | Action                 | State (A, B)     | Operation Detail                
----------------------------------------------------------------------------------
0      | Initial State          | (0L, 0L)  [0/4L, 0/3L] | Starting configuration          
1      | Fill Jug B             | (0L, 3L)  [0/4L, 3/3L] | Fill Jug B to full capacity (3L)
2      | Pour Jug B -> Jug A    | (3L, 0L)  [3/4L, 0/3L] | Pour 3L from Jug B into Jug A   
3      | Fill Jug B             | (3L, 3L)  [3/4L, 3/3L] | Fill Jug B to full capacity (3L)
4      | Pour Jug B -> Jug A    | (4L, 2L)  [4/4L, 2/3L] | Pour 1L from Jug B into Jug A   
----------------------------------------------------------------------------------
 PERMISSION & PERFORMANCE METRICS:
  * Optimal / Shortest Path : YES (Guaranteed by BFS)
  * Path Length (Cost)      : 4 actions
  * Nodes Explored          : 8
  * Max Frontier Size       : 3
  * Execution Time          : 0.0449 ms
==================================================================================
```

---

## 📚 Academic References
1. **Russell, S., & Norvig, P.** (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. (Chapter 3: Solving Problems by Searching).
2. **Korf, R. E.** (1985). *Depth-first iterative-deepening: An optimal admissible tree search*. Artificial Intelligence, 27(1), 97–109.
3. **Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.** (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. (Chapter 22: Elementary Graph Algorithms).
4. **Bézout, É.** (1779). *Théorie générale des équations algébriques*. Ph.-D. Pierres, Paris.
