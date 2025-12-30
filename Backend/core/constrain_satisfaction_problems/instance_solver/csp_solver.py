from __future__ import annotations

from typing import Dict, List, Optional, Tuple

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
    @staticmethod
    def solve(payload: JsonDict, *, strict: bool = True) -> JsonDict:
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

        # apply partial assignment propagation
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