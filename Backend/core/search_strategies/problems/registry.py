from __future__ import annotations

from Backend.core.search_strategies.search_problem import SearchProblem
from Backend.core.search_strategies.problems.nqueens import build_nqueens_problem
from Backend.core.search_strategies.problems.graph_coloring import build_graph_coloring_problem
from Backend.core.search_strategies.problems.knights_tour import build_knights_tour_problem
from Backend.core.search_strategies.problems.generalized_hanoi import build_generalized_hanoi_problem


def build_problem(problem_key: str, instance: dict) -> SearchProblem:
    p = (problem_key or "").strip().lower()
    if p in ("nqueens", "n-queens", "n_queens"):
        board = instance if isinstance(instance, list) else (instance.get("board") or [])
        return build_nqueens_problem(board)
    if p in ("graph_coloring", "graph-coloring", "coloring"):
        return build_graph_coloring_problem(instance)
    if p in ("knights_tour", "knightstour", "knights-tour"):
        return build_knights_tour_problem(instance)
    if p in ("generalized_hanoi", "hanoi", "tower_of_hanoi"):
        return build_generalized_hanoi_problem(instance)

    raise ValueError(f"Unknown problem_key: {problem_key}")