from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

JsonDict = Dict[str, Any]

class CSPPayloadNormalizer:
    @staticmethod
    def normalize(payload: JsonDict) -> JsonDict:
        p = dict(payload or {})

        # settings defaults
        p.setdefault("inference", "NONE")
        p.setdefault("var_heuristic", "FIXED")
        p.setdefault("value_heuristic", "NONE")
        p.setdefault("consistency", "NONE")
        p.setdefault("ask_for", "TRACE_UNTIL_SOLUTION")

        inst = dict(p.get("instance") or {})

        # variables / order
        variables = inst.get("variables") or []
        inst["variables"] = [str(v) for v in variables]

        order = inst.get("order")
        if order:
            inst["order"] = [str(v) for v in order]
        elif inst["variables"]:
            inst["order"] = list(inst["variables"])

        # domains: force list[int], unique, sorted
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

        # constraints: dict with {type, vars:[a,b]}
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

        # partial_assignment: dict[str,int]
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
        return p


class CSPPayloadValidator:
    @staticmethod
    def validate(payload: JsonDict, *, strict: bool) -> None:
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
