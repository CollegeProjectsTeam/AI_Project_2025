import os
import time
import importlib.util


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
    def _get_algorithms_path():
        current_dir = os.path.dirname(__file__)
        search_strategies_root = os.path.dirname(current_dir)
        algorithms_dir = os.path.join(search_strategies_root, "Algorithms")
        if not os.path.exists(algorithms_dir):
            raise FileNotFoundError(f"[NQueens Comparator] Algorithms folder not found: {algorithms_dir}")
        return algorithms_dir

    @staticmethod
    def compare_algorithms(board):
        algorithms_path = AlgorithmComparator._get_algorithms_path()
        results = {}
        report_string = ""
        times_vector = [None] * len(AlgorithmComparator.ALGORITHM_ORDER)

        for idx, algorithm_name in enumerate(AlgorithmComparator.ALGORITHM_ORDER):
            filepath = os.path.join(algorithms_path, f"{algorithm_name}.py")
            if not os.path.exists(filepath):
                report_string += f"{string_name(algorithm_name)} missing file\n"
                continue

            spec = importlib.util.spec_from_file_location(algorithm_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            solve_fn = getattr(module, "solve_nqueens", None)
            if not solve_fn:
                report_string += f"{string_name(algorithm_name)} missing solve_nqueens\n"
                continue

            start = time.time()
            try:
                solution = solve_fn(board)
                exec_time = time.time() - start

                if solution:
                    report_string += f"{string_name(algorithm_name)} found a solution in {exec_time:.6f}s\n"
                    results[algorithm_name] = (exec_time, solution)
                    times_vector[idx] = exec_time
                else:
                    report_string += f"{string_name(algorithm_name)} did not find a solution\n"
            except Exception as e:
                report_string += f"{string_name(algorithm_name)} ERROR: {e}\n"

        if not results:
            return None

        fastest_algorithm_key = min(results, key=lambda k: results[k][0])
        fastest_time, fastest_solution = results[fastest_algorithm_key]
        percentages = AlgorithmComparator.calculate_time_percentages(times_vector)

        return {
            "fastest_algorithm_key": fastest_algorithm_key,
            "fastest_algorithm": string_name(fastest_algorithm_key),
            "execution_time": fastest_time,
            "solution": fastest_solution,
            "report": report_string,
            "times_vector": times_vector,
            "time_percentages": percentages,
        }

    @staticmethod
    def calculate_time_percentages(times_vector):
        valid = [t for t in times_vector if t is not None]
        if not valid:
            return [None] * len(times_vector)

        fastest = min(valid)
        out = []
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


def string_name(algorithm_name):
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
