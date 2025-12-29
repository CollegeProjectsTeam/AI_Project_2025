from __future__ import annotations

import os
import time
import importlib.util

from Backend.services import Logger

log = Logger("NQueensComparator")


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
    def _get_algorithms_path() -> str:
        current_dir = os.path.dirname(__file__)
        search_strategies_root = os.path.dirname(current_dir)
        algorithms_dir = os.path.join(search_strategies_root, "Algorithms")

        log.info(
            "Resolving algorithms directory",
            ctx={
                "current_dir": current_dir,
                "search_strategies_root": search_strategies_root,
                "algorithms_dir": algorithms_dir,
            },
        )

        if not os.path.exists(algorithms_dir):
            log.error("Algorithms folder not found", ctx={"algorithms_dir": algorithms_dir})
            raise FileNotFoundError(
                f"[NQueens Comparator] Algorithms folder not found: {algorithms_dir}"
            )

        log.ok("Algorithms folder resolved", ctx={"algorithms_dir": algorithms_dir})
        return algorithms_dir

    @staticmethod
    def compare_algorithms(board: list[list[int]]):
        algorithms_path = AlgorithmComparator._get_algorithms_path()

        log.info(
            "Starting N-Queens algorithm comparison",
            ctx={
                "algorithms_path": algorithms_path,
                "board_size": len(board) if board else None,
            },
        )

        results: dict[str, tuple[float, Any]] = {}
        report_string = ""
        times_vector = [None] * len(AlgorithmComparator.ALGORITHM_ORDER)

        # NEW: per-alg timing info (for FE explanation)
        timings: list[dict] = []

        for idx, algorithm_name in enumerate(AlgorithmComparator.ALGORITHM_ORDER):
            filepath = os.path.join(algorithms_path, f"{algorithm_name}.py")

            log.info(
                "Loading algorithm module",
                ctx={"algorithm": algorithm_name, "index": idx, "filepath": filepath},
            )

            if not os.path.exists(filepath):
                log.warn("Algorithm file missing", ctx={"algorithm": algorithm_name, "filepath": filepath})
                report_string += f"{string_name(algorithm_name)} missing file\n"

                timings.append(
                    {
                        "key": algorithm_name,
                        "name": string_name(algorithm_name),
                        "status": "missing_file",
                        "time_s": None,
                        "time_ms": None,
                        "note": "file missing",
                    }
                )
                continue

            try:
                spec = importlib.util.spec_from_file_location(algorithm_name, filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception as e:
                log.error(
                    "Failed to import algorithm module",
                    ctx={"algorithm": algorithm_name, "filepath": filepath, "exc_type": type(e).__name__},
                    exc=e,
                )
                report_string += f"{string_name(algorithm_name)} ERROR: {e}\n"

                timings.append(
                    {
                        "key": algorithm_name,
                        "name": string_name(algorithm_name),
                        "status": "import_error",
                        "time_s": None,
                        "time_ms": None,
                        "note": str(e),
                    }
                )
                continue

            solve_fn = getattr(module, "solve_nqueens", None)
            if not solve_fn:
                log.warn(
                    "Algorithm module missing solve_nqueens",
                    ctx={"algorithm": algorithm_name, "filepath": filepath},
                )
                report_string += f"{string_name(algorithm_name)} missing solve_nqueens\n"

                timings.append(
                    {
                        "key": algorithm_name,
                        "name": string_name(algorithm_name),
                        "status": "missing_entrypoint",
                        "time_s": None,
                        "time_ms": None,
                        "note": "missing solve_nqueens",
                    }
                )
                continue

            log.info("Running algorithm", ctx={"algorithm": algorithm_name})

            start = time.time()
            try:
                solution = solve_fn(board)
                exec_time = time.time() - start
                exec_time_s = round(exec_time, 6)
                exec_time_ms = round(exec_time * 1000.0, 3)

                if solution:
                    log.ok(
                        "Algorithm found solution",
                        ctx={"algorithm": algorithm_name, "execution_time_s": exec_time_s},
                    )
                    report_string += f"{string_name(algorithm_name)} found a solution in {exec_time_s:.6f}s\n"
                    results[algorithm_name] = (exec_time, solution)
                    times_vector[idx] = exec_time

                    timings.append(
                        {
                            "key": algorithm_name,
                            "name": string_name(algorithm_name),
                            "status": "solved",
                            "time_s": exec_time_s,
                            "time_ms": exec_time_ms,
                        }
                    )
                else:
                    log.warn(
                        "Algorithm did not find solution",
                        ctx={"algorithm": algorithm_name, "execution_time_s": exec_time_s},
                    )
                    report_string += f"{string_name(algorithm_name)} did not find a solution\n"

                    timings.append(
                        {
                            "key": algorithm_name,
                            "name": string_name(algorithm_name),
                            "status": "no_solution",
                            "time_s": exec_time_s,
                            "time_ms": exec_time_ms,
                        }
                    )

            except Exception as e:
                exec_time = time.time() - start
                exec_time_s = round(exec_time, 6)
                exec_time_ms = round(exec_time * 1000.0, 3)

                log.error(
                    "Algorithm crashed while solving",
                    ctx={"algorithm": algorithm_name, "execution_time_s": exec_time_s, "exc_type": type(e).__name__},
                    exc=e,
                )
                report_string += f"{string_name(algorithm_name)} ERROR: {e}\n"

                timings.append(
                    {
                        "key": algorithm_name,
                        "name": string_name(algorithm_name),
                        "status": "runtime_error",
                        "time_s": exec_time_s,
                        "time_ms": exec_time_ms,
                        "note": str(e),
                    }
                )

        if not results:
            log.warn("No algorithm produced a solution")
            return None

        fastest_algorithm_key = min(results, key=lambda k: results[k][0])
        fastest_time, fastest_solution = results[fastest_algorithm_key]
        percentages = AlgorithmComparator.calculate_time_percentages(times_vector)

        # NEW: sort timings DESC by time (None last)
        def _sort_key(t: dict):
            ts = t.get("time_s")
            return (ts is None, -(ts or 0.0))

        timings_sorted_desc = sorted(timings, key=_sort_key)

        # NEW: pct_of_fastest per entry (only for those with time_s)
        fastest_valid = min([t for t in times_vector if t is not None], default=None)
        if fastest_valid is not None:
            for t in timings_sorted_desc:
                ts = t.get("time_s")
                if ts is None or ts <= 0:
                    t["pct_of_fastest"] = None
                else:
                    t["pct_of_fastest"] = round((fastest_valid / ts) * 100.0, 2)
        else:
            for t in timings_sorted_desc:
                t["pct_of_fastest"] = None

        log.ok(
            "Comparison finished",
            ctx={
                "fastest_algorithm_key": fastest_algorithm_key,
                "fastest_algorithm": string_name(fastest_algorithm_key),
                "fastest_time_s": round(fastest_time, 6),
            },
        )

        return {
            "fastest_algorithm_key": fastest_algorithm_key,
            "fastest_algorithm": string_name(fastest_algorithm_key),
            "execution_time": fastest_time,
            "solution": fastest_solution,
            "report": report_string,
            "times_vector": times_vector,
            "time_percentages": percentages,
            "timings": timings_sorted_desc,  # NEW
        }

    @staticmethod
    def calculate_time_percentages(times_vector: list[float | None]) -> list[float | None]:
        valid = [t for t in times_vector if t is not None]
        if not valid:
            log.warn("No valid execution times for percentage calculation")
            return [None] * len(times_vector)

        fastest = min(valid)
        log.info(
            "Calculating time percentages",
            ctx={
                "fastest_time_s": round(fastest, 6),
                "valid_count": len(valid),
                "total_count": len(times_vector),
            },
        )

        out: list[float | None] = []
        for t in times_vector:
            if t is None:
                out.append(None)
            else:
                out.append(round((fastest / t) * 100, 2))
        return out

    @staticmethod
    def answer_option_keys():
        return list(AlgorithmComparator.ALGORITHM_ORDER)

    @staticmethod
    def answer_options():
        return [string_name(k) for k in AlgorithmComparator.ALGORITHM_ORDER]
