from __future__ import annotations

from typing import List, Optional, Tuple

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_constraints import neighbors, pair_ok
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import Assignment, Domains, JsonDict

"""
csp_inference.py

Inference and consistency algorithms for binary-constraint CSPs.

Provided algorithms:
- forward_check(): Forward Checking (FC) from recently assigned variables
- ac3(): AC-3 arc consistency algorithm
- revise(): arc revision primitive used by AC-3
- all_arcs(): build full queue of arcs from constraints
- arcs_touching(): build queue of arcs incident to a subset of variables

All functions mutate `domains` in-place and return:
- ok: whether domains remain non-empty (no domain wipe-out)
- pruned: how many domain values were removed
"""


def forward_check(
    domains: Domains,
    constraints: List[JsonDict],
    assignment: Assignment,
    *,
    last_assigned_vars: List[str],
) -> Tuple[bool, int]:
    """
      Perform Forward Checking propagation from recently assigned variables.

      For each assigned variable X in `last_assigned_vars`, prune each unassigned
      neighbor Y by removing values y in D(Y) that conflict with X's assigned value.

      Args:
          domains: Current domains (mutated in-place).
          constraints: Binary constraints list.
          assignment: Current partial assignment.
          last_assigned_vars: Variables to propagate from (typically the last chosen var,
              or all vars from an initial partial assignment).

      Returns:
          (ok, pruned) where:
          - ok is False iff some domain becomes empty (domain wipe-out)
          - pruned is the number of removed values across all pruned domains
      """

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
    """
      Enforce arc consistency using the AC-3 algorithm.

      AC-3 processes arcs (X, Y). If revising X w.r.t. Y removes values from D(X),
      then arcs (Z, X) for neighbors Z of X are re-added (except the current Y).

      Args:
          domains: Current domains (mutated in-place).
          constraints: Binary constraints list.
          queue: Optional initial queue of arcs. If None, uses all arcs in constraints.

      Returns:
          (ok, pruned) where:
          - ok is False iff some domain becomes empty (domain wipe-out)
          - pruned is the number of removed values across all revisions
      """

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
    """
     Revise the domain of x to be consistent with y.

     Removes any value xv in D(x) for which there is no supporting yv in D(y)
     that satisfies the constraints between x and y.

     Args:
         domains: Current domains (mutated in-place if changes occur).
         constraints: Binary constraints list.
         x: Source variable.
         y: Target variable.

     Returns:
         (changed, removed) where:
         - changed is True iff at least one value was removed from D(x)
         - removed is the number of removed values
     """

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
    """
       Build the full set of directed arcs implied by constraints.

       For each constraint (A, B) add arcs (A, B) and (B, A).

       Args:
           constraints: Binary constraints list.

       Returns:
           List of directed arcs (x, y).
       """

    arcs: List[Tuple[str, str]] = []
    for c in constraints:
        a, b = c["vars"]
        arcs.append((a, b))
        arcs.append((b, a))
    return arcs


def arcs_touching(vars_: List[str], constraints: List[JsonDict]) -> List[Tuple[str, str]]:
    """
    Build directed arcs for constraints incident to any variable in `vars_`.

    Useful for MAC: after assigning variable X, enforce AC-3 only on arcs that
    may be affected by X (instead of running AC-3 on the whole graph).

    Args:
        vars_: Variables considered "touched" (recently assigned).
        constraints: Binary constraints list.

    Returns:
        List of directed arcs (a, b) and (b, a) for each incident constraint.
    """

    s = set(vars_)
    arcs: List[Tuple[str, str]] = []
    for c in constraints:
        a, b = c["vars"]
        if a in s or b in s:
            arcs.append((a, b))
            arcs.append((b, a))
    return arcs