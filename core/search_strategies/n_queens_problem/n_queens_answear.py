# core/search_strategies/n_queens_problem/n_queens_answear.py
import os
import time
import importlib.util


class AlgorithmComparator:
    """Compares execution times of all algorithms in the Algorithms folder for a given N-Queens board."""

    @staticmethod
    def _get_algorithms_path():
        """
        Returnează calea reală către folderul:
            core/search_strategies/Algorithms
        indiferent de locul din care rulezi scriptul.
        """
        # acest fișier = core/search_strategies/n_queens_problem
        current_dir = os.path.dirname(__file__)

        # urcăm la: core/search_strategies
        search_strategies_root = os.path.dirname(current_dir)

        # folderul unde sunt toate algoritmurile
        algorithms_dir = os.path.join(search_strategies_root, "Algorithms")

        if not os.path.exists(algorithms_dir):
            raise FileNotFoundError(f"[NQueens Comparator] Algorithms folder not found: {algorithms_dir}")

        return algorithms_dir

    @staticmethod
    def compare_algorithms(board):
        """
        rulează toate algoritmurile din folderul Algorithms/ și returnează:
            - fastest_algorithm
            - execution_time
            - solution
            - report
            - times_vector
            - time_percentages
        """
        algorithms_path = AlgorithmComparator._get_algorithms_path()
        results = {}
        report_string = ""

        # ordine fixă pentru UI
        algorithm_order = [
            'breadth_first_search',
            'depth_first_search',
            'uniform_cost_search',
            'iterative_deepening_depth_first_search',
            'backtracking',
            'bidirectional_search',
            'greedy_best_first_search',
            'hill_climbing',
            'simulated_annealing',
            'beam_search',
            'a_star'
        ]

        times_vector = [None] * len(algorithm_order)

        for file in os.listdir(algorithms_path):
            if not file.endswith(".py") or file == "__init__.py":
                continue

            algorithm_name = file[:-3]
            filepath = os.path.join(algorithms_path, file)

            # import dynamic
            spec = importlib.util.spec_from_file_location(algorithm_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            solve_fn = getattr(module, "solve_nqueens", None)
            if not solve_fn:
                continue

            # măsurăm timpul
            start = time.time()
            try:
                solution = solve_fn(board)
                exec_time = time.time() - start

                if solution:
                    # append la raport
                    report_string += f"{string_name(algorithm_name)} found a solution in {exec_time:.6f}s\n"
                    results[algorithm_name] = (exec_time, solution)

                    if algorithm_name in algorithm_order:
                        idx = algorithm_order.index(algorithm_name)
                        times_vector[idx] = exec_time
                else:
                    report_string += f"{string_name(algorithm_name)} did not find a solution\n"

            except Exception as e:
                report_string += f"{string_name(algorithm_name)} ERROR: {e}\n"

        if not results:
            return None

        # cel mai rapid
        fastest_algorithm = min(results, key=lambda k: results[k][0])
        fastest_time, fastest_solution = results[fastest_algorithm]

        percentages = AlgorithmComparator.calculate_time_percentages(times_vector)

        return {
            "fastest_algorithm": string_name(fastest_algorithm),
            "execution_time": fastest_time,
            "solution": fastest_solution,
            "report": report_string,
            "times_vector": times_vector,
            "time_percentages": percentages
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


def string_name(algorithm_name):
    """Converts algorithm internal names to readable names."""
    names = {
        'breadth_first_search': 'Best First Search',
        'depth_first_search': 'Depth First Search',
        'uniform_cost_search': 'Uniform Cost Search',
        'iterative_deepening_depth_first_search': 'Iterative Deepening DFS',
        'backtracking': 'Backtracking',
        'bidirectional_search': 'Bidirectional Search',
        'greedy_best_first_search': 'Greedy Best First',
        'hill_climbing': 'Hill Climbing',
        'simulated_annealing': 'Simulated Annealing',
        'beam_search': 'Beam Search',
        'a_star': 'A*'
    }
    return names.get(algorithm_name, algorithm_name)