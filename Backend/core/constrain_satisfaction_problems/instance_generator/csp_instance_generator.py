from __future__ import annotations

"""
csp_instance_generator.py

Random instance/payload generator for Constraint Satisfaction Problems (CSP).

This module builds *satisfiable* CSP instances by first sampling a hidden complete
assignment (a "solution") and then generating domains and constraints that are
consistent with that hidden solution.

The output of `generate_random_payload()` is a JSON-serializable dictionary
("payload") that includes:
- solver configuration options (inference, heuristics, etc.)
- an `instance` object (variables, order, domains, constraints, partial assignment)

Constraint types currently supported by the generator:
- "neq": X != Y
- "lt" : X < Y
- "gt" : X > Y

Notes:
- Randomness is controlled via `CSPGenConfig.seed`.
- Constraints are constructed to not eliminate the hidden solution; hence the
  generated instances are intended to be solvable (at least one solution exists).
"""

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
    """
    Factory for generating random CSP payloads and exam-style CSP instances.

    The generator follows this high-level pipeline:

    1) Pick variable names (A, B, C, ...).
    2) Sample a hidden solution: a value for each variable in [value_min, value_max].
    3) Build each variable domain around its solution value (always includes it).
    4) Create constraints (neq/lt/gt) consistent with the hidden solution.
    5) Optionally reveal a partial assignment (some variables fixed to solution values).
    6) Package everything into a JSON payload usable by your solver/tracer.
    """
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
        """
               Generate a JSON-serializable CSP solver payload.

               The generated CSP instance is guaranteed to contain at least one solution
               (the internally sampled hidden solution), because domains and constraints are
               constructed to be consistent with it.

               Args:
                   config: Generator configuration (number of vars, value range, domain sizes,
                       number of constraints, partial assignment probability, seed).
                   inference: Inference mode label to embed in payload (e.g., "FC", "MAC", "NONE").
                   var_heuristic: Variable selection heuristic label (e.g., "MRV", "DEG", "FIXED").
                   value_heuristic: Value ordering heuristic label (e.g., "LCV", "NONE").
                   consistency: Additional consistency enforcement label (e.g., "AC3", "NONE").
                   ask_for: What the solver should return/compute (e.g., "TRACE_UNTIL_SOLUTION").
                   fixed_order: If True, keep variable order as generated; otherwise shuffle.

               Returns:
                   A dict payload with the following structure:
                   {
                     "inference": ...,
                     "var_heuristic": ...,
                     "value_heuristic": ...,
                     "consistency": ...,
                     "ask_for": ...,
                     "instance": {
                        "variables": [...],
                        "order": [...],
                        "domains": {var: [..], ...},
                        "constraints": [{"type": "...", "vars": [a,b]}, ...],
                        "partial_assignment": {var: value, ...}
                     }
                   }

               Raises:
                   ValueError: If `config.num_vars < 2` or domain size range is invalid.

               Notes:
                   - Constraint generation tries to hit `config.num_constraints`. In rare edge
                     cases (e.g., all hidden values equal), it may not be possible to add all
                     requested constraints while staying consistent.
               """
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
        """
             Generate a small CSP payload in an "exam style" configuration.

             This is a convenience wrapper over `generate_random_payload()` using:
             - 3 variables
             - value range [0, 15]
             - 3 constraints
             - no partial assignment
             - solver options: FC + FIXED variable order + LCV value heuristic

             Args:
                 seed: Optional seed for deterministic generation.

             Returns:
                 A CSP payload dict compatible with the solver pipeline.
             """
        cfg = CSPGenConfig(
            num_vars=3,
            value_min=0,
            value_max=15,
            domain_min_size=2,
            domain_max_size=10,
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
        """
               Build variable names for a CSP instance.

               For up to 26 variables: A..Z.
               After that: X1, X2, ...

               Args:
                   n: Number of variables.

               Returns:
                   List of variable identifiers.
               """
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if n <= len(alphabet):
            return [alphabet[i] for i in range(n)]
        return [f"X{i+1}" for i in range(n)]

    @staticmethod
    def _shuffled(items: List[str], rnd: random.Random) -> List[str]:
        """
             Return a shuffled copy of `items`.

             Args:
                 items: Input list.
                 rnd: Random generator (seeded).

             Returns:
                 Shuffled list copy.
             """
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
        """
              Sample a complete hidden assignment (one value per variable).

              Args:
                  variables: Variable names.
                  rnd: Random generator.
                  vmin: Minimum allowed value (inclusive).
                  vmax: Maximum allowed value (inclusive).

              Returns:
                  Dict mapping each variable to a sampled integer value.
              """
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
        """
               Construct variable domains ensuring each includes its solution value.

               For each variable:
               - pick a random size in [min_size, max_size]
               - start with {solution_value}
               - add random values from [vmin, vmax] until size is reached (or tries limit)

               Args:
                   solution: Hidden solution mapping var -> value.
                   rnd: Random generator.
                   vmin: Minimum value to sample.
                   vmax: Maximum value to sample.
                   min_size: Minimum domain size (>= 1).
                   max_size: Maximum domain size (>= min_size).

               Returns:
                   Dict mapping var -> sorted list of unique integer domain values.

               Raises:
                   ValueError: If min/max domain size range is invalid.

               Notes:
                   The tries limit (200) prevents an infinite loop when the value range
                   is too small to fill large domains with unique values.
               """
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
        """
               Generate binary constraints consistent with the hidden solution.

               The generator considers all unordered variable pairs and tries to add
               constraints until `target` is reached:
               - randomly choose relation among: neq, lt, gt
               - only add the constraint if it is satisfied by the hidden solution
               - avoid duplicates via a `used` set

               If after this pass we still have fewer than `target` constraints, a fallback
               pass tries to add more "neq" constraints where possible.

               Args:
                   variables: Variable list.
                   solution: Hidden solution mapping var -> value.
                   rnd: Random generator.
                   target: Desired number of constraints (>= 0).

               Returns:
                   List of constraint dicts: {"type": <"neq"|"lt"|"gt">, "vars": [a, b]}.

               Raises:
                   ValueError: If target < 0.
               """
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
        """
               Optionally reveal a partial assignment consistent with the hidden solution.

               Each variable is included with independent probability `prob`, and if included,
               it is fixed to its solution value.

               Args:
                   variables: Variables list.
                   solution: Hidden solution mapping var -> value.
                   rnd: Random generator.
                   prob: Probability of including each variable in the partial assignment.

               Returns:
                   Dict mapping some variables to their fixed values. Empty if prob <= 0.
               """
        if prob <= 0:
            return {}
        out: Dict[str, int] = {}
        for v in variables:
            if rnd.random() < prob:
                out[v] = solution[v]
        return out
