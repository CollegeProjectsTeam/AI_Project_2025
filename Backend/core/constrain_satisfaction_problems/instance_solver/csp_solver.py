from __future__ import annotations

from typing import Dict, List, Optional, Tuple

"""
csp_solver.py

Backtracking CSP solver with optional inference and consistency maintenance.

This module implements a classic depth-first backtracking search for CSPs,
augmented with:
- variable selection heuristics (FIXED / MRV)
- value ordering heuristics (NONE / LCV)
- inference (NONE / FC = forward checking)
- consistency maintenance (NONE / AC3 preprocess / MAC during search)

The solver consumes a JSON-like payload:
- first normalizes it (defaults, coercions)
- then validates structure and references
- then runs AC3 preprocess / partial propagation
- then runs recursive backtracking until a solution is found or search fails

A step-by-step trace is produced for educational/debug purposes.
"""

try:
    from Backend.services.logging_service import Logger
except Exception:
    from Backend.services import Logger  # fallback

from Backend.core.constrain_satisfaction_problems.instance_generator.csp_payload import (
    CSPPayloadNormalizer,
    CSPPayloadValidator,
)

from Backend.core.constrain_satisfaction_problems.instance_solver.csp_constraints import (
    is_consistent_partial,
    is_consistent_with,
)
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_heuristics import (
    order_values,
    select_unassigned_var,
)
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_inference import (
    ac3,
    arcs_touching,
    forward_check,
)
from Backend.core.constrain_satisfaction_problems.instance_solver.csp_types import (
    Assignment,
    CSPSolveStats,
    Domains,
    JsonDict,
    domains_snapshot,
)

log = Logger("CSP.Solver")


class CSPSolver:
    """
    CSP solver entrypoint.

    Public API:
        solve(payload, strict=True) -> result dict

    The solver is designed for:
    - correctness on small/medium educational instances
    - explainability via `trace`
    - configurable heuristics/inference via payload settings
    """

    @staticmethod
    def solve(payload: JsonDict, *, strict: bool = True) -> JsonDict:
        """
               Solve a CSP instance provided as a JSON-like payload.

               Steps:
               1) Normalize payload (fill defaults, coerce types).
               2) Validate payload structure and references.
               3) Initialize domains and optional partial assignment.
               4) Optional AC3 preprocessing (if consistency == "AC3").
               5) If partial assignment exists, propagate it using FC and/or MAC.
               6) Run recursive backtracking search with configured heuristics.
               7) Return a result dict with solution, trace, and statistics.

               Args:
                   payload: Input payload containing solver settings and CSP instance data.
                   strict: If True, enforce strict validation (partial assignments must be in
                       domain and reference known variables).

               Returns:
                   Result dict:
                   {
                     "ok": True,
                     "found": bool,
                     "solution": {var: value} | None,
                     "settings": {...},
                     "stats": {"nodes":..., "backtracks":..., "fails":..., "prunes":...},
                     "trace": [ ... step dicts ... ]
                   }

               Notes:
                   - "ok" signals API-level success (normalization/validation succeeded).
                   - "found" indicates satisfiable vs unsatisfiable under given constraints.
               """

        p = CSPPayloadNormalizer.normalize(payload)
        CSPPayloadValidator.validate(p, strict=strict)

        settings = {
            "inference": (p.get("inference") or "NONE").upper(),
            "var_heuristic": (p.get("var_heuristic") or "FIXED").upper(),
            "value_heuristic": (p.get("value_heuristic") or "NONE").upper(),
            "consistency": (p.get("consistency") or "NONE").upper(),
            "ask_for": (p.get("ask_for") or "TRACE_UNTIL_SOLUTION").upper(),
        }

        inst = p["instance"]
        variables: List[str] = inst["variables"]
        order: List[str] = inst["order"]
        constraints: List[JsonDict] = inst["constraints"]

        domains: Domains = {v: list(inst["domains"][v]) for v in variables}
        assignment: Assignment = dict(inst.get("partial_assignment") or {})

        trace: List[JsonDict] = []
        stats = CSPSolveStats()

        # preprocess AC3
        if settings["consistency"] == "AC3":
            ok, pruned = ac3(domains, constraints)
            stats.prunes += pruned
            trace.append({"step": "AC3_PRE", "ok": ok, "domains": domains_snapshot(domains)})
            if not ok:
                return CSPSolver._result(False, None, trace, stats, settings)

        if assignment:
            if not is_consistent_partial(assignment, constraints):
                return CSPSolver._result(False, None, trace, stats, settings)

            if settings["inference"] == "FC":
                ok, pruned = forward_check(domains, constraints, assignment, last_assigned_vars=list(assignment.keys()))
                stats.prunes += pruned
                trace.append({"step": "FC_FROM_PARTIAL", "ok": ok, "domains": domains_snapshot(domains)})
                if not ok:
                    return CSPSolver._result(False, None, trace, stats, settings)

            if settings["consistency"] == "MAC":
                ok, pruned = ac3(domains, constraints, queue=arcs_touching(list(assignment.keys()), constraints))
                stats.prunes += pruned
                trace.append({"step": "MAC_FROM_PARTIAL", "ok": ok, "domains": domains_snapshot(domains)})
                if not ok:
                    return CSPSolver._result(False, None, trace, stats, settings)

        found, sol = CSPSolver._backtrack(
            variables=variables,
            order=order,
            domains=domains,
            constraints=constraints,
            assignment=assignment,
            settings=settings,
            trace=trace,
            stats=stats,
        )

        return CSPSolver._result(found, sol if found else None, trace, stats, settings)

    @staticmethod
    def _backtrack(
        *,
        variables: List[str],
        order: List[str],
        domains: Domains,
        constraints: List[JsonDict],
        assignment: Assignment,
        settings: Dict[str, str],
        trace: List[JsonDict],
        stats: CSPSolveStats,
    ) -> Tuple[bool, Optional[Assignment]]:
        """
               Recursive backtracking search.

               At each recursion level:
               - if assignment is complete -> success
               - select an unassigned variable (FIXED or MRV)
               - order its values (NONE or LCV)
               - try values one by one:
                   * check consistency with current partial assignment
                   * commit assignment
                   * run inference (FC) and/or maintain arc consistency (MAC via AC3)
                   * recurse
                   * if failure, undo assignment and restore domains

               Args:
                   variables: All variable names.
                   order: Preferred variable order (used by FIXED and as tie-break).
                   domains: Current domains (mutable; gets pruned by inference).
                   constraints: List of binary constraints.
                   assignment: Current partial assignment (mutable).
                   settings: Uppercased solver settings.
                   trace: Mutable list of trace step dicts.
                   stats: Mutable search statistics.

               Returns:
                   (found, solution) where solution is a fresh dict copy if found.
               """

        if len(assignment) == len(variables):
            return True, dict(assignment)

        var = select_unassigned_var(
            variables,
            order,
            domains,
            assignment,
            heuristic=settings["var_heuristic"],
        )

        values = order_values(
            var,
            domains,
            constraints,
            assignment,
            heuristic=settings["value_heuristic"],
        )

        trace.append({"step": "SELECT_VAR", "var": var, "domain": list(domains[var]), "ordered_values": list(values)})

        for val in values:
            stats.nodes += 1

            if not is_consistent_with(var, val, assignment, constraints):
                stats.fails += 1
                trace.append({"step": "TRY", "var": var, "val": val, "ok": False, "reason": "inconsistent"})
                continue

            assignment[var] = val
            trace.append({"step": "TRY", "var": var, "val": val, "ok": True})

            saved_domains = {k: list(v) for k, v in domains.items()}
            ok = True
            pruned_total = 0

            if settings["inference"] == "FC":
                ok, pruned = forward_check(domains, constraints, assignment, last_assigned_vars=[var])
                pruned_total += pruned
                trace.append({"step": "FC", "var": var, "ok": ok, "domains": domains_snapshot(domains)})
                if not ok:
                    stats.fails += 1

            if ok and settings["consistency"] == "MAC":
                ok, pruned = ac3(domains, constraints, queue=arcs_touching([var], constraints))
                pruned_total += pruned
                trace.append({"step": "MAC", "var": var, "ok": ok, "domains": domains_snapshot(domains)})
                if not ok:
                    stats.fails += 1

            stats.prunes += pruned_total

            if ok:
                found, sol = CSPSolver._backtrack(
                    variables=variables,
                    order=order,
                    domains=domains,
                    constraints=constraints,
                    assignment=assignment,
                    settings=settings,
                    trace=trace,
                    stats=stats,
                )
                if found:
                    return True, sol

            stats.backtracks += 1
            trace.append({"step": "BACKTRACK", "var": var, "val": val})

            assignment.pop(var, None)
            domains.clear()
            domains.update({k: list(v) for k, v in saved_domains.items()})

        return False, None

    @staticmethod
    def _result(
        found: bool,
        solution: Optional[Assignment],
        trace: List[JsonDict],
        stats: CSPSolveStats,
        settings: Dict[str, str],
    ) -> JsonDict:
        """
              Build a standardized solver result object.

              Args:
                  found: Whether a complete solution was found.
                  solution: Solution mapping if found, otherwise None.
                  trace: Trace steps accumulated during preprocess/search.
                  stats: Search counters (nodes, backtracks, fails, prunes).
                  settings: Effective solver settings (uppercased).

              Returns:
                  JSON-like dict used by the API/UI layer.
              """

        return {
            "ok": True,
            "found": found,
            "solution": solution,
            "settings": settings,
            "stats": {
                "nodes": stats.nodes,
                "backtracks": stats.backtracks,
                "fails": stats.fails,
                "prunes": stats.prunes,
            },
            "trace": trace,
        }