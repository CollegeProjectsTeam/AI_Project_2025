import os
import importlib.util
import random

from .graph_coloring_validator import GraphColoringValidator


class GraphColoringInstanceGenerator:
    """
    Generates a random Graph Coloring instance given number of vertices and colors,
    ensuring it is solvable by the Backtracking algorithm.
    """

    @staticmethod
    def load_backtracking_solver():
        """
        Dynamically loads the backtracking solver module for graph coloring.
        Expected path: core/search_strategies/graph_coloring_problem/Algorithms/backtracking.py
        Expected function: solve_graph_coloring(instance_dict) -> list[int] | None
        """
        algorithms_folder = "core/search_strategies/graph_coloring_problem/Algorithms"
        algorithm_file = "backtracking.py"
        algorithms_path = os.path.join(os.getcwd(), algorithms_folder, algorithm_file)

        spec = importlib.util.spec_from_file_location("graph_backtracking", algorithms_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.solve_graph_coloring

    @staticmethod
    def _generate_random_graph(num_vertices: int) -> list[list[int]]:
        """
        Generates a random undirected simple graph as adjacency matrix.
        Edge probability is chosen randomly in a reasonable interval.
        """
        p = random.uniform(0.3, 0.7)  # edge probability

        adj = [[0] * num_vertices for _ in range(num_vertices)]
        for i in range(num_vertices):
            for j in range(i + 1, num_vertices):
                if random.random() < p:
                    adj[i][j] = adj[j][i] = 1

        return adj

    @staticmethod
    def generate(num_vertices: int, num_colors: int) -> dict:
        """
        Generates a solvable Graph Coloring instance.

        Returns:
            dict with keys:
                - problem_name: "Graph Coloring"
                - num_vertices
                - num_colors
                - adjacency_matrix
        """
        if num_vertices < 2:
            raise ValueError("num_vertices must be >= 2")
        if num_colors < 1:
            raise ValueError("num_colors must be >= 1")

        validator = GraphColoringInstanceGenerator._get_validator()
        solve_backtracking = GraphColoringInstanceGenerator.load_backtracking_solver()

        attempts = 0
        while True:
            attempts += 1
            adjacency_matrix = GraphColoringInstanceGenerator._generate_random_graph(num_vertices)

            if not validator.is_valid_instance(adjacency_matrix):
                continue

            # Build instance dict
            instance = {
                "problem_name": "Graph Coloring",
                "num_vertices": num_vertices,
                "num_colors": num_colors,
                "adjacency_matrix": adjacency_matrix
            }

            # Ensure solvable
            solution = solve_backtracking(instance)
            if solution is not None and validator.is_valid_coloring(adjacency_matrix, solution, num_colors):
                # OK, we have a solvable instance
                break

            if attempts > 100:
                raise RuntimeError("Failed to generate a solvable Graph Coloring instance after 100 tries")

        return instance

    @staticmethod
    def _get_validator():
        return GraphColoringValidator()
