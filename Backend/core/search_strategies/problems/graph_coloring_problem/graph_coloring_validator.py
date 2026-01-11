from __future__ import annotations

from Backend.services import Logger

log = Logger("GraphColoringValidator")


class GraphColoringValidator:
    @staticmethod
    def is_valid(adj_list: list[list[int]], num_nodes: int, num_colors: int) -> bool:
        if not isinstance(adj_list, list) or len(adj_list) != num_nodes:
            return False
        if not isinstance(num_colors, int) or num_colors < 2 or num_colors > num_nodes:
            return False

        for u, neigh in enumerate(adj_list):
            if not isinstance(neigh, list):
                return False
            seen = set()
            for v in neigh:
                if not isinstance(v, int):
                    return False
                if v < 0 or v >= num_nodes:
                    return False
                if v == u:
                    return False
                if v in seen:
                    return False
                seen.add(v)

        # undirected symmetry check
        for u, neigh in enumerate(adj_list):
            for v in neigh:
                if u not in adj_list[v]:
                    return False

        log.ok("Graph instance valid", ctx={"num_nodes": num_nodes, "num_colors": num_colors})
        return True