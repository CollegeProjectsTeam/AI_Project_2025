from __future__ import annotations

from typing import Any, Dict, Tuple

from Backend.config.runtime_store import store
from Backend.core.question_generator import QuestionGenerator
from Backend.services import Logger
from Backend.services.question_handlers.utils import clamp_int

from Backend.core.search_strategies.problems.n_queens_problem.n_queens_instance_generator import NQueensInstanceGenerator
from Backend.core.search_strategies.problems.graph_coloring_problem.graph_coloring_instance_generator import GraphColoringInstanceGenerator
from Backend.core.search_strategies.problems.knights_tour_problem.knights_tour_instance_generator import KnightsTourInstanceGenerator
from Backend.core.search_strategies.problems.generalized_hanoi_problem.generalized_hanoi_instance_generator import GeneralizedHanoiInstanceGenerator

from Backend.core.search_strategies.algorithm_comparator import AlgorithmComparator, string_name

log = Logger("QH.SearchStrategies")


_RULES: Dict[str, Dict[str, Dict[str, int]]] = {
    "easy": {
        "nqueens": {"min": 2, "max": 5, "def": 4},
        "graph_coloring": {"min": 4, "max": 9, "def": 6},
        "knights_tour": {"min": 5, "max": 7, "def": 5},
        "generalized_hanoi": {"min": 3, "max": 6, "def": 4},
    },
    "medium": {
        "nqueens": {"min": 4, "max": 8, "def": 6},
        "graph_coloring": {"min": 6, "max": 14, "def": 9},
        "knights_tour": {"min": 5, "max": 9, "def": 6},
        "generalized_hanoi": {"min": 3, "max": 10, "def": 5},
    },
    "hard": {
        "nqueens": {"min": 6, "max": 10, "def": 8},
        "graph_coloring": {"min": 10, "max": 18, "def": 12},
        "knights_tour": {"min": 7, "max": 10, "def": 8},
        "generalized_hanoi": {"min": 6, "max": 14, "def": 8},
    },
}
def _norm_problem(options: Dict[str, Any]) -> str:
    return str((options or {}).get("problem") or "nqueens").strip().lower()


def _norm_diff(options: Dict[str, Any]) -> str:
    d = str((options or {}).get("difficulty") or "medium").strip().lower()
    return d if d in ("easy", "medium", "hard") else "medium"


def _size_bounds(diff: str, problem: str) -> Tuple[int, int, int]:
    d = _RULES.get(diff) or _RULES["medium"]
    r = d.get(problem) or d["nqueens"]
    return int(r["min"]), int(r["max"]), int(r["def"])


def _pick_size(options: Dict[str, Any], lo: int, hi: int, default: int, keys: Tuple[str, ...]) -> int:
    raw = (options or {}).get("size")
    if raw is None:
        for k in keys:
            if k in (options or {}):
                raw = (options or {}).get(k)
                break
    return clamp_int(raw, lo, hi, default)


def _options_text(labels: list[str]) -> str:
    return ", ".join([str(x) for x in labels if str(x).strip()])


class SearchStrategiesQuestionHandler:
    def __init__(self, qgen: QuestionGenerator):
        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        return (ch_num, sub_num) == (1, 1)

    def generate(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        problem = _norm_problem(options)
        diff = _norm_diff(options)

        lo, hi, default = _size_bounds(diff, problem)

        if problem == "nqueens":
            size = _pick_size(options, lo, hi, default, ("n",))
            instance = NQueensInstanceGenerator.generate(size)
            display_name = "N-Queens"

        elif problem == "graph_coloring":
            size = _pick_size(options, lo, hi, default, ("nodes",))
            num_colors = {"easy": 3, "medium": 4, "hard": 5}.get(diff, 4)
            num_colors = max(2, min(num_colors, size))
            instance = GraphColoringInstanceGenerator.generate(size, num_colors=num_colors)
            display_name = "Graph Coloring"

        elif problem == "knights_tour":
            size = _pick_size(options, lo, hi, default, ("n",))
            instance = KnightsTourInstanceGenerator.generate(size)
            display_name = "Knights Tour"

        elif problem == "generalized_hanoi":
            size = _pick_size(options, lo, hi, default, ("disks",))
            pegs = {"easy": 3, "medium": 4, "hard": 5}.get(diff, 4)
            instance = GeneralizedHanoiInstanceGenerator.generate(size, pegs=pegs)
            display_name = "Generalized Hanoi"

        else:
            return {"ok": False, "error": f"unknown search strategies problem '{problem}'"}

        comp = AlgorithmComparator.compare(problem, instance)
        if comp is None:
            return {"ok": False, "error": "no valid solution found by any algorithm"}

        algo_keys = list(getattr(AlgorithmComparator, "ALGORITHM_ORDER", []))
        algo_labels = [string_name(k) for k in algo_keys]

        correct = comp.get("fastest_algorithm_key")
        if not correct:
            return {"ok": False, "error": "internal error: comparator missing fastest_algorithm_key"}

        render_ctx = {
            "problem_name": display_name,
            "instance": instance,
            "options": _options_text(algo_labels),
        }
        question_text = self.qgen.render_question(template_text, render_ctx)

        meta_store = {
            "type": problem,
            "group": "search_strategies",
            "problem": problem,
            "difficulty": diff,
            "size": size,

            "answer_option_keys": algo_keys,
            "answer_options": algo_labels,

            # comparator info (raw)
            "timings": comp.get("timings") or [],
            "fastest_algorithm_key": correct,
            "fastest_algorithm": comp.get("fastest_algorithm"),
            "execution_time": round(float(comp.get("execution_time") or 0.0), 6),
        }

        qa = store.put(ch_num, sub_num, question_text, str(correct), meta_store)

        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {
                    "type": problem,
                    "group": "search_strategies",
                    "problem": problem,
                    "difficulty": diff,
                    "size": size,
                    "answer_option_keys": algo_keys,
                    "answer_options": algo_labels,
                },
            },
        }