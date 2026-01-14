from __future__ import annotations

from typing import List, Tuple

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_constraints import neighbors, pair_ok
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import Assignment, Domains, JsonDict

"""
csp_heuristics.py

Variable and value heuristics used by the CSP solver.

Provided heuristics:
- select_unassigned_var():
    * FIXED: choose first unassigned variable in `order`
    * MRV: choose variable with Minimum Remaining Values (smallest domain),
           with tie-break by `order`
- order_values():
    * NONE: keep domain order as-is
    * LCV: Least Constraining Value (minimize eliminations in neighbors' domains)
"""

def select_unassigned_var(
    variables: List[str],
    order: List[str],
    domains: Domains,
    assignment: Assignment,
    heuristic: str,
) -> str:
    """
       Select the next unassigned variable.

       Args:
           variables: All variables (source of truth for membership).
           order: Preferred variable ordering used by FIXED and as MRV tie-break.
           domains: Current domains (used by MRV).
           assignment: Current partial assignment.
           heuristic: Name of heuristic ("MRV" or "FIXED"/other).

       Returns:
           The chosen variable name.

       Notes:
           - If heuristic is MRV, chooses smallest domain variable, tie-break by `order`.
           - Otherwise chooses the first unassigned variable according to `order`.
       """
    unassigned = [v for v in variables if v not in assignment]

    if heuristic.upper() == "MRV":
        return min(
            unassigned,
            key=lambda v: (len(domains[v]), order.index(v) if v in order else 10**9),
        )

    for v in order:
        if v not in assignment:
            return v

    return unassigned[0]


def order_values(
    var: str,
    domains: Domains,
    constraints: List[JsonDict],
    assignment: Assignment,
    heuristic: str,
) -> List[int]:
    """
       Order the candidate values for a variable.

       Args:
           var: Variable to assign.
           domains: Current domains.
           constraints: Binary constraints list.
           assignment: Current partial assignment.
           heuristic: Name of heuristic ("LCV" or "NONE"/other).

       Returns:
           List of values in the order they should be tried.

       Notes:
           LCV scoring counts how many neighbor values would be eliminated if `var = val`.
           Lower elimination count is better (try first).
       """
    vals = list(domains[var])
    if heuristic.upper() != "LCV":
        return vals

    neigh = neighbors(var, constraints)
    scored: List[Tuple[int, int]] = []
    for val in vals:
        eliminated = 0
        for n in neigh:
            if n in assignment:
                continue
            for nv in domains[n]:
                if not pair_ok(var, val, n, nv, constraints):
                    eliminated += 1
        scored.append((eliminated, val))

    scored.sort(key=lambda t: (t[0], t[1]))
    return [v for _, v in scored]