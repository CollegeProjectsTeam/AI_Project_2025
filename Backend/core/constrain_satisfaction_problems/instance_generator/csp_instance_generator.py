from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Tuple

try:
    from Backend.services.logging_service import Logger
except Exception:
    from Backend.services import Logger

from Backend.core.constrain_satisfaction_problems.instance_generator.csp_models import CSPGenConfig

log = Logger("CSP.InstanceGen")
JsonDict = Dict[str, Any]


class CSPInstanceGenerator:
    @staticmethod
    def generate_random_payload(
        config: CSPGenConfig,
        *,
        inference: str = "FC",
        var_heuristic: str = "FIXED",
        value_heuristic: str = "LCV",
        consistency: str = "NONE",
        ask_for: str = "TRACE_UNTIL_SOLUTION",
        fixed_order: bool = True,
    ) -> JsonDict:
        rnd = random.Random(config.seed)

        if config.num_vars < 2:
            raise ValueError("num_vars must be >= 2")

        variables = CSPInstanceGenerator._var_names(config.num_vars)
        order = variables[:] if fixed_order else CSPInstanceGenerator._shuffled(variables, rnd)

        solution = CSPInstanceGenerator._hidden_solution(
            variables=variables,
            rnd=rnd,
            vmin=config.value_min,
            vmax=config.value_max,
        )

        domains = CSPInstanceGenerator._domains_around_solution(
            solution=solution,
            rnd=rnd,
            vmin=config.value_min,
            vmax=config.value_max,
            min_size=config.domain_min_size,
            max_size=config.domain_max_size,
        )

        constraints = CSPInstanceGenerator._constraints_consistent_with_solution(
            variables=variables,
            solution=solution,
            rnd=rnd,
            target=config.num_constraints,
        )

        partial_assignment = CSPInstanceGenerator._partial_assignment(
            variables=variables,
            solution=solution,
            rnd=rnd,
            prob=config.partial_assign_prob,
        )

        payload: JsonDict = {
            "inference": inference,
            "var_heuristic": var_heuristic,
            "value_heuristic": value_heuristic,
            "consistency": consistency,
            "ask_for": ask_for,
            "instance": {
                "variables": variables,
                "order": order,
                "domains": domains,
                "constraints": constraints,
                "partial_assignment": partial_assignment,
            },
        }

        log.info(
            "Generated random CSP payload",
            {
                "num_vars": config.num_vars,
                "num_constraints": len(constraints),
                "inference": inference,
                "var_heuristic": var_heuristic,
                "value_heuristic": value_heuristic,
                "consistency": consistency,
                "ask_for": ask_for,
                "seed": config.seed,
            },
        )

        return payload

    @staticmethod
    def generate_fc_lcv_exam_style(seed: Optional[int] = None) -> JsonDict:
        cfg = CSPGenConfig(
            num_vars=3,
            value_min=0,
            value_max=6,
            domain_min_size=2,
            domain_max_size=4,
            num_constraints=3,
            partial_assign_prob=0.0,
            seed=seed,
        )
        return CSPInstanceGenerator.generate_random_payload(
            cfg,
            inference="FC",
            var_heuristic="FIXED",
            value_heuristic="LCV",
            consistency="NONE",
            ask_for="TRACE_UNTIL_SOLUTION",
            fixed_order=True,
        )

    @staticmethod
    def _var_names(n: int) -> List[str]:
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if n <= len(alphabet):
            return [alphabet[i] for i in range(n)]
        return [f"X{i+1}" for i in range(n)]

    @staticmethod
    def _shuffled(items: List[str], rnd: random.Random) -> List[str]:
        out = items[:]
        rnd.shuffle(out)
        return out

    @staticmethod
    def _hidden_solution(
        *,
        variables: List[str],
        rnd: random.Random,
        vmin: int,
        vmax: int,
    ) -> Dict[str, int]:
        sol: Dict[str, int] = {}
        for v in variables:
            sol[v] = rnd.randint(vmin, vmax)
        return sol

    @staticmethod
    def _domains_around_solution(
        *,
        solution: Dict[str, int],
        rnd: random.Random,
        vmin: int,
        vmax: int,
        min_size: int,
        max_size: int,
    ) -> Dict[str, List[int]]:
        if min_size < 1 or max_size < min_size:
            raise ValueError("invalid domain size range")

        domains: Dict[str, List[int]] = {}
        for var, sol_val in solution.items():
            size = rnd.randint(min_size, max_size)
            vals = {sol_val}
            tries = 0
            while len(vals) < size and tries < 200:
                vals.add(rnd.randint(vmin, vmax))
                tries += 1
            domains[var] = sorted(vals)
        return domains

    @staticmethod
    def _constraints_consistent_with_solution(
        *,
        variables: List[str],
        solution: Dict[str, int],
        rnd: random.Random,
        target: int,
    ) -> List[JsonDict]:
        if target < 0:
            raise ValueError("target constraints must be >= 0")

        pairs: List[Tuple[str, str]] = []
        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                pairs.append((variables[i], variables[j]))

        rnd.shuffle(pairs)

        constraints: List[JsonDict] = []
        used = set()

        for a, b in pairs:
            if len(constraints) >= target:
                break

            va, vb = solution[a], solution[b]
            rel = rnd.choice(["neq", "lt", "gt"])

            if rel == "neq":
                if va == vb:
                    continue
                key = ("neq", tuple(sorted((a, b))))
                if key in used:
                    continue
                constraints.append({"type": "neq", "vars": [a, b]})
                used.add(key)
                continue

            if rel == "lt":
                if va < vb:
                    key = ("lt", a, b)
                    if key in used:
                        continue
                    constraints.append({"type": "lt", "vars": [a, b]})
                    used.add(key)
                elif vb < va:
                    key = ("lt", b, a)
                    if key in used:
                        continue
                    constraints.append({"type": "lt", "vars": [b, a]})
                    used.add(key)
                continue

            if rel == "gt":
                if va > vb:
                    key = ("gt", a, b)
                    if key in used:
                        continue
                    constraints.append({"type": "gt", "vars": [a, b]})
                    used.add(key)
                elif vb > va:
                    key = ("gt", b, a)
                    if key in used:
                        continue
                    constraints.append({"type": "gt", "vars": [b, a]})
                    used.add(key)
                continue

        if len(constraints) < target:
            for a, b in pairs:
                if len(constraints) >= target:
                    break
                va, vb = solution[a], solution[b]
                if va == vb:
                    continue
                key = ("neq", tuple(sorted((a, b))))
                if key in used:
                    continue
                constraints.append({"type": "neq", "vars": [a, b]})
                used.add(key)

        return constraints

    @staticmethod
    def _partial_assignment(
        *,
        variables: List[str],
        solution: Dict[str, int],
        rnd: random.Random,
        prob: float,
    ) -> Dict[str, int]:
        if prob <= 0:
            return {}
        out: Dict[str, int] = {}
        for v in variables:
            if rnd.random() < prob:
                out[v] = solution[v]
        return out
