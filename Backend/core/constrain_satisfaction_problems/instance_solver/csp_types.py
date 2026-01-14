from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

"""
csp_types.py

Shared type aliases and small utilities for the CSP solver.

This module defines:
- JsonDict: JSON-like dict payload fragments
- Domains: mapping var -> list[int] (current domain values)
- Assignment: mapping var -> int (partial/complete assignment)
- CSPSolveStats: counters used for tracing solver effort
- domains_snapshot(): deep-ish copy helper for trace logging
"""

JsonDict = Dict[str, Any]
Domains = Dict[str, List[int]]
Assignment = Dict[str, int]


@dataclass
class CSPSolveStats:
    """
      Search statistics accumulated during solving.

      Attributes:
          nodes: Number of value-attempts tried (one per TRY candidate).
          backtracks: Number of times the solver backtracked from a choice.
          fails: Number of failed attempts due to inconsistency or propagation failure.
          prunes: Total number of domain values removed by inference/consistency.
      """

    nodes: int = 0
    backtracks: int = 0
    fails: int = 0
    prunes: int = 0


def domains_snapshot(domains: Domains) -> Dict[str, List[int]]:
    """
    Return a snapshot copy of current domains.

    This is used primarily for trace logging so that later domain mutations do not
    overwrite the recorded view.

    Args:
        domains: Current domains mapping var -> list[int].

    Returns:
        A new dict with new lists for each variable.
    """
    return {k: list(v) for k, v in domains.items()}
