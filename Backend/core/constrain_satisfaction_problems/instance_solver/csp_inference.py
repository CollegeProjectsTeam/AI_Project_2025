from __future__ import annotations

from typing import List, Optional, Tuple

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_constraints import neighbors, pair_ok
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import Assignment, Domains, JsonDict


def forward_check(
    domains: Domains,
    constraints: List[JsonDict],
    assignment: Assignment,
    *,
    last_assigned_vars: List[str],
) -> Tuple[bool, int]:
    pruned = 0
    for var in last_assigned_vars:
        if var not in assignment:
            continue
        val = assignment[var]
        for n in neighbors(var, constraints):
            if n in assignment:
                continue
            before = list(domains[n])
            kept = [nv for nv in before if pair_ok(var, val, n, nv, constraints)]
            if len(kept) != len(before):
                pruned += (len(before) - len(kept))
                domains[n] = kept
            if not domains[n]:
                return False, pruned
    return True, pruned


def ac3(
    domains: Domains,
    constraints: List[JsonDict],
    *,
    queue: Optional[List[Tuple[str, str]]] = None,
) -> Tuple[bool, int]:
    pruned = 0
    q = queue[:] if queue is not None else all_arcs(constraints)

    while q:
        x, y = q.pop(0)
        changed, removed = revise(domains, constraints, x, y)
        pruned += removed
        if changed:
            if not domains[x]:
                return False, pruned
            for z in neighbors(x, constraints):
                if z != y:
                    q.append((z, x))
    return True, pruned


def revise(domains: Domains, constraints: List[JsonDict], x: str, y: str) -> Tuple[bool, int]:
    removed = 0
    new_dx = []
    for xv in domains[x]:
        ok = False
        for yv in domains[y]:
            if pair_ok(x, xv, y, yv, constraints):
                ok = True
                break
        if ok:
            new_dx.append(xv)
        else:
            removed += 1

    if removed > 0:
        domains[x] = new_dx
        return True, removed
    return False, 0


def all_arcs(constraints: List[JsonDict]) -> List[Tuple[str, str]]:
    arcs: List[Tuple[str, str]] = []
    for c in constraints:
        a, b = c["vars"]
        arcs.append((a, b))
        arcs.append((b, a))
    return arcs


def arcs_touching(vars_: List[str], constraints: List[JsonDict]) -> List[Tuple[str, str]]:
    s = set(vars_)
    arcs: List[Tuple[str, str]] = []
    for c in constraints:
        a, b = c["vars"]
        if a in s or b in s:
            arcs.append((a, b))
            arcs.append((b, a))
    return arcs