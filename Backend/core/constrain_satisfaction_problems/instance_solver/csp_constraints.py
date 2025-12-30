from __future__ import annotations

from typing import List, Set

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import Assignment, JsonDict


ALLOWED_CONSTRAINTS = {"neq", "lt", "gt"}


def neighbors(var: str, constraints: List[JsonDict]) -> List[str]:
    out: Set[str] = set()
    for c in constraints:
        a, b = c["vars"]
        if a == var:
            out.add(b)
        elif b == var:
            out.add(a)
    return list(out)


def satisfies(ctype: str, a: int, b: int) -> bool:
    if ctype == "neq":
        return a != b
    if ctype == "lt":
        return a < b
    if ctype == "gt":
        return a > b
    raise ValueError(f"unknown constraint type: {ctype}")


def is_consistent_partial(assignment: Assignment, constraints: List[JsonDict]) -> bool:
    for c in constraints:
        a, b = c["vars"]
        if a in assignment and b in assignment:
            if not satisfies(c["type"], assignment[a], assignment[b]):
                return False
    return True


def is_consistent_with(var: str, val: int, assignment: Assignment, constraints: List[JsonDict]) -> bool:
    for c in constraints:
        a, b = c["vars"]
        if a == var and b in assignment:
            if not satisfies(c["type"], val, assignment[b]):
                return False
        if b == var and a in assignment:
            if not satisfies(c["type"], assignment[a], val):
                return False
    return True


def pair_ok(x: str, xv: int, y: str, yv: int, constraints: List[JsonDict]) -> bool:
    for c in constraints:
        a, b = c["vars"]
        if a == x and b == y:
            if not satisfies(c["type"], xv, yv):
                return False
        if a == y and b == x:
            if not satisfies(c["type"], yv, xv):
                return False
    return True