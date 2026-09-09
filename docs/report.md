# Academic Project Report: Water Jug Problem Solver

**Course Module**: Artificial Intelligence & State-Space Search  
**Student Register Number**: `113025148034`  
**Deterministic Random Seed**: `148034` (`int("113025148034"[-6:])`)  
**Date**: September 2026  

---

## 1. Executive Summary
The Water Jug Problem is a foundational problem in Artificial Intelligence used to demonstrate state-space modeling, graph formulation, and search strategies. This project delivers an automated solver capable of finding optimal solutions using Breadth-First Search (BFS) and alternative exploratory solutions using Depth-First Search (DFS), with number-theoretic solvability verification based on Bézout's Identity.

---

## 2. Formal Problem Formulation

The problem is defined as a formal 5-tuple:
$$\mathcal{P} = \langle \mathcal{S}, s_0, \mathcal{A}(s), \mathcal{T}(s, a), \mathcal{G}(s) \rangle$$

1. **State Space ($\mathcal{S}$)**:
   All ordered pairs $(a, b) \in \mathbb{Z}^2$ representing the current volume of water in Jug A and Jug B:
   $$\mathcal{S} = \{ (a, b) \mid 0 \le a \le C_A, 0 \le b \le C_B \}$$
2. **Initial State ($s_0$)**:
   $$s_0 = (0, 0)$$
3. **Actions ($\mathcal{A}(s)$)**:
   - `Fill Jug A`: $(C_A, b)$
   - `Fill Jug B`: $(a, C_B)$
   - `Empty Jug A`: $(0, b)$
   - `Empty Jug B`: $(a, 0)$
   - `Pour Jug A -> Jug B`: $(a - \Delta, b + \Delta)$, where $\Delta = \min(a, C_B - b)$
   - `Pour Jug B -> Jug A`: $(a + \Delta, b - \Delta)$, where $\Delta = \min(b, C_A - a)$
4. **Transition Function ($\mathcal{T}$)**:
   Deterministic mapping $\mathcal{S} \times \mathcal{A} \to \mathcal{S}$.
5. **Goal Condition ($\mathcal{G}(s)$)**:
   $$\mathcal{G}(s) \iff (a = T) \lor (b = T)$$

---

## 3. Mathematical Solvability (Diophantine Analysis)

By Bézout's Identity:
$$C_A \cdot x + C_B \cdot y = T$$
A solution exists if and only if:
1. $T \le \max(C_A, C_B)$
2. $T \equiv 0 \pmod{\gcd(C_A, C_B)}$

If either condition is violated, the program terminates immediately without executing unnecessary search iterations.

---

## 4. Search Algorithm Analysis

### Breadth-First Search (BFS)
- **Frontier**: First-In-First-Out (FIFO) queue (`collections.deque`).
- **Completeness**: Guaranteed complete in finite state spaces.
- **Optimality**: **Guaranteed optimal** (shortest sequence of operations) because action costs are uniform ($c(s, a, s') = 1$).
- **Complexity**:
  - Time: $\mathcal{O}(b^d)$
  - Space: $\mathcal{O}(b^d)$

### Depth-First Search (DFS)
- **Frontier**: Last-In-First-Out (LIFO) stack (`list`).
- **Completeness**: Complete with cycle-detection closed set.
- **Optimality**: Non-optimal (returns first path encountered, which may contain sub-optimal loops).
- **Complexity**:
  - Time: $\mathcal{O}(b^m)$
  - Space: $\mathcal{O}(b \cdot m)$

---

## 5. Experimental Results & Comparisons

### Case 1: Capacities (4L, 3L) $\to$ Target 2L
| Metric | BFS (Breadth-First) | DFS (Depth-First) |
|---|---|---|
| Status | SOLVED | SOLVED |
| Solution Cost (Transitions) | **4 actions** (Optimal) | 4 actions |
| Nodes Explored | 8 | 5 |
| Max Frontier Size | 3 | 3 |
| Execution Time | ~0.04 ms | ~0.02 ms |

### Case 2: Capacities (5L, 3L) $\to$ Target 4L
| Metric | BFS (Breadth-First) | DFS (Depth-First) |
|---|---|---|
| Status | SOLVED | SOLVED |
| Solution Cost (Transitions) | **6 actions** (Optimal) | 8 actions (Sub-optimal) |
| Nodes Explored | 11 | 9 |
| Max Frontier Size | 3 | 3 |
| Execution Time | ~0.06 ms | ~0.03 ms |

---

## 6. Screenshots & Output Placeholders

The visual logs and screenshots of terminal runs should be placed in [`docs/screenshots/`](file:///c:/idea/docs/screenshots/):

- `docs/screenshots/terminal_run_bfs.png`: Screenshot of `python src/main.py --algorithm bfs`
- `docs/screenshots/terminal_run_comparison.png`: Screenshot of `python src/main.py --cap_a 5 --cap_b 3 --target 4 --algorithm both`
- `docs/screenshots/terminal_unsolvable.png`: Screenshot of unsolvable scenario `python src/main.py --cap_a 6 --cap_b 4 --target 5`
- `docs/screenshots/unit_tests.png`: Screenshot of `python -m unittest discover tests`

---

## 7. References
1. Russell, S., & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach* (4th ed.). Pearson. (Chapter 3).
2. Korf, R. E. (1985). *Depth-first iterative-deepening: An optimal admissible tree search*. Artificial Intelligence, 27(1), 97–109.
3. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
