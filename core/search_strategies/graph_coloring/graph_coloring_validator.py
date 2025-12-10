class GraphColoringValidator:
    """Validates Graph Coloring instances and colorings."""

    @staticmethod
    def is_valid_instance(adjacency_matrix: list[list[int]]) -> bool:
        """
        Check if the adjacency matrix represents a valid simple, undirected graph.
        Conditions:
        - square matrix
        - 0 on diagonal
        - symmetric
        - only 0/1 values
        """
        n = len(adjacency_matrix)
        if n == 0:
            return False

        # Check all rows have length n
        for row in adjacency_matrix:
            if len(row) != n:
                return False

        # Check diagonal 0 and symmetry + values 0/1
        for i in range(n):
            if adjacency_matrix[i][i] != 0:
                return False
            for j in range(n):
                if adjacency_matrix[i][j] not in (0, 1):
                    return False
                if adjacency_matrix[i][j] != adjacency_matrix[j][i]:
                    return False

        return True

    @staticmethod
    def is_valid_coloring(
        adjacency_matrix: list[list[int]],
        colors: list[int],
        num_colors: int
    ) -> bool:
        """
        Check if a given coloring is valid:
        - colors length == num_vertices
        - each color in [0, num_colors-1]
        - no adjacent vertices share the same color
        """
        n = len(adjacency_matrix)
        if len(colors) != n:
            return False

        for c in colors:
            if not (0 <= c < num_colors):
                return False

        # Check edges
        for i in range(n):
            for j in range(i + 1, n):
                if adjacency_matrix[i][j] == 1 and colors[i] == colors[j]:
                    return False

        return True
