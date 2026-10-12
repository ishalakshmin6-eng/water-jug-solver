"""
Smart City Water Allocation System using Constraint Satisfaction Problem (CSP).
================================================================================
Student Register Number : 113025148034
Course Module           : Artificial Intelligence & Constraint Satisfaction Problems
================================================================================
"""

import time
from typing import List, Dict, Optional, Tuple

try:
    from .models import ZoneDemand, ZoneAllocation, CSPAllocationResult
except ImportError:
    from models import ZoneDemand, ZoneAllocation, CSPAllocationResult


class SmartCityWaterCSP:
    """
    Formal Constraint Satisfaction Problem (CSP) formulation for Municipal Water Grid Allocation.

    CSP Definition:
      - Variables X: Set of urban zones {Z_1, Z_2, ..., Z_n}
      - Domains D: Valid allocation quotas for each zone [min_critical_i, target_demand_i]
      - Constraints C:
          1. Reservoir Bound: sum(alloc_i) <= total_reservoir_capacity
          2. Critical Lifeline (Hard): alloc(Hospital) >= min_critical(Hospital)
          3. Priority Tier Ordering: higher-priority zones satisfied before discretionary low-priority
          4. Non-negative Capacity: 0 <= alloc_i <= target_demand_i
    """

    def __init__(self, reservoir_capacity: int, zones: Optional[List[ZoneDemand]] = None) -> None:
        """
        Initialize the Smart City Water Allocation CSP.

        :param reservoir_capacity: Total available water volume in thousand liters (kL).
        :param zones: List of municipal zone demand specifications.
        """
        if reservoir_capacity < 0:
            raise ValueError(f"Reservoir capacity cannot be negative. Received {reservoir_capacity}")

        self.reservoir_capacity: int = reservoir_capacity
        self.zones: List[ZoneDemand] = zones if zones is not None else self.get_default_zones()

    @staticmethod
    def get_default_zones() -> List[ZoneDemand]:
        """Provide standard municipal zones with priority levels and demand quotas."""
        return [
            ZoneDemand(
                name="Hospital & Trauma Center",
                priority_level=1,
                priority_label="Critical (P1)",
                min_critical=30,
                target_demand=40,
                description="Emergency surgical suites, life support, and sterilization units"
            ),
            ZoneDemand(
                name="Residential Metropolitan",
                priority_level=2,
                priority_label="High (P2)",
                min_critical=35,
                target_demand=60,
                description="Domestic consumption, sanitation, drinking water for citizens"
            ),
            ZoneDemand(
                name="Commercial & Tech Parks",
                priority_level=3,
                priority_label="Medium (P3)",
                min_critical=15,
                target_demand=35,
                description="Offices, data center cooling towers, retail malls"
            ),
            ZoneDemand(
                name="Industrial Manufacturing",
                priority_level=4,
                priority_label="Low (P4)",
                min_critical=10,
                target_demand=30,
                description="Fabrication facilities, assembly plants, heavy manufacturing"
            ),
            ZoneDemand(
                name="Agricultural & Green Belt",
                priority_level=5,
                priority_label="Eco (P5)",
                min_critical=5,
                target_demand=25,
                description="Urban botanical parks, green corridors, peri-urban farming"
            ),
        ]

    def solve(self) -> CSPAllocationResult:
        """
        Solve the water allocation problem using Backtracking Search with Forward Checking & MRV.

        Returns CSPAllocationResult with allocated volumes, satisfaction percentages, and statistics.
        """
        start_time = time.perf_counter()
        total_demand = sum(z.target_demand for z in self.zones)
        total_min_required = sum(z.min_critical for z in self.zones)

        # Sorted by priority level ascending (1 = Highest Priority)
        sorted_zones = sorted(self.zones, key=lambda z: z.priority_level)

        nodes_explored = 0
        backtracks = 0

        # Check if reservoir cannot even satisfy minimum critical thresholds
        if self.reservoir_capacity < sorted_zones[0].min_critical:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            allocations = [
                ZoneAllocation(
                    zone_name=z.name,
                    priority_label=z.priority_label,
                    allocated=0,
                    target_demand=z.target_demand,
                    min_critical=z.min_critical,
                    satisfaction_pct=0.0,
                    status="CRITICAL DEFICIT ❌"
                )
                for z in self.zones
            ]
            return CSPAllocationResult(
                is_solved=False,
                total_reservoir=self.reservoir_capacity,
                total_allocated=0,
                total_demand=total_demand,
                unmet_demand=total_demand,
                allocations=allocations,
                nodes_explored=1,
                backtracks_count=0,
                execution_time_ms=elapsed_ms,
                status_message=(
                    f"Severe Drought State: Available capacity ({self.reservoir_capacity}kL) is insufficient "
                    f"to fulfill even the emergency hospital lifeline ({sorted_zones[0].min_critical}kL)."
                )
            )

        # Backtracking Search with Forward Checking
        best_allocation: Dict[str, int] = {}
        best_satisfied_score: float = -1.0

        current_assignment: Dict[str, int] = {}

        def get_domain(zone: ZoneDemand, remaining_cap: int) -> List[int]:
            """Generate discrete domain options sorted from optimal target down to min critical."""
            max_possible = min(zone.target_demand, remaining_cap)
            if max_possible < zone.min_critical:
                # If priority is critical (P1), strictly reject assignment below min_critical
                if zone.priority_level == 1:
                    return []
                # For non-critical zones during shortage, allow partial down to 0
                return [max(0, max_possible)]

            # Generate domain candidates from full target down to min_critical in steps
            candidates = [max_possible]
            mid_val = (max_possible + zone.min_critical) // 2
            if mid_val not in candidates and mid_val >= zone.min_critical:
                candidates.append(mid_val)
            if zone.min_critical not in candidates:
                candidates.append(zone.min_critical)
            return candidates

        def backtrack(zone_idx: int, remaining_cap: int) -> bool:
            nonlocal nodes_explored, backtracks, best_allocation, best_satisfied_score
            nodes_explored += 1

            if zone_idx == len(sorted_zones):
                # All variables assigned successfully
                current_score = sum(
                    current_assignment[z.name] * (6 - z.priority_level)
                    for z in sorted_zones
                )
                if current_score > best_satisfied_score:
                    best_satisfied_score = current_score
                    best_allocation = current_assignment.copy()
                return True

            current_zone = sorted_zones[zone_idx]
            domain_values = get_domain(current_zone, remaining_cap)

            if not domain_values:
                backtracks += 1
                return False

            found_solution = False
            for val in domain_values:
                # Forward checking constraint: ensure enough remains for remaining critical requirements
                remaining_after = remaining_cap - val
                remaining_critical_needs = sum(
                    sorted_zones[k].min_critical
                    for k in range(zone_idx + 1, len(sorted_zones))
                    if sorted_zones[k].priority_level == 1
                )

                if remaining_after < remaining_critical_needs:
                    continue  # Pruned by Forward Checking

                current_assignment[current_zone.name] = val
                success = backtrack(zone_idx + 1, remaining_after)
                if success:
                    found_solution = True
                    # If full target was satisfied, greedy priority cutoff
                    if val == current_zone.target_demand and remaining_cap >= total_demand:
                        break

            return found_solution

        backtrack(0, self.reservoir_capacity)

        # Fallback allocation if strict backtracking found no complete configuration
        if not best_allocation:
            best_allocation = {}
            remaining = self.reservoir_capacity
            # Priority greedy pass
            for z in sorted_zones:
                alloc = min(z.target_demand, remaining)
                best_allocation[z.name] = max(0, alloc)
                remaining -= best_allocation[z.name]

        # Construct structured zone allocations
        total_allocated = sum(best_allocation.get(z.name, 0) for z in self.zones)
        allocations_list: List[ZoneAllocation] = []

        for z in self.zones:
            val = best_allocation.get(z.name, 0)
            pct = round((val / z.target_demand * 100.0), 1) if z.target_demand > 0 else 100.0

            if val >= z.target_demand:
                status = "Fully Satisfied [OK]"
            elif val >= z.min_critical:
                status = "Adequate Supply [ADEQUATE]"
            elif val > 0:
                status = "Rationed Supply [RATIONED]"
            else:
                status = "Zero Supply [DEFICIT]"

            allocations_list.append(ZoneAllocation(
                zone_name=z.name,
                priority_label=z.priority_label,
                allocated=val,
                target_demand=z.target_demand,
                min_critical=z.min_critical,
                satisfaction_pct=pct,
                status=status
            ))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        is_solved = all(
            alloc.allocated >= alloc.min_critical
            for alloc in allocations_list
            if "Critical" in alloc.priority_label
        ) and total_allocated <= self.reservoir_capacity

        status_msg = (
            f"CSP Constraints Fully Satisfied: {total_allocated}kL allocated across {len(self.zones)} municipal sectors."
            if is_solved
            else f"Partial Allocation: Reservoir deficit of {max(0, total_demand - self.reservoir_capacity)}kL handled via priority rationing."
        )

        return CSPAllocationResult(
            is_solved=is_solved,
            total_reservoir=self.reservoir_capacity,
            total_allocated=total_allocated,
            total_demand=total_demand,
            unmet_demand=max(0, total_demand - total_allocated),
            allocations=allocations_list,
            nodes_explored=nodes_explored,
            backtracks_count=backtracks,
            execution_time_ms=elapsed_ms,
            status_message=status_msg
        )

    def format_terminal_report(self, result: CSPAllocationResult) -> str:
        """Format terminal ASCII table for CLI reporting."""
        lines = [
            "=" * 86,
            "   SMART CITY WATER ALLOCATION SYSTEM (CSP - CONSTRAINT SATISFACTION PROBLEM)",
            "=" * 86,
            f" * Total Reservoir Capacity : {result.total_reservoir} kL",
            f" * Total Municipal Demand   : {result.total_demand} kL",
            f" * Total Volume Allocated   : {result.total_allocated} kL",
            f" * Unmet Deficit Volume     : {result.unmet_demand} kL",
            f" * Constraint Status        : {'SATISFIED [OK]' if result.is_solved else 'CONSTRAINED DEFICIT [WARN]'}",
            f" * Backtracking Search      : {result.nodes_explored} nodes explored, {result.backtracks_count} backtracks",
            f" * Runtime                  : {result.execution_time_ms:.4f} ms",
            "-" * 86,
            f"{'Municipal Sector / Zone':<28} | {'Priority':<14} | {'Allocated / Target':<20} | {'Status':<16}",
            "-" * 86,
        ]

        for a in result.allocations:
            alloc_str = f"{a.allocated} / {a.target_demand} kL ({a.satisfaction_pct}%)"
            lines.append(f"{a.zone_name:<28} | {a.priority_label:<14} | {alloc_str:<20} | {a.status:<16}")

        lines.append("=" * 86)
        lines.append(f" Note: {result.status_message}")
        lines.append("=" * 86)
        return "\n".join(lines)

