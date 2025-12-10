import os
import time
import importlib.util


class GraphColoringAlgorithmComparator:
    """
    Compares execution times of all algorithms in the Algorithms folder
    for a given Graph Coloring instance.
    """

    @staticmethod
    def compare_algorithms(instance: dict):
        """
        Compares all algorithms in the Algorithms folder and returns the fastest one.

        Args:
            instance (dict): The Graph Coloring problem instance:
                {
                  "problem_name": "Graph Coloring",
                  "num_vertices": ...,
                  "num_colors": ...,
                  "adjacency_matrix": [...]
                }

        Returns:
            dict: {
                "fastest_algorithm": <friendly name>,
                "execution_time": <float>,
                "solution": <algorithm output>,
                "report": <multi-line string>,
                "times_vector": [t1, t2, ...],
                "time_percentages": [p1, p2, ...]
            }
            or (None, report_string) if no algorithm returns a solution.
        """

        algorithms_folder = "core/search_strategies/graph_coloring_problem/Algorithms"
        algorithms_path = os.path.join(os.getcwd(), algorithms_folder)

        results = {}
        report_string = ""

        # You can adapt names / order to ce ai la Graph Coloring
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
        time_algorithms = [None] * len(algorithm_order)

        if not os.path.isdir(algorithms_path):
            raise RuntimeError(f"Algorithms folder not found: {algorithms_path}")

        for file in os.listdir(algorithms_path):
            if file.endswith(".py") and file != "__init__.py":
                algorithm_name = file[:-3]  # remove .py
                module_path = os.path.join(algorithms_path, file)

                spec = importlib.util.spec_from_file_location(algorithm_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, "solve_graph_coloring"):
                    # ignore modules care nu implementeaza solve_graph_coloring
                    continue

                start_time = time.time()
                try:
                    solution = module.solve_graph_coloring(instance)
                    exec_time = time.time() - start_time

                    if solution:
                        msg = f"{string_name_gc(algorithm_name)} found a coloring in {exec_time:.6f} seconds\n"
                        report_string += msg
                        results[algorithm_name] = (exec_time, solution)

                        if algorithm_name in algorithm_order:
                            idx = algorithm_order.index(algorithm_name)
                            time_algorithms[idx] = exec_time
                    else:
                        msg = f"{string_name_gc(algorithm_name)} did not find a valid coloring\n"
                        report_string += msg

                except Exception as e:
                    report_string += f"Error running {string_name_gc(algorithm_name)}: {e}\n"

        if not results:
            return None, report_string

        # Fastest algorithm
        fastest_algorithm = min(results, key=lambda k: results[k][0])
        fastest_time, fastest_solution = results[fastest_algorithm]

        percentages = GraphColoringAlgorithmComparator.calculate_time_percentages(time_algorithms)

        return {
            "fastest_algorithm": string_name_gc(fastest_algorithm),
            "execution_time": fastest_time,
            "solution": fastest_solution,
            "report": report_string,
            "times_vector": time_algorithms,
            "time_percentages": percentages
        }

    @staticmethod
    def calculate_time_percentages(time_algorithms: list[float | None]) -> list[float | None]:
        """
        Calculate (min_time / t_i) * 100 pentru fiecare algoritm (la fel ca la N-Queens).
        """
        valid_times = [t for t in time_algorithms if t is not None]

        if not valid_times:
            return [None] * len(time_algorithms)

        total_min = min(valid_times)

        percentages = []
        for t in time_algorithms:
            if t is None:
                percentages.append(None)
            else:
                percentages.append(round((total_min / t) * 100, 2))
        return percentages


def string_name_gc(algorithm_name: str) -> str:
    """Converts internal names to user-friendly names for Graph Coloring."""
    names = {
        'breadth_first_search': 'Breadth First Search',
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
