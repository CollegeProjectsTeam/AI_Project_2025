import os
import time
import importlib.util

class AlgorithmComparator:
    """Compares execution times of all algorithms in the Algorithms folder for a given N-Queens instance."""

    @staticmethod
    def compare_algorithms(instance):
        """
        Compares all algorithms in the Algorithms folder and returns the fastest one.

        Args:
            instance (dict): The N-Queens problem instance.

        Returns:
            dict: A dictionary containing the fastest algorithm, its execution time, and the solution.
                  If no algorithm provides a solution, returns None.
        """

        algorithms_folder = "core/search_strategies/n_queens_problem/Algorithms"
        algorithms_path = os.path.join(os.getcwd(), algorithms_folder)
        results = {}
        report_string = ""

        for file in os.listdir(algorithms_path):
            if file.endswith(".py") and file != "__init__.py":
                algorithm_name = file[:-3]  # Remove .py extension
                algorithm_module = f"core.search_strategies.n_queens_problem.Algorithms.{algorithm_name}"
                
                # Dynamically import the algorithm
                spec = importlib.util.spec_from_file_location(algorithm_name, os.path.join(algorithms_path, file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Measure execution time
                start_time = time.time()
                try:
                    #print(f"Running algorithm: {algorithm_name}")
                    solution = module.solve_nqueens(instance)
                    exec_time = time.time() - start_time
                    # Validate the solution
                    if solution:
                        # Append to report string for explication
                        message = f"{string_name(algorithm_name)} found a solution in {exec_time:.6f} seconds\n"
                        report_string += message

                        #print(f"[answear] Algorithm {string_name(algorithm_name)} found a solution in {exec_time:.6f} seconds.")
                        results[algorithm_name] = (exec_time, solution)
                    else:
                        # Append to report string for explication
                        message = f"{string_name(algorithm_name)} did not find a solution\n"
                        report_string += message

                        #print(f"Algorithm {string_name(algorithm_name)} did not return a valid solution.")
                except Exception as e:
                    print(f"Error running {string_name(algorithm_name)}: {e}")
    
        if not results:
            #print("No algorithms provided a valid solution.")
            return None, report_string
        
        # Determine the fastest algorithm
        fastest_algorithm = min(results, key=lambda k: results[k][0])
        fastest_time, fastest_solution = results[fastest_algorithm]

        return {
            "fastest_algorithm": string_name(fastest_algorithm),
            "execution_time": fastest_time,
            "solution": fastest_solution,
            "report": report_string
        }
    
def string_name (algorithm_name):
    """Converts algorithm internal names to user-friendly names."""
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