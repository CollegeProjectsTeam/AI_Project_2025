from __future__ import annotations

from typing import List, Set

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import Assignment, JsonDict

"""
csp_constraints.py

Constraint primitives for a simple binary-constraint CSP.

Constraint representation:
- Each constraint is a dict: {"type": "neq"|"lt"|"gt", "vars": [A, B]}
- Semantics: type(A, B) must hold on assigned values (e.g., A != B)

Provided utilities:
- neighbors(): adjacency query based on constraint list
- satisfies(): evaluate a single constraint type on two integers
- is_consistent_partial(): check all constraints whose endpoints are assigned
- is_consistent_with(): check whether assigning (var=val) violates any constraint
  against already assigned neighbors
- pair_ok(): check if a pair of values is consistent w.r.t. all constraints between
  two variables (considering both directions in the list)
"""

ALLOWED_CONSTRAINTS = {"neq", "lt", "gt"}


def neighbors(var: str, constraints: List[JsonDict]) -> List[str]:
    """
        Return the neighbor variables of `var` in the constraint graph.

        Args:
            var: Variable name.
            constraints: List of constraint dicts.

        Returns:
            List of variables that appear in a constraint together with `var`.
        """

    out: Set[str] = set()
    for c in constraints:
        a, b = c["vars"]
        if a == var:
            out.add(b)
        elif b == var:
            out.add(a)
    return list(out)


def satisfies(ctype: str, a: int, b: int) -> bool:
    """
       Evaluate a constraint type on two integer values.

       Args:
           ctype: Constraint type ("neq", "lt", "gt").
           a: Left operand.
           b: Right operand.

       Returns:
           True if the relation holds, otherwise False.

       Raises:
           ValueError: If ctype is unknown.
       """

    if ctype == "neq":
        return a != b
    if ctype == "lt":
        return a < b
    if ctype == "gt":
        return a > b
    raise ValueError(f"unknown constraint type: {ctype}")


def is_consistent_partial(assignment: Assignment, constraints: List[JsonDict]) -> bool:
    """
       Check whether a partial assignment violates any fully-instantiated constraint.

       Only constraints whose both variables are assigned are evaluated.

       Args:
           assignment: Current partial assignment.
           constraints: Constraint list.

       Returns:
           True if no violated constraint exists, otherwise False.
       """

    for c in constraints:
        a, b = c["vars"]
        if a in assignment and b in assignment:
            if not satisfies(c["type"], assignment[a], assignment[b]):
                return False
    return True


def is_consistent_with(var: str, val: int, assignment: Assignment, constraints: List[JsonDict]) -> bool:
    """
       Check whether assigning `var = val` is consistent with current assignment.

       Evaluates only constraints between `var` and variables already assigned.

       Args:
           var: Variable to test.
           val: Candidate value.
           assignment: Current partial assignment (without var assigned, typically).
           constraints: Constraint list.

       Returns:
           True if the assignment is locally consistent, otherwise False.
       """

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
    """
        Check if (x=xv, y=yv) satisfies all constraints between x and y.

        The constraint list may contain constraints in either direction [x, y] or [y, x].
        This function enforces that all applicable constraints are satisfied.

        Args:
            x: First variable.
            xv: Value for x.
            y: Second variable.
            yv: Value for y.
            constraints: Constraint list.

        Returns:
            True if the pair is consistent for all constraints between x and y, else False.
        """
    for c in constraints:
        a, b = c["vars"]
        if a == x and b == y:
            if not satisfies(c["type"], xv, yv):
                return False
        if a == y and b == x:
            if not satisfies(c["type"], yv, xv):
                return False
    return True