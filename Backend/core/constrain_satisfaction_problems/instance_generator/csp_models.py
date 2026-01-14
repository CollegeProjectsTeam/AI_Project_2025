from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

JsonDict = Dict[str, Any]


@dataclass(frozen=True)
class CSPGenConfig:
    num_vars: int = 3
    value_min: int = 0
    value_max: int = 15
    domain_min_size: int = 2
    domain_max_size: int = 10
    num_constraints: int = 3
    partial_assign_prob: float = 0.0
    seed: Optional[int] = None