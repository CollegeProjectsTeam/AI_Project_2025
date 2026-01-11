from __future__ import annotations

import time
from typing import Any, Optional

from Backend.core.search_strategies.problems.registry import build_problem
from Backend.core.search_strategies.search_problem import SearchBudget
from Backend.core.search_strategies import algorithms_generic as ag
from Backend.services import Logger

log = Logger("SearchComparator")


def string_name(algorithm_name: str) -> str:
    names = {
        "breadth_first_search": "Breadth First Search",
        "depth_first_search": "Depth First Search",
        "uniform_cost_search": "Uniform Cost Search",
        "iterative_deepening_depth_first_search": "Iterative Deepening DFS",
        "backtracking": "Backtracking",
        "bidirectional_search": "Bidirectional Search",
        "greedy_best_first_search": "Greedy Best First",
        "hill_climbing": "Hill Climbing",
        "simulated_annealing": "Simulated Annealing",
        "beam_search": "Beam Search",
        "a_star": "A*",
    }
    return names.get(algorithm_name, algorithm_name)


def _auto_max_depth(problem: Any) -> int:
    n = getattr(problem, "n", None)
    num_nodes = getattr(problem, "num_nodes", None)
    disks = getattr(problem, "disks", None)

    if isinstance(n, int) and n > 0:
        return min(max(8, n), 25)

    if isinstance(num_nodes, int) and num_nodes > 0:
        return min(max(10, num_nodes), 30)

    if isinstance(disks, int) and disks > 0:
        return min(max(8, disks * 3), 30)

    return 25


class AlgorithmComparator:
    ALGORITHM_ORDER = [
        "breadth_first_search",
        "depth_first_search",
        "uniform_cost_search",
        "iterative_deepening_depth_first_search",
        "backtracking",
        "bidirectional_search",
        "greedy_best_first_search",
        "hill_climbing",
        "simulated_annealing",
        "beam_search",
        "a_star",
    ]

    @staticmethod
    def compare(problem_key: str, instance: dict, budget: SearchBudget | None = None) -> Optional[dict]:
        problem = build_problem(problem_key, instance)
        budget_base = budget or SearchBudget()

        results: dict[str, tuple[float, Any]] = {}
        timings: list[dict] = []

        def run_alg(key: str) -> Any:
            b = SearchBudget(max_time_s=budget_base.max_time_s, max_expansions=budget_base.max_expansions)

            if key == "breadth_first_search":
                return ag.bfs(problem, b)
            if key == "depth_first_search":
                return ag.dfs(problem, b)
            if key == "uniform_cost_search":
                return ag.ucs(problem, b)
            if key == "iterative_deepening_depth_first_search":
                md = _auto_max_depth(problem)
                return ag.iddfs(problem, b, max_depth=md)
            if key == "backtracking":
                return ag.backtracking(problem, b)
            if key == "greedy_best_first_search":
                return ag.greedy_best_first(problem, b)
            if key == "hill_climbing":
                return ag.hill_climbing(problem, b)
            if key == "simulated_annealing":
                return ag.simulated_annealing(problem, b)
            if key == "beam_search":
                return ag.beam_search(problem, b, beam_width=20)
            if key == "a_star":
                return ag.a_star(problem, b)

            return None

        for alg in AlgorithmComparator.ALGORITHM_ORDER:
            if alg == "bidirectional_search":
                timings.append(
                    {
                        "key": alg,
                        "name": string_name(alg),
                        "status": "not_implemented",
                        "time_s": None,
                        "time_ms": None,
                        "note": "Not implemented in algorithms_generic",
                    }
                )
                continue

            t0 = time.perf_counter()
            try:
                sol = run_alg(alg)
                dt = time.perf_counter() - t0
            except Exception as e:
                dt = time.perf_counter() - t0
                timings.append(
                    {
                        "key": alg,
                        "name": string_name(alg),
                        "status": "runtime_error",
                        "time_s": round(dt, 6),
                        "time_ms": round(dt * 1000.0, 3),
                        "note": str(e),
                    }
                )
                continue

            if sol is None:
                timings.append(
                    {
                        "key": alg,
                        "name": string_name(alg),
                        "status": "no_solution",
                        "time_s": round(dt, 6),
                        "time_ms": round(dt * 1000.0, 3),
                    }
                )
                continue

            results[alg] = (dt, sol)
            timings.append(
                {
                    "key": alg,
                    "name": string_name(alg),
                    "status": "solved",
                    "time_s": round(dt, 6),
                    "time_ms": round(dt * 1000.0, 3),
                }
            )

        if not results:
            return None

        best_alg = min(results, key=lambda k: results[k][0])
        best_t, best_sol = results[best_alg]
        best_t = float(best_t)

        for t in timings:
            ms = t.get("time_ms")
            if isinstance(ms, (int, float)) and best_t > 0:
                t["pct_of_fastest"] = (float(ms) / (best_t * 1000.0)) * 100.0

        timings_sorted = sorted(
            timings,
            key=lambda x: (x["time_s"] is None, x["time_s"] if isinstance(x["time_s"], (int, float)) else 10**18),
        )

        return {
            "fastest_algorithm_key": best_alg,
            "fastest_algorithm": string_name(best_alg),
            "execution_time": round(best_t, 6),
            "solution": best_sol,
            "timings": timings_sorted,
        }