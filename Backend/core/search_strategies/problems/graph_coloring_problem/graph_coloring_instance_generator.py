from __future__ import annotations

import random
from typing import Any

from Backend.services import Logger
from .graph_coloring_validator import GraphColoringValidator

log = Logger("GraphColoringInstanceGenerator")


class GraphColoringInstanceGenerator:
    @staticmethod
    def generate(num_nodes: int, num_colors: int | None = None) -> dict[str, Any]:
        if num_colors is None:
            num_colors = min(4, max(3, num_nodes))

        num_colors = max(2, min(int(num_colors), int(num_nodes)))

        # Build guaranteed k-colorable graph by constructing a k-partition and only adding inter-part edges.
        partitions: list[list[int]] = [[] for _ in range(num_colors)]
        nodes = list(range(num_nodes))
        random.shuffle(nodes)

        for i, node in enumerate(nodes):
            partitions[i % num_colors].append(node)

        # Edge probability: moderate density, scales down for large n
        p = min(0.35, 3.0 / max(1, num_nodes))

        adj_list: list[list[int]] = [[] for _ in range(num_nodes)]

        def add_edge(u: int, v: int):
            if v not in adj_list[u]:
                adj_list[u].append(v)
            if u not in adj_list[v]:
                adj_list[v].append(u)

        # Add edges only between different partitions
        part_of = {}
        for c, part in enumerate(partitions):
            for node in part:
                part_of[node] = c

        for u in range(num_nodes):
            for v in range(u + 1, num_nodes):
                if part_of[u] == part_of[v]:
                    continue
                if random.random() < p:
                    add_edge(u, v)

        # Ensure at least a few edges (avoid trivial empty graph)
        attempts = 0
        while attempts < 10 and sum(len(x) for x in adj_list) == 0 and num_nodes >= 2:
            attempts += 1
            u = random.randrange(0, num_nodes)
            v = random.randrange(0, num_nodes)
            if u != v and part_of[u] != part_of[v]:
                add_edge(u, v)

        for row in adj_list:
            row.sort()

        validator = GraphColoringValidator()
        if not validator.is_valid(adj_list, num_nodes, num_colors):
            log.error("Generated invalid graph instance", ctx={"num_nodes": num_nodes, "num_colors": num_colors})
            raise RuntimeError("GraphColoringInstanceGenerator produced invalid instance")

        log.ok("Generated Graph Coloring instance", ctx={"num_nodes": num_nodes, "num_colors": num_colors, "edge_count": sum(len(x) for x in adj_list) // 2})

        return {
            "problem_name": "Graph Coloring",
            "num_nodes": num_nodes,
            "num_colors": num_colors,
            "adj_list": adj_list,
        }