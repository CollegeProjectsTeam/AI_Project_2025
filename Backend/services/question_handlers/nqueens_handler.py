from __future__ import annotations

from typing import Any, Dict

from Backend.config.runtime_store import store
from Backend.core.question_generator import QuestionGenerator
from Backend.core.search_strategies.n_queens_problem.n_queens_instance_generator import NQueensInstanceGenerator
from Backend.core.search_strategies.n_queens_problem.n_queens_answear import AlgorithmComparator, string_name
from Backend.services import Logger
from Backend.services.question_handlers.utils import clamp_int

log = Logger("QH.NQueens")


class NQueensQuestionHandler:
    def __init__(self, qgen: QuestionGenerator):
        self.qgen = qgen

    @staticmethod
    def can_handle(ch_num: int, sub_num: int) -> bool:
        return (ch_num, sub_num) == (1, 1)

    def generate(self, ch_num: int, sub_num: int, template_text: str, options: Dict[str, Any]) -> Dict[str, Any]:
        n = clamp_int(options.get("n"), 4, 12, 4)

        instance = NQueensInstanceGenerator.generate(n)
        question_text = self.qgen.render_question(template_text, instance)

        comp = AlgorithmComparator.compare_algorithms(instance["board"])
        if comp is None:
            log.warn("No valid solution found by any algorithm", {"n": n})
            return {"ok": False, "error": "no valid solution found by any algorithm"}

        algo_keys = getattr(AlgorithmComparator, "ALGORITHM_ORDER", [])
        algo_labels = [string_name(k) for k in algo_keys]
        correct = comp["fastest_algorithm_key"]

        meta = {
            "type": "nqueens",
            "n": n,
            "answer_option_keys": algo_keys,
            "answer_options": algo_labels,
            "choices": comp.get("times_vector"),
            "percentages": comp.get("time_percentages"),
            "nqueens_comparison": {
                "fastest_algorithm_key": comp.get("fastest_algorithm_key"),
                "fastest_algorithm": comp.get("fastest_algorithm"),
                "fastest_time_s": round(float(comp.get("execution_time") or 0.0), 6),
                "sorted_by": "time_desc",
                "timings": comp.get("timings") or [],
            },
        }

        log.info("NQueens question generated", ctx={"n": n, "correct": correct})

        qa = store.put(ch_num, sub_num, question_text, correct, meta)
        return {
            "ok": True,
            "question": {
                "question_id": qa.id,
                "chapter_number": ch_num,
                "subchapter_number": sub_num,
                "question_text": qa.question_text,
                "meta": {
                    "type": "nqueens",
                    "n": n,
                    "answer_option_keys": algo_keys,
                    "answer_options": algo_labels,
                },
            },
        }
