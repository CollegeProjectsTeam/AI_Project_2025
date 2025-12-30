from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

JsonDict = Dict[str, Any]
Domains = Dict[str, List[int]]
Assignment = Dict[str, int]


@dataclass
class CSPSolveStats:
    nodes: int = 0
    backtracks: int = 0
    fails: int = 0
    prunes: int = 0


def domains_snapshot(domains: Domains) -> Dict[str, List[int]]:
    return {k: list(v) for k, v in domains.items()}
