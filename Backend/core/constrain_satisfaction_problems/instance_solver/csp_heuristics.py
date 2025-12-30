from __future__ import annotations

from typing import List, Tuple

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_constraints import neighbors, pair_ok
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import Assignment, Domains, JsonDict


def select_unassigned_var(
    variables: List[str],
    order: List[str],
    domains: Domains,
    assignment: Assignment,
    heuristic: str,
) -> str:
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