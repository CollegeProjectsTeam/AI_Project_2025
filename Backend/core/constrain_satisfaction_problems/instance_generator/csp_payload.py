from __future__ import annotations

"""
csp_payload.py

Normalization and validation utilities for CSP solver payloads.

This module provides:
- `CSPPayloadNormalizer.normalize()`:
    * fills missing top-level defaults
    * coerces/cleans instance fields into a consistent shape:
      variables as strings, domains as sorted unique int lists, constraints filtered
      and lowercased, partial_assignment coerced to ints
- `CSPPayloadValidator.validate()`:
    * enforces required fields and consistent references
    * optionally enforces strict partial assignment validity (values must be in domains)

These helpers are typically used at API boundaries:
- user uploads/edits a JSON payload -> normalize -> validate -> run solver
"""

from typing import Any, Dict, List, Set

try:
    from Backend.services.logging_service import Logger
except Exception:
    from Backend.services import Logger

JsonDict = Dict[str, Any]
log = Logger("CSP.Payload")


class CSPPayloadNormalizer:
    """
      Normalize a CSP payload into a stable, solver-friendly structure.

      The normalizer is intentionally forgiving:
      - missing fields get defaults
      - invalid entries are skipped rather than raising
      - values are coerced when possible (e.g., domain entries to int)

      Use `CSPPayloadValidator` after normalization to enforce correctness.
      """

    @staticmethod
    def normalize(payload: JsonDict) -> JsonDict:
        """
             Normalize a potentially messy CSP payload.

             Normalization steps:
             - Top-level defaults:
               inference, var_heuristic, value_heuristic, consistency, ask_for
             - instance.variables:
               coerced to list[str]
             - instance.order:
               if provided, coerced to list[str]; else defaults to variables order
             - instance.domains:
               coerced to dict[str, list[int]] with sorted unique ints; invalid values skipped
             - instance.constraints:
               coerced to list of {"type": <lowercase str>, "vars": [str, str]}
               only keeps entries with 2 vars and a non-empty type
             - instance.partial_assignment:
               coerced to dict[str, int]; invalid entries skipped

             Args:
                 payload: Input dict (possibly missing fields / wrong types).

             Returns:
                 A new dict containing a normalized CSP payload.
             """

        p = dict(payload or {})

        p.setdefault("inference", "NONE")
        p.setdefault("var_heuristic", "FIXED")
        p.setdefault("value_heuristic", "NONE")
        p.setdefault("consistency", "NONE")
        p.setdefault("ask_for", "TRACE_UNTIL_SOLUTION")

        inst = dict(p.get("instance") or {})

        variables = inst.get("variables") or []
        inst["variables"] = [str(v) for v in variables]

        order = inst.get("order")
        if order:
            inst["order"] = [str(v) for v in order]
        elif inst["variables"]:
            inst["order"] = list(inst["variables"])

        domains = inst.get("domains") or {}
        norm_domains: Dict[str, List[int]] = {}
        if isinstance(domains, dict):
            for k, v in domains.items():
                if v is None:
                    continue
                vals: List[int] = []
                if isinstance(v, list):
                    for x in v:
                        try:
                            vals.append(int(x))
                        except Exception:
                            continue
                norm_domains[str(k)] = sorted(set(vals))
        inst["domains"] = norm_domains

        constraints = inst.get("constraints") or []
        norm_constraints: List[JsonDict] = []
        if isinstance(constraints, list):
            for c in constraints:
                if not isinstance(c, dict):
                    continue
                ctype = (c.get("type") or "").strip().lower()
                vars_c = c.get("vars") or []
                if ctype and isinstance(vars_c, list) and len(vars_c) == 2:
                    norm_constraints.append(
                        {"type": ctype, "vars": [str(vars_c[0]), str(vars_c[1])]}
                    )
        inst["constraints"] = norm_constraints

        pa = inst.get("partial_assignment") or {}
        norm_pa: Dict[str, int] = {}
        if isinstance(pa, dict):
            for k, v in pa.items():
                try:
                    norm_pa[str(k)] = int(v)
                except Exception:
                    continue
        inst["partial_assignment"] = norm_pa

        p["instance"] = inst

        log.info(
            "CSP payload normalized",
            {
                "vars": len(inst.get("variables") or []),
                "domains": len(inst.get("domains") or {}),
                "constraints": len(inst.get("constraints") or []),
                "partial_assignment": len(inst.get("partial_assignment") or {}),
            },
        )

        return p


class CSPPayloadValidator:
    """
        Validate a normalized CSP payload.

        This is the stricter counterpart to `CSPPayloadNormalizer`:
        it raises ValueError on invalid structure or references.

        Validation checks:
        - variables non-empty
        - order contains exactly the same variables
        - domains is a dict and each variable has a non-empty list domain
        - constraints is a list of dicts with allowed types and existing vars
        - partial_assignment is a dict
        - (strict mode) partial_assignment only references existing variables and
          assigned values must belong to the corresponding domain
        """

    @staticmethod
    def validate(payload: JsonDict, *, strict: bool) -> None:
        """
                Validate a CSP payload.

                Args:
                    payload: A payload dict (ideally already normalized).
                    strict: If True, enforce that partial assignments are valid:
                        - variable exists in instance.variables
                        - assigned value is in that variable's domain

                Raises:
                    ValueError: If required fields are missing, types are wrong, references
                        are inconsistent, or strict checks fail.
                """

        inst = payload.get("instance") or {}

        variables = inst.get("variables") or []
        if not variables:
            raise ValueError("CSP payload invalid: instance.variables is required and must be non-empty")

        var_set: Set[str] = set(variables)

        order = inst.get("order") or []
        if set(order) != var_set or len(order) != len(variables):
            raise ValueError(
                "CSP payload invalid: instance.order must contain exactly the same variables as instance.variables"
            )

        domains = inst.get("domains") or {}
        if not isinstance(domains, dict):
            raise ValueError("CSP payload invalid: instance.domains must be an object/dict")

        for v in variables:
            if v not in domains:
                raise ValueError(f"CSP payload invalid: missing domain for variable '{v}'")
            if not isinstance(domains[v], list) or len(domains[v]) == 0:
                raise ValueError(f"CSP payload invalid: domain for '{v}' must be a non-empty list")

        constraints = inst.get("constraints") or []
        if not isinstance(constraints, list):
            raise ValueError("CSP payload invalid: instance.constraints must be a list")

        allowed = {"neq", "lt", "gt"}
        for c in constraints:
            if not isinstance(c, dict):
                raise ValueError("CSP payload invalid: each constraint must be an object")

            ctype = c.get("type")
            vars_c = c.get("vars") or []

            if ctype not in allowed:
                raise ValueError(
                    f"CSP payload invalid: unknown constraint type '{ctype}' (allowed: {sorted(allowed)})"
                )

            if (
                not isinstance(vars_c, list)
                or len(vars_c) != 2
                or vars_c[0] not in var_set
                or vars_c[1] not in var_set
            ):
                raise ValueError(
                    f"CSP payload invalid: constraint vars must reference existing variables: {c}"
                )

        pa = inst.get("partial_assignment") or {}
        if not isinstance(pa, dict):
            raise ValueError("CSP payload invalid: instance.partial_assignment must be an object/dict")

        if strict:
            for v, val in pa.items():
                if v not in var_set:
                    raise ValueError(f"CSP payload invalid: partial_assignment contains unknown variable '{v}'")
                if val not in domains[v]:
                    raise ValueError(
                        f"CSP payload invalid: partial_assignment[{v}]={val} is not in domain {domains[v]}"
                    )

        log.info(
            "CSP payload validated",
            {
                "strict": strict,
                "vars": len(variables),
                "constraints": len(constraints),
                "domains": len(domains),
                "partial_assignment": len(pa),
            },
        )