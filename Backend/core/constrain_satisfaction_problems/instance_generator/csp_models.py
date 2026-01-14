from __future__ import annotations

"""
csp_models.py

Dataclasses used for CSP instance generation.

`CSPGenConfig` describes the parameter space for generating a random CSP instance:
- number of variables
- value range used to sample hidden solutions and domain values
- domain size range for each variable
- number of constraints to generate
- probability of creating a partial assignment
- RNG seed
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

JsonDict = Dict[str, Any]


@dataclass(frozen=True)
class CSPGenConfig:
    """
      Configuration for random CSP generation.

      Attributes:
          num_vars: Number of variables in the instance (>= 2 is required by generator).
          value_min: Minimum integer value allowed (inclusive).
          value_max: Maximum integer value allowed (inclusive).
          domain_min_size: Minimum size for each variable domain (>= 1).
          domain_max_size: Maximum size for each variable domain (>= domain_min_size).
          num_constraints: Target number of binary constraints to generate (>= 0).
          partial_assign_prob: Probability for each variable to be included in a
              partial assignment. If 0.0, no partial assignment is provided.
          seed: Optional RNG seed used for deterministic generation.
      """

    num_vars: int = 3
    value_min: int = 0
    value_max: int = 15
    domain_min_size: int = 2
    domain_max_size: int = 10
    num_constraints: int = 3
    partial_assign_prob: float = 0.0
    seed: Optional[int] = None